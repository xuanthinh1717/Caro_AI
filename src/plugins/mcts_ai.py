import math
import random
import time

from ai.base import AIPlayer
from game.constants import BOARD_SIZE, EMPTY, PLAYER_X, PLAYER_O
from game.move import Move
from game.pattern import PatternAnalyzer


class MCTSNode:

    def __init__(
        self,
        state,
        parent=None,
        move=None,
        untried_moves=None
    ):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0.0
        self.untried_moves = list(untried_moves or [])

    def is_fully_expanded(self):
        return not self.untried_moves

    def best_child(self, exploration):
        log_parent = math.log(max(1, self.visits))

        def uct(child):
            if child.visits == 0:
                return math.inf

            exploitation = child.score / child.visits
            exploration_bonus = exploration * math.sqrt(
                log_parent / child.visits
            )

            return exploitation + exploration_bonus

        return max(
            self.children,
            key=uct
        )


class MCTSAI(AIPlayer):

    def __init__(self):
        self.time_limit = 0.8
        self.max_iterations = 200
        self.max_candidates = 10
        self.rollout_depth = 12
        self.exploration = 1.4
        self.iterations_done = 0

    @property
    def name(self):
        return "MCTS AI"

    def choose_move(self, state):
        start_time = time.perf_counter()
        self.iterations_done = 0

        ai_player = state.current_player
        opponent = self.get_opponent(ai_player)

        if state.piece_count() == 0:
            center = BOARD_SIZE // 2
            return Move(center, center)

        valid_moves = state.get_valid_moves()

        if not valid_moves:
            return None

        winning_moves = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            ai_player
        )

        if winning_moves:
            return winning_moves[0]

        opponent_winning_moves = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            opponent
        )

        if opponent_winning_moves:
            return opponent_winning_moves[0]

        root = MCTSNode(
            state=state,
            untried_moves=self.get_candidate_moves(state)
        )

        while (
            self.iterations_done < self.max_iterations
            and time.perf_counter() - start_time < self.time_limit
        ):
            node = self.select(root)

            if (
                not node.state.is_terminal()
                and not node.is_fully_expanded()
            ):
                node = self.expand(node)

            result = self.rollout(
                node.state.clone(),
                ai_player
            )

            self.backpropagate(
                node,
                result
            )

            self.iterations_done += 1

        best = self.best_root_child(root)

        move = (
            best.move
            if best is not None
            else random.choice(valid_moves)
        )

        elapsed = time.perf_counter() - start_time

        print(
            f"[{self.name}] "
            f"Move: ({move.row}, {move.col}) | "
            f"Iterations: {self.iterations_done} | "
            f"Time: {elapsed:.4f}s"
        )

        return move

    def select(self, node):
        while (
            not node.state.is_terminal()
            and node.is_fully_expanded()
            and node.children
        ):
            node = node.best_child(
                self.exploration
            )

        return node

    def expand(self, node):
        move = node.untried_moves.pop()
        child_state = node.state.simulate_move(move)

        child = MCTSNode(
            state=child_state,
            parent=node,
            move=move,
            untried_moves=self.get_candidate_moves(child_state)
        )

        node.children.append(child)

        return child

    def rollout(self, state, ai_player):
        depth = 0

        while (
            not state.is_terminal()
            and depth < self.rollout_depth
        ):
            move = self.rollout_move(state)

            if move is None:
                break

            state = state.simulate_move(move)
            depth += 1

        return self.score_result(
            state,
            ai_player
        )

    def rollout_move(self, state):
        valid_moves = state.get_valid_moves()

        if not valid_moves:
            return None

        candidates = state.get_candidate_moves(
            distance=1
        )

        if candidates:
            return random.choice(candidates)

        return random.choice(valid_moves)

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            node.score += result
            node = node.parent

    def score_result(self, state, ai_player):
        if state.winner == ai_player:
            return 1.0

        if state.winner == self.get_opponent(ai_player):
            return -1.0

        return self.heuristic_result(
            state,
            ai_player
        )

    def heuristic_result(self, state, ai_player):
        opponent = self.get_opponent(ai_player)

        ai_score = self.evaluate_player(
            state,
            ai_player
        )

        opponent_score = self.evaluate_player(
            state,
            opponent
        )

        if ai_score == opponent_score:
            return 0.0

        return (
            0.25
            if ai_score > opponent_score
            else -0.25
        )

    def evaluate_player(self, state, player):
        score = 0
        board = state.board

        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                for dr, dc in directions:
                    cells = []

                    for i in range(5):
                        r = row + dr * i
                        c = col + dc * i

                        if not (
                            0 <= r < BOARD_SIZE
                            and 0 <= c < BOARD_SIZE
                        ):
                            break

                        cells.append(
                            board.get_cell(r, c)
                        )

                    if len(cells) == 5:
                        score += self.score_window(
                            cells,
                            player
                        )

        return score

    def score_window(self, cells, player):
        opponent = self.get_opponent(player)

        player_count = cells.count(player)
        opponent_count = cells.count(opponent)
        empty_count = cells.count(EMPTY)

        if player_count > 0 and opponent_count > 0:
            return 0

        if player_count == 5:
            return 1_000_000

        if player_count == 4 and empty_count == 1:
            return 100_000

        if player_count == 3 and empty_count == 2:
            return 10_000

        if player_count == 2 and empty_count == 3:
            return 1_000

        if player_count == 1 and empty_count == 4:
            return 10

        return 0

    def best_root_child(self, root):
        if not root.children:
            return None

        return max(
            root.children,
            key=lambda child: (
                child.visits,
                child.score / child.visits
                if child.visits
                else -math.inf
            )
        )

    def get_candidate_moves(
        self,
        state,
        top_n=None
    ):
        limit = (
            top_n
            if top_n is not None
            else self.max_candidates
        )

        moves = state.get_candidate_moves(
            distance=2
        )

        if not moves:
            moves = state.get_valid_moves()

        random.shuffle(moves)

        return moves[:limit]

    def get_opponent(self, player):
        if player == PLAYER_X:
            return PLAYER_O

        return PLAYER_X

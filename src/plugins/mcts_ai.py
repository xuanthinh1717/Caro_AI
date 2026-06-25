import math
import random
import time
from ai.base import AIPlayer
from game.move import Move
from game.pattern import PatternAnalyzer
from game.board_analyzer import BoardAnalyzer
from game.constants import PLAYER_X, PLAYER_O

class MCTSNode:
    def __init__(self, state, parent=None, move=None, is_root=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        
        self.visits = 0
        self.wins = 0
        self.rave_visits = 0
        self.rave_wins = 0
        
        self.untried_moves = self._get_smart_moves(state, is_root)

    def _get_smart_moves(self, state, is_root):
        """Tối ưu tốc độ mở rộng nhánh (Expansion Culling)"""
        if is_root:
            candidates = BoardAnalyzer.get_candidate_analysis(state.board, distance=2, top_n=12)
            if candidates:
                return [(cand.move, cand.priority_score) for cand in candidates]
        else:
            cands = state.get_candidate_moves(distance=1)
            if cands:
                random.shuffle(cands)
                return [(m, 0) for m in cands[:8]]
        
        valid_moves = state.get_valid_moves()
        return [(m, 0) for m in valid_moves]

    def uct_select_child(self, c_param=1.414, rave_equiv=300):
        best_score = float('-inf')
        best_child = None
        for child in self.children:
            if child.visits == 0:
                return child
                
            mcts_exploit = child.wins / child.visits
            explore = math.sqrt(math.log(self.visits) / child.visits)
            rave_exploit = child.rave_wins / child.rave_visits if child.rave_visits > 0 else 0
            
            beta = math.sqrt(rave_equiv / (3 * child.visits + rave_equiv))
            score = (1 - beta) * mcts_exploit + beta * rave_exploit + c_param * explore
            
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        move, _ = self.untried_moves.pop(0)
        next_state = self.state.simulate_move(move)
        child_node = MCTSNode(next_state, parent=self, move=move, is_root=False)
        self.children.append(child_node)
        return child_node

class MctsAI(AIPlayer):
    def __init__(self, time_limit=3.0):
        super().__init__()
        self.time_limit = time_limit
        self.nodes_simulated = 0
        self.tt = {} 

    @property
    def name(self) -> str:
        return "MCTS-RAVE Ultimate"

    def _get_state_hash(self, state):
        """Băm trạng thái nhanh thành chuỗi để lưu Cache (O(1) lookup)"""
        return str(state.board.grid)

    def choose_move(self, state) -> Move:
        self.nodes_simulated = 0
        self.tt.clear() 
        current_player = state.current_player
        valid_moves = state.get_valid_moves()

        if not valid_moves:
            raise Exception("Không còn nước đi hợp lệ")

        if len(valid_moves) == 15 * 15:
            return Move(7, 7) 

        winning_moves = PatternAnalyzer.find_winning_moves(state.board, valid_moves, current_player)
        if winning_moves:
            return winning_moves[0]
        
        opponent = state.get_opponent()
        opponent_wins = PatternAnalyzer.find_winning_moves(state.board, valid_moves, opponent)
        if opponent_wins:
            return opponent_wins[0]

        root_node = MCTSNode(state, is_root=True)
        start_time = time.time()

        while time.time() - start_time < self.time_limit:
            node = root_node
            sim_state = state.clone()
            played_moves = { 1: set(), 2: set() }

            while not node.untried_moves and node.children:
                node = node.uct_select_child()
                sim_state = sim_state.simulate_move(node.move)
                played_moves[sim_state.get_opponent()].add(node.move)

            if node.untried_moves:
                node = node.expand()
                sim_state = sim_state.simulate_move(node.move)
                played_moves[sim_state.get_opponent()].add(node.move)

            state_hash = self._get_state_hash(sim_state)
            if state_hash in self.tt:
                result = self.tt[state_hash]
                simulated_moves = {1: set(), 2: set()} 
            else:
                result, simulated_moves = self.light_playout(sim_state)
                self.tt[state_hash] = result
                self.nodes_simulated += 1

            for p in [1, 2]:
                played_moves[p].update(simulated_moves[p])

            while node is not None:
                node.visits += 1
                if result == current_player: 
                    node.wins += 1
                elif result == 0: # Hòa
                    node.wins += 0.5
                    
                if node.parent:
                    for sibling in node.parent.children:
                        if sibling.move in played_moves[current_player]:
                            sibling.rave_visits += 1
                            if result == current_player:
                                sibling.rave_wins += 1
                            elif result == 0:
                                sibling.rave_wins += 0.5
                node = node.parent

        if not root_node.children:
            return valid_moves[0]

        best_child = max(root_node.children, key=lambda c: c.visits)
        print(f"[{self.name}] Đã duyệt {self.nodes_simulated} nodes. (Tăng tốc = {round((self.nodes_simulated/self.time_limit),0)} node/s)")
        
        return best_child.move

    def light_playout(self, state):
        """Mô phỏng siêu tốc: Bỏ hết Heuristic nặng, chỉ check block/win trực tiếp rồi random cục bộ"""
        current_state = state.clone()
        depth = 0
        simulated_moves = { 1: set(), 2: set() }
        
        while not current_state.game_over and depth < 25:
            player = current_state.current_player
            valid_moves = current_state.get_valid_moves()
            if not valid_moves:
                break
                
            win_moves = PatternAnalyzer.find_winning_moves(current_state.board, valid_moves, player)
            if win_moves:
                best_move = win_moves[0]
            else:
                opp = current_state.get_opponent()
                opp_wins = PatternAnalyzer.find_winning_moves(current_state.board, valid_moves, opp)
                if opp_wins:
                    best_move = opp_wins[0]
                else:
                    candidates = current_state.get_candidate_moves(distance=1)
                    if candidates:
                        best_move = random.choice(candidates)
                    else:
                        best_move = random.choice(valid_moves)
            
            current_state = current_state.simulate_move(best_move)
            simulated_moves[player].add(best_move)
            depth += 1
            
        return current_state.winner or 0, simulated_moves
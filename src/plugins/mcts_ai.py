import math
import random
import time
import copy
from plugins.opening_book import OpeningBook
from ai.vcf_solver import VCFSolver

class MCTSNode:
    def __init__(self, state, parent=None, move=None, heuristic_score=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        
        self.visits = 0
        self.wins = 0
        
        self.rave_visits = 0
        self.rave_wins = 0
        
        self.heuristic_score = heuristic_score 
        self.untried_moves = self._get_smart_moves(state)

    def _get_smart_moves(self, state):
        """Ưu tiên mở rộng các nước đi có tiềm năng theo Heuristic"""
        if hasattr(state, 'get_candidate_moves'):
            moves = state.get_candidate_moves()
            return [m for m, score in moves]
        return state.get_empty_cells()

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
        move = self.untried_moves.pop(0)
        next_state = copy.deepcopy(self.state)
        next_state.make_move(move)
        
        h_score = next_state.evaluate_heuristic() if hasattr(next_state, 'evaluate_heuristic') else 0
        child_node = MCTSNode(next_state, parent=self, move=move, heuristic_score=h_score)
        self.children.append(child_node)
        return child_node

class MctsAI:
    def __init__(self, time_limit=5.0):
        self.time_limit = time_limit
        self.name = "MCTS-RAVE Ultimate"
        self.book = OpeningBook()
        self.vcf = VCFSolver()
        self.nodes_simulated = 0

    def get_move(self, board_state):
        self.nodes_simulated = 0
        
        if hasattr(board_state, 'zobrist_hash'):
            book_move = self.book.get_move(board_state.zobrist_hash)
            if book_move:
                print(f"[{self.name}] Tìm thấy thế khai cuộc trong sách!")
                return book_move

        vcf_move = self.vcf.find_winning_path(board_state, board_state.current_player)
        if vcf_move:
            print(f"[{self.name}] Phát hiện đường thắng bắt buộc (VCF)!")
            return vcf_move

        root_node = MCTSNode(board_state)
        start_time = time.time()

        while time.time() - start_time < self.time_limit:
            node = root_node
            state = copy.deepcopy(board_state)
            
            played_moves = { 'X': set(), 'O': set() }

            while not node.untried_moves and node.children:
                node = node.uct_select_child()
                state.make_move(node.move)
                played_moves[state.current_player].add(node.move)

            if node.untried_moves:
                node = node.expand()
                state.make_move(node.move)
                played_moves[state.current_player].add(node.move)

            result, simulated_moves = self.heavy_playout(state)
            for p in ['X', 'O']:
                played_moves[p].update(simulated_moves[p])
            self.nodes_simulated += 1

            while node is not None:
                node.visits += 1
                if result == board_state.current_player: 
                    node.wins += 1
                elif result == 'DRAW':
                    node.wins += 0.5
                    
                if node.parent:
                    for sibling in node.parent.children:
                        if sibling.move in played_moves[board_state.current_player]:
                            sibling.rave_visits += 1
                            if result == board_state.current_player:
                                sibling.rave_wins += 1
                            elif result == 'DRAW':
                                sibling.rave_wins += 0.5
                node = node.parent

        if not root_node.children:
            return None

        best_child = max(root_node.children, key=lambda c: c.visits)
        print(f"[{self.name}] Đã duyệt {self.nodes_simulated} nodes. Win-rate gốc: {best_child.wins/best_child.visits:.2f}")
        return best_child.move

    def heavy_playout(self, state):
        current_state = state 
        depth = 0
        simulated_moves = { 'X': set(), 'O': set() }
        
        while not current_state.is_game_over() and depth < 50:
            best_move = None
            player = current_state.current_player
            
            if hasattr(current_state, 'get_winning_move'):
                best_move = current_state.get_winning_move(player)
                if not best_move:
                    best_move = current_state.get_winning_move(1 - player)

            if not best_move:
                moves = current_state.get_candidate_moves() if hasattr(current_state, 'get_candidate_moves') else current_state.get_empty_cells()
                if not moves: break
                best_move = random.choice(moves[:10]) 
            
            current_state.make_move(best_move)
            simulated_moves[player].add(best_move)
            depth += 1
            
        return current_state.get_winner(), simulated_moves
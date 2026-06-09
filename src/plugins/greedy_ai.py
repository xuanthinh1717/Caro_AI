"""Example AI from development guide - Greedy AI"""
from ai.base import AIPlayer
from game.move import Move
from game.pattern import PatternAnalyzer, PatternType
from game.board_analyzer import BoardAnalyzer
from game.constants import PLAYER_X, PLAYER_O


class GreedyAI(AIPlayer):
    """
    Simple Greedy AI strategy:
    1. Win if possible
    2. Block opponent if needed
    3. Play best candidate
    """
    
    @property
    def name(self):
        return "Greedy AI"
    
    def choose_move(self, state):
        """Main AI logic"""
        valid_moves = state.get_valid_moves()
        current_player = state.current_player
        opponent = state.get_opponent()
        
        # 1. Check if we can win
        winning = PatternAnalyzer.find_winning_moves(
            state.board,
            valid_moves,
            current_player
        )
        if winning:
            return winning[0]
        
        # 2. Check if opponent can win next move - block it!
        threats = PatternAnalyzer.find_threats(
            state.board,
            valid_moves,
            opponent
        )
        
        # Priority order: block OPEN_4 > DEAD_4 > LIVE_3
        if PatternType.OPEN_4 in threats:
            return threats[PatternType.OPEN_4][0]
        elif PatternType.DEAD_4 in threats:
            return threats[PatternType.DEAD_4][0]
        elif PatternType.LIVE_3 in threats:
            return threats[PatternType.LIVE_3][0]
        
        # 3. Play best candidate (highest priority)
        candidates = BoardAnalyzer.get_candidate_analysis(
            state.board,
            distance=2,
            top_n=1
        )
        
        if candidates:
            return candidates[0].move
        else:
            # Fallback: random valid move
            return valid_moves[0] if valid_moves else None

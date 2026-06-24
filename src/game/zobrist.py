import random
from game.constants import PLAYER_X, PLAYER_O

class ZobristHashing:
    def __init__(self, rows=15, cols=15):
        self.rows = rows
        self.cols = cols
        self.table = [[[random.getrandbits(64) for _ in range(2)] for _ in range(cols)] for _ in range(rows)]
        self.turn_hash = random.getrandbits(64)

    def _get_piece_index(self, piece):
        """Map hằng số của nhóm sang index của mảng (0 hoặc 1)"""
        return 0 if piece == PLAYER_X else 1

    def compute_initial_hash(self, board, current_player):
        """Tính mã hash cho một bàn cờ tĩnh"""
        h = 0
        for r in range(self.rows):
            for c in range(self.cols):
                piece = board.get_cell(r, c)
                if piece in (PLAYER_X, PLAYER_O):
                    h ^= self.table[r][c][self._get_piece_index(piece)]
        
        if current_player == PLAYER_O:
            h ^= self.turn_hash
        return h

    def update_hash(self, current_hash, row, col, piece):
        """Cập nhật hash O(1) khi có nước đi mới hoặc undo"""
        if piece not in (PLAYER_X, PLAYER_O):
            return current_hash
            
        piece_idx = self._get_piece_index(piece)
        new_hash = current_hash ^ self.table[row][col][piece_idx]
        new_hash ^= self.turn_hash 
        return new_hash

ZOBRIST = ZobristHashing()
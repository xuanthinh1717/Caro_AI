import random

class ZobristHashing:
    def __init__(self, rows=15, cols=15):
        self.rows = rows
        self.cols = cols
        self.table = [[[random.getrandbits(64) for _ in range(2)] for _ in range(cols)] for _ in range(rows)]
        self.turn_hash = random.getrandbits(64)

    def compute_initial_hash(self, board, current_player_is_x):
        """Tính mã hash cho một bàn cờ tĩnh"""
        h = 0
        for r in range(self.rows):
            for c in range(self.cols):
                piece = board[r][c]
                if piece == 'X':
                    h ^= self.table[r][c][0]
                elif piece == 'O':
                    h ^= self.table[r][c][1]
        
        if not current_player_is_x:
            h ^= self.turn_hash
        return h

    def update_hash(self, current_hash, row, col, piece_type):
        """Cập nhật hash O(1) khi có nước đi mới hoặc undo"""
        new_hash = current_hash ^ self.table[row][col][piece_type]
        new_hash ^= self.turn_hash 
        return new_hash

ZOBRIST = ZobristHashing()
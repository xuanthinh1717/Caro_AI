import json
import os
from game.move import Move

class OpeningBook:
    def __init__(self, filepath="src/plugins/book.json"):
        self.book = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.book = json.load(f)

    def get_move(self, state_hash) -> Move | None:
        """Trả về object Move nếu hash tồn tại trong book"""
        hash_str = str(state_hash)
        if hash_str in self.book:
            r, c = self.book[hash_str]
            return Move(r, c)
        return None
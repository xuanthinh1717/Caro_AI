import json
import os

class OpeningBook:
    def __init__(self, filepath="src/plugins/book.json"):
        self.book = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.book = json.load(f)

    def get_move(self, state_hash):
        hash_str = str(state_hash)
        if hash_str in self.book:
            return tuple(self.book[hash_str])
        return None
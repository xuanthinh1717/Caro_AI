EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

class TranspositionTable:
    def __init__(self, size_limit=2000000):
        self.table = {}
        self.size_limit = size_limit

    def store(self, zobrist_key, depth, score, flag, best_move):
        if len(self.table) >= self.size_limit:
            self.table.clear() 
            
        self.table[zobrist_key] = {
            'depth': depth,
            'score': score,
            'flag': flag,
            'best_move': best_move
        }

    def lookup(self, zobrist_key, depth, alpha, beta):
        if zobrist_key in self.table:
            entry = self.table[zobrist_key]
            if entry['depth'] >= depth:
                if entry['flag'] == EXACT:
                    return entry['score'], entry['best_move']
                elif entry['flag'] == LOWERBOUND and entry['score'] >= beta:
                    return entry['score'], entry['best_move']
                elif entry['flag'] == UPPERBOUND and entry['score'] <= alpha:
                    return entry['score'], entry['best_move']
        return None, None
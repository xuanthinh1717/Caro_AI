import time

class VCFSolver:
    def __init__(self, max_depth=11):
        self.max_depth = max_depth # Độ sâu tối đa để tìm chuỗi VCF (11 nước là rất sâu)
        
    def find_winning_path(self, board_state, current_player):
        """
        Tìm chuỗi thắng liên tục bằng cách ép đối thủ chặn Threat-4.
        Trả về nước đi đầu tiên trong chuỗi thắng, hoặc None nếu không có.
        """
        path = self._dfs_vcf(board_state, current_player, depth=0)
        if path and len(path) > 0:
            return path[0] # Trả về nước đi đầu tiên để thực thi
        return None

    def _dfs_vcf(self, state, attack_player, depth):
        if depth > self.max_depth:
            return None
            
        # 1. Nếu đối thủ vừa đi và tạo ra threat thắng ngay, mình phải chặn
        # (Giả định M1 có hàm get_winning_move / get_threat_4)
        if hasattr(state, 'get_winning_move'):
            opponent_win = state.get_winning_move(1 - attack_player)
            if opponent_win:
                return None 
        if not hasattr(state, 'get_moves_creating_threat_4'):
            return None

        candidate_attacks = state.get_moves_creating_threat_4(attack_player)
        
        for attack_move in candidate_attacks:
            state.make_move(attack_move)
            
            if state.check_win() == attack_player:
                state.undo_move(attack_move)
                return [attack_move]

            defense_move = state.get_forced_defense_move() 
            if defense_move:
                state.make_move(defense_move)
                
                sub_path = self._dfs_vcf(state, attack_player, depth + 2)
                
                state.undo_move(defense_move)
                state.undo_move(attack_move)
                
                if sub_path is not None:
                    return [attack_move, defense_move] + sub_path
            else:
                state.undo_move(attack_move)

        return None
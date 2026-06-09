from dataclasses import dataclass
from enum import IntEnum

from game.constants import BOARD_SIZE, EMPTY, WIN_LENGTH
from game.move import Move


class PatternType(IntEnum):
    """Loại pattern được phát hiện"""
    WINNING = 5          # 5 liên tiếp (chiến thắng)
    OPEN_4 = 44          # 4 liên tiếp mở 2 mặt (44XX00 hoặc 00XX44)
    LIVE_3 = 33          # 3 liên tiếp mở 2 mặt (33X00 hoặc 00X33)
    DEAD_4 = 444         # 4 liên tiếp, 1 mặt bị chặn
    LIVE_2 = 22          # 2 liên tiếp mở 2 mặt
    THREAT_4 = 434       # Có 2 cách tạo 4 liên tiếp
    BLOCKED_3 = 333      # 3 liên tiếp, 1 mặt bị chặn
    THREAT_3 = 233       # Có 2 cách tạo 3 liên tiếp mở


@dataclass
class LineInfo:
    """Thông tin về một line (hàng/cột/chéo)"""
    direction: tuple        # (dr, dc)
    piece_count: int        # Số quân liên tiếp
    empty_left: int         # Số ô trống trước (theo hướng âm)
    empty_right: int        # Số ô trống sau (theo hướng dương)
    player: int             # Quân của player nào (1=X, 2=O)
    pattern: PatternType    # Loại pattern


class PatternAnalyzer:
    """Phân tích pattern trên board"""
    
    DIRECTIONS = [
        (1, 0),      # Ngang
        (0, 1),      # Dọc
        (1, 1),      # Chéo /
        (1, -1),     # Chéo \
    ]
    
    @staticmethod
    def get_line_info(
        board,
        row: int,
        col: int,
        direction: tuple,
        player: int
    ) -> LineInfo:
        """
        Lấy thông tin về line tại vị trí (row, col) theo hướng.
        Trả về LineInfo với piece_count, empty_left, empty_right, pattern.
        """
        dr, dc = direction
        
        # Đếm quân liên tiếp theo hướng
        piece_count = 1
        
        # Đếm về phía âm (-direction)
        r, c = row - dr, col - dc
        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == player
        ):
            piece_count += 1
            r -= dr
            c -= dc
        
        # Vị trí ô trống đầu tiên về phía âm
        empty_left = 0
        r, c = row - dr, col - dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board.get_cell(r, c) == EMPTY:
                empty_left = 1
        
        # Đếm về phía dương (+direction)
        r, c = row + dr, col + dc
        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == player
        ):
            piece_count += 1
            r += dr
            c += dc
        
        # Vị trí ô trống đầu tiên về phía dương
        empty_right = 0
        r, c = row + dr, col + dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board.get_cell(r, c) == EMPTY:
                empty_right = 1
        
        # Xác định loại pattern
        pattern = PatternAnalyzer._classify_pattern(
            piece_count,
            empty_left,
            empty_right
        )
        
        return LineInfo(
            direction=direction,
            piece_count=piece_count,
            empty_left=empty_left,
            empty_right=empty_right,
            player=player,
            pattern=pattern
        )
    
    @staticmethod
    def _classify_pattern(
        piece_count: int,
        empty_left: int,
        empty_right: int
    ) -> PatternType:
        """Phân loại pattern dựa vào piece_count và số ô trống"""
        is_open_both_sides = empty_left > 0 and empty_right > 0
        is_open_one_side = (empty_left > 0 or empty_right > 0)
        
        if piece_count >= WIN_LENGTH:
            return PatternType.WINNING
        elif piece_count == 4:
            if is_open_both_sides:
                return PatternType.OPEN_4
            elif is_open_one_side:
                return PatternType.DEAD_4
            else:
                return PatternType.DEAD_4  # Bị chặn 2 mặt
        elif piece_count == 3:
            if is_open_both_sides:
                return PatternType.LIVE_3
            elif is_open_one_side:
                return PatternType.BLOCKED_3
            else:
                return PatternType.BLOCKED_3
        elif piece_count == 2:
            if is_open_both_sides:
                return PatternType.LIVE_2
            else:
                return PatternType.DEAD_4  # Placeholder
        else:
            return PatternType.LIVE_2
    
    @staticmethod
    def analyze_move(
        board,
        move: Move,
        player: int
    ) -> list[LineInfo]:
        """
        Phân tích nước đi: lấy thông tin 4 direction (ngang/dọc/2 chéo).
        Trả về danh sách LineInfo, sắp xếp theo piece_count (giảm dần).
        """
        lines = []
        
        for direction in PatternAnalyzer.DIRECTIONS:
            # Tạo board tạm để phân tích
            temp_board = board.clone()
            temp_board.place_piece(move.row, move.col, player)
            
            line_info = PatternAnalyzer.get_line_info(
                temp_board,
                move.row,
                move.col,
                direction,
                player
            )
            lines.append(line_info)
        
        # Sắp xếp theo piece_count giảm dần
        lines.sort(key=lambda x: x.piece_count, reverse=True)
        
        return lines
    
    @staticmethod
    def find_winning_moves(
        board,
        valid_moves: list[Move],
        player: int
    ) -> list[Move]:
        """Tìm các nước có thể chiến thắng ngay lập tức"""
        winning_moves = []
        
        for move in valid_moves:
            temp_board = board.clone()
            if not temp_board.place_piece(move.row, move.col, player):
                continue
            
            lines = []
            for direction in PatternAnalyzer.DIRECTIONS:
                line_info = PatternAnalyzer.get_line_info(
                    temp_board,
                    move.row,
                    move.col,
                    direction,
                    player
                )
                if line_info.pattern == PatternType.WINNING:
                    winning_moves.append(move)
                    break
        
        return winning_moves
    
    @staticmethod
    def find_threats(
        board,
        valid_moves: list[Move],
        player: int
    ) -> dict[PatternType, list[Move]]:
        """
        Nhóm các nước theo loại threat tạo ra.
        Trả về dict: {PatternType: [Move, ...]}
        """
        threats = {}
        
        for move in valid_moves:
            lines = PatternAnalyzer.analyze_move(
                board,
                move,
                player
            )
            
            best_pattern = lines[0].pattern if lines else None
            
            if best_pattern and best_pattern != PatternType.LIVE_2:
                if best_pattern not in threats:
                    threats[best_pattern] = []
                threats[best_pattern].append(move)
        
        return threats

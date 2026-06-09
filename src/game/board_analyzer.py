"""Phân tích board - lấy thông tin chi tiết các line, threats, v.v."""

from dataclasses import dataclass
from typing import Optional

from game.constants import BOARD_SIZE, EMPTY, PLAYER_X, PLAYER_O
from game.move import Move
from game.pattern import PatternAnalyzer, PatternType, LineInfo


@dataclass
class CellAnalysis:
    """Phân tích chi tiết một ô"""
    move: Move
    
    # Thông tin nếu X đặt ở đây
    x_lines: list[LineInfo]  # 4 direction lines cho X
    x_best_pattern: PatternType
    
    # Thông tin nếu O đặt ở đây
    o_lines: list[LineInfo]  # 4 direction lines cho O
    o_best_pattern: PatternType
    
    # Priority score (cao hơn = ưu tiên hơn)
    # AI sẽ dùng để sắp xếp nước đi
    priority_score: float = 0.0


class BoardAnalyzer:
    """Phân tích board để hỗ trợ AI"""
    
    @staticmethod
    def analyze_cell(
        board,
        move: Move,
        depth: int = 1
    ) -> CellAnalysis:
        """
        Phân tích 1 ô trống:
        - Nếu X đặt ở đây sẽ tạo patterns gì?
        - Nếu O đặt ở đây sẽ tạo patterns gì?
        - Priority score (nước này quan trọng cỡ nào?)
        """
        x_lines = PatternAnalyzer.analyze_move(board, move, PLAYER_X)
        x_best_pattern = x_lines[0].pattern if x_lines else None
        
        o_lines = PatternAnalyzer.analyze_move(board, move, PLAYER_O)
        o_best_pattern = o_lines[0].pattern if o_lines else None
        
        # Tính priority score (heuristic đơn giản)
        # AI sẽ có heuristic riêng, cái này chỉ để rank nước đi ban đầu
        priority_score = BoardAnalyzer._calculate_priority_score(
            x_best_pattern,
            o_best_pattern
        )
        
        return CellAnalysis(
            move=move,
            x_lines=x_lines,
            x_best_pattern=x_best_pattern,
            o_lines=o_lines,
            o_best_pattern=o_best_pattern,
            priority_score=priority_score
        )
    
    @staticmethod
    def _calculate_priority_score(
        x_pattern: Optional[PatternType],
        o_pattern: Optional[PatternType]
    ) -> float:
        """
        Tính priority score cho nước đi.
        Cao hơn = AI nên xem xét trước.
        
        Pattern priority (từ cao nhất):
        1. WINNING (5 liên tiếp)
        2. OPEN_4 (4 mở 2 mặt)
        3. DEAD_4 (4 bị chặn)
        4. LIVE_3 (3 mở 2 mặt)
        ...
        """
        pattern_scores = {
            PatternType.WINNING: 100,
            PatternType.OPEN_4: 50,
            PatternType.DEAD_4: 30,
            PatternType.THREAT_4: 80,
            PatternType.LIVE_3: 15,
            PatternType.BLOCKED_3: 10,
            PatternType.THREAT_3: 25,
            PatternType.LIVE_2: 2,
        }
        
        x_score = pattern_scores.get(x_pattern, 0) if x_pattern else 0
        o_score = pattern_scores.get(o_pattern, 0) if o_pattern else 0
        
        # Nếu o_pattern cao hơn, cần block (tăng priority)
        # Nếu x_pattern cao hơn, tấn công (tăng priority)
        return max(x_score, o_score * 0.9)  # Block không quan trọng bằng attack
    
    @staticmethod
    def get_candidate_analysis(
        board,
        distance: int = 2,
        top_n: Optional[int] = None
    ) -> list[CellAnalysis]:
        """
        Lấy danh sách ô ứng viên (gần các nước đã đi).
        Sắp xếp theo priority_score (cao nhất trước).
        
        Args:
            board: Board object
            distance: Tìm ô cách quân đã đi tối đa distance ô
            top_n: Chỉ lấy top N nước (nếu None thì lấy hết)
        
        Returns:
            Danh sách CellAnalysis sắp xếp theo priority_score giảm dần
        """
        from game.game_state import GameState
        
        # Tạo state để dùng get_candidate_moves
        state = GameState(
            board=board,
            current_player=PLAYER_X,
            winner=None,
            game_over=False,
            last_move=None
        )
        
        candidate_moves = state.get_candidate_moves(distance)
        
        # Phân tích từng nước
        analyses = []
        for move in candidate_moves:
            analysis = BoardAnalyzer.analyze_cell(board, move)
            analyses.append(analysis)
        
        # Sắp xếp theo priority_score giảm dần
        analyses.sort(
            key=lambda x: x.priority_score,
            reverse=True
        )
        
        if top_n is not None:
            analyses = analyses[:top_n]
        
        return analyses
    
    @staticmethod
    def get_critical_cells(
        board,
        player: int
    ) -> list[Move]:
        """
        Lấy các ô quan trọng nhất để xem xét (blocking/attacking).
        Chỉ lấy những nước tạo OPEN_4, DEAD_4, hay LIVE_3.
        """
        from game.game_state import GameState
        
        state = GameState(
            board=board,
            current_player=player,
            winner=None,
            game_over=False,
            last_move=None
        )
        
        critical = []
        
        for move in state.get_candidate_moves(distance=2):
            analysis = BoardAnalyzer.analyze_cell(board, move)
            
            # Kiểm tra xem bất kỳ player (X hoặc O) có tạo HIGH-PRIORITY pattern không
            x_critical = analysis.x_best_pattern in [
                PatternType.WINNING,
                PatternType.OPEN_4,
                PatternType.DEAD_4,
                PatternType.THREAT_4,
            ]
            o_critical = analysis.o_best_pattern in [
                PatternType.WINNING,
                PatternType.OPEN_4,
                PatternType.DEAD_4,
                PatternType.THREAT_4,
            ]
            
            if x_critical or o_critical:
                critical.append(move)
        
        return critical
    
    @staticmethod
    def get_board_heatmap(
        board,
        player: int = PLAYER_X
    ) -> list[list[float]]:
        """
        Trả về heatmap của board - priority score cho mỗi ô.
        Dùng để visualize hoặc debug AI strategy.
        
        Returns:
            List[List[float]] có kích thước BOARD_SIZE x BOARD_SIZE
            Giá trị = priority score, nếu ô đã có quân thì = -1
        """
        from game.constants import PLAYER_X, PLAYER_O
        
        heatmap = [
            [0.0 for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell = board.get_cell(row, col)
                
                if cell != EMPTY:
                    heatmap[row][col] = -1.0  # Ô đã có quân
                    continue
                
                move = Move(row, col)
                analysis = BoardAnalyzer.analyze_cell(board, move)
                heatmap[row][col] = analysis.priority_score
        
        return heatmap

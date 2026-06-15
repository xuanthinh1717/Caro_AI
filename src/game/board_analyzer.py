from dataclasses import dataclass
from typing import Optional

from game.constants import (
    BOARD_SIZE,
    EMPTY,
    PLAYER_X,
    PLAYER_O
)

from game.move import Move

from game.pattern import (
    PatternAnalyzer,
    PatternType,
    LineInfo
)


@dataclass
class CellAnalysis:
    """
    Phân tích một ô trống.
    """

    move: Move

    # Nếu X đánh vào đây
    x_lines: list[LineInfo]
    x_best_pattern: PatternType
    x_score: float

    # Nếu O đánh vào đây
    o_lines: list[LineInfo]
    o_best_pattern: PatternType
    o_score: float

    # Dùng để ranking candidate
    priority_score: float = 0.0


class BoardAnalyzer:
    """
    Phân tích board ở mức nước đi.

    PatternAnalyzer:
        xử lý từng direction

    BoardAnalyzer:
        xử lý toàn bộ move
        (fork, double threat, ...)
    """

    DOUBLE_LIVE3_BONUS = 50_000

    DOUBLE_OPEN4_BONUS = 500_000

    DOUBLE_DEAD4_BONUS = 100_000

    @staticmethod
    def analyze_cell(
        board,
        move: Move,
        depth: int = 1
    ) -> CellAnalysis:

        x_lines = PatternAnalyzer.analyze_move(
            board,
            move,
            PLAYER_X
        )

        o_lines = PatternAnalyzer.analyze_move(
            board,
            move,
            PLAYER_O
        )

        x_best_pattern = (
            x_lines[0].pattern
            if x_lines
            else PatternType.NONE
        )

        o_best_pattern = (
            o_lines[0].pattern
            if o_lines
            else PatternType.NONE
        )

        x_score = BoardAnalyzer._score_lines(
            x_lines
        )

        o_score = BoardAnalyzer._score_lines(
            o_lines
        )

        priority_score = max(
            x_score,
            o_score
        )

        return CellAnalysis(
            move=move,

            x_lines=x_lines,
            x_best_pattern=x_best_pattern,
            x_score=x_score,

            o_lines=o_lines,
            o_best_pattern=o_best_pattern,
            o_score=o_score,

            priority_score=priority_score
        )

    @staticmethod
    def _score_lines(
        lines: list[LineInfo]
    ) -> float:

        if not lines:
            return 0

        score = 0

        patterns = []

        for line in lines:

            score += PatternAnalyzer.get_pattern_score(
                line.pattern
            )

            patterns.append(
                line.pattern
            )

        live3_count = patterns.count(
            PatternType.LIVE_3
        )

        open4_count = patterns.count(
            PatternType.OPEN_4
        )

        dead4_count = patterns.count(
            PatternType.DEAD_4
        )

        # --------------------------------------------------
        # Fork detection
        # --------------------------------------------------

        if live3_count >= 2:
            score += (
                BoardAnalyzer.DOUBLE_LIVE3_BONUS
            )

        if open4_count >= 2:
            score += (
                BoardAnalyzer.DOUBLE_OPEN4_BONUS
            )

        if dead4_count >= 2:
            score += (
                BoardAnalyzer.DOUBLE_DEAD4_BONUS
            )

        return score

    @staticmethod
    def get_candidate_analysis(
        board,
        distance: int = 2,
        top_n: Optional[int] = None
    ) -> list[CellAnalysis]:

        from game.game_state import GameState

        state = GameState(
            board=board,
            current_player=PLAYER_X,
            winner=None,
            game_over=False,
            last_move=None
        )

        candidate_moves = (
            state.get_candidate_moves(
                distance
            )
        )

        analyses = []

        for move in candidate_moves:

            analyses.append(
                BoardAnalyzer.analyze_cell(
                    board,
                    move
                )
            )

        analyses.sort(
            key=lambda analysis:
                analysis.priority_score,
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

        from game.game_state import GameState

        state = GameState(
            board=board,
            current_player=player,
            winner=None,
            game_over=False,
            last_move=None
        )

        critical_moves = []

        for move in state.get_candidate_moves(
            distance=2
        ):

            analysis = (
                BoardAnalyzer.analyze_cell(
                    board,
                    move
                )
            )

            x_critical = (
                analysis.x_best_pattern
                in [
                    PatternType.WINNING,
                    PatternType.OPEN_4,
                    PatternType.DEAD_4,
                ]
            )

            o_critical = (
                analysis.o_best_pattern
                in [
                    PatternType.WINNING,
                    PatternType.OPEN_4,
                    PatternType.DEAD_4,
                ]
            )

            if x_critical or o_critical:
                critical_moves.append(
                    move
                )

        return critical_moves

    @staticmethod
    def get_board_heatmap(
        board,
        player: int = PLAYER_X
    ) -> list[list[float]]:

        heatmap = [
            [
                0.0
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        for row in range(
            BOARD_SIZE
        ):

            for col in range(
                BOARD_SIZE
            ):

                if (
                    board.get_cell(
                        row,
                        col
                    )
                    != EMPTY
                ):
                    heatmap[row][col] = -1
                    continue

                move = Move(
                    row,
                    col
                )

                analysis = (
                    BoardAnalyzer.analyze_cell(
                        board,
                        move
                    )
                )

                heatmap[row][col] = (
                    analysis.priority_score
                )

        return heatmap
from dataclasses import dataclass
from enum import IntEnum

from game.constants import BOARD_SIZE, EMPTY, WIN_LENGTH
from game.move import Move


class PatternType(IntEnum):
    """
    Pattern của MỘT direction.

    Lưu ý:
    THREAT_3 / THREAT_4 là pattern của cả move
    nên sẽ được xử lý ở BoardAnalyzer.
    """

    NONE = 0

    LIVE_2 = 10

    BLOCKED_3 = 20
    THREAT_3 = 25
    LIVE_3 = 30

    DEAD_4 = 40
    THREAT_4 = 45
    OPEN_4 = 50

    WINNING = 100


@dataclass
class LineInfo:
    direction: tuple
    piece_count: int

    empty_left: int
    empty_right: int

    player: int

    pattern: PatternType


class PatternAnalyzer:

    DIRECTIONS = [
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1),
    ]

    PATTERN_SCORES = {
        PatternType.NONE: 0,

        PatternType.LIVE_2: 500,

        PatternType.BLOCKED_3: 3_000,
        PatternType.THREAT_3: 8_000,
        PatternType.LIVE_3: 10_000,

        PatternType.DEAD_4: 30_000,
        PatternType.THREAT_4: 80_000,
        PatternType.OPEN_4: 100_000,

        PatternType.WINNING: 1_000_000,
    }

    @staticmethod
    def get_pattern_score(pattern: PatternType) -> int:
        return PatternAnalyzer.PATTERN_SCORES.get(pattern, 0)

    @staticmethod
    def get_line_info(
        board,
        row: int,
        col: int,
        direction: tuple,
        player: int
    ) -> LineInfo:

        dr, dc = direction

        piece_count = 1

        # ---- phía âm ----

        r, c = row - dr, col - dc

        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == player
        ):
            piece_count += 1
            r -= dr
            c -= dc

        empty_left = 0

        if (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == EMPTY
        ):
            empty_left = 1

        # ---- phía dương ----

        r, c = row + dr, col + dc

        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == player
        ):
            piece_count += 1
            r += dr
            c += dc

        empty_right = 0

        if (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and board.get_cell(r, c) == EMPTY
        ):
            empty_right = 1

        pattern = PatternAnalyzer._classify_pattern(
            piece_count,
            empty_left,
            empty_right
        )

        pattern = max(
            pattern,
            PatternAnalyzer._classify_line_pattern(
                board,
                row,
                col,
                direction,
                player
            )
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

        open_both = (
            empty_left > 0
            and empty_right > 0
        )

        open_one = (
            empty_left > 0
            or empty_right > 0
        )

        if piece_count >= WIN_LENGTH:
            return PatternType.WINNING

        if piece_count == 4:

            if open_both:
                return PatternType.OPEN_4

            if open_one:
                return PatternType.DEAD_4

            return PatternType.NONE

        if piece_count == 3:

            if open_both:
                return PatternType.LIVE_3

            if open_one:
                return PatternType.BLOCKED_3

            return PatternType.NONE

        if piece_count == 2:

            if open_both:
                return PatternType.LIVE_2

            return PatternType.NONE

        return PatternType.NONE

    @staticmethod
    def _classify_line_pattern(
        board,
        row: int,
        col: int,
        direction: tuple,
        player: int
    ) -> PatternType:

        cells = PatternAnalyzer._get_line_cells(
            board,
            row,
            col,
            direction,
            player
        )

        center_index = len(cells) // 2
        best_pattern = PatternType.NONE

        for segment_length in (WIN_LENGTH, WIN_LENGTH + 1):
            for start in range(len(cells) - segment_length + 1):
                end = start + segment_length

                if not (start <= center_index < end):
                    continue

                segment = cells[start:end]

                if "O" in segment:
                    continue

                player_count = segment.count("X")
                empty_count = segment.count(".")

                if "XXXXX" in "".join(segment):
                    return PatternType.WINNING

                if player_count == 4 and empty_count >= 1:
                    pattern = PatternAnalyzer._classify_four_segment(
                        segment
                    )
                    best_pattern = max(best_pattern, pattern)

                elif player_count == 3 and empty_count >= 2:
                    pattern = PatternAnalyzer._classify_three_segment(
                        segment
                    )
                    best_pattern = max(best_pattern, pattern)

                elif player_count == 2 and empty_count >= 2:
                    pattern = PatternAnalyzer._classify_two_segment(
                        segment
                    )
                    best_pattern = max(best_pattern, pattern)

        return best_pattern

    @staticmethod
    def _get_line_cells(
        board,
        row: int,
        col: int,
        direction: tuple,
        player: int
    ) -> list[str]:

        dr, dc = direction
        cells = []

        for offset in range(-5, 6):
            r = row + dr * offset
            c = col + dc * offset

            if not (
                0 <= r < BOARD_SIZE
                and 0 <= c < BOARD_SIZE
            ):
                cells.append("O")
                continue

            cell = board.get_cell(r, c)

            if cell == player:
                cells.append("X")
            elif cell == EMPTY:
                cells.append(".")
            else:
                cells.append("O")

        return cells

    @staticmethod
    def _classify_four_segment(segment: list[str]) -> PatternType:

        compact = "".join(segment)

        if "XXXX" in compact:
            x_start = compact.index("XXXX")
            left_open = (
                x_start - 1 >= 0
                and compact[x_start - 1] == "."
            )
            right_index = x_start + 4
            right_open = (
                right_index < len(compact)
                and compact[right_index] == "."
            )

            if left_open and right_open:
                return PatternType.OPEN_4

            return PatternType.DEAD_4

        return PatternType.THREAT_4

    @staticmethod
    def _classify_three_segment(segment: list[str]) -> PatternType:

        compact = "".join(segment)

        if "XXX" in compact:
            x_start = compact.index("XXX")
            left_open = (
                x_start - 1 >= 0
                and compact[x_start - 1] == "."
            )
            right_index = x_start + 3
            right_open = (
                right_index < len(compact)
                and compact[right_index] == "."
            )

            if left_open and right_open:
                return PatternType.LIVE_3

            if left_open or right_open:
                return PatternType.BLOCKED_3

            return PatternType.NONE

        return PatternType.THREAT_3

    @staticmethod
    def _classify_two_segment(segment: list[str]) -> PatternType:

        compact = "".join(segment)

        if "XX" not in compact:
            return PatternType.NONE

        x_start = compact.index("XX")
        left_open = (
            x_start - 1 >= 0
            and compact[x_start - 1] == "."
        )
        right_index = x_start + 2
        right_open = (
            right_index < len(compact)
            and compact[right_index] == "."
        )

        if left_open and right_open:
            return PatternType.LIVE_2

        return PatternType.NONE

    @staticmethod
    def analyze_move(
        board,
        move: Move,
        player: int
    ) -> list[LineInfo]:

        if (
            not (0 <= move.row < BOARD_SIZE)
            or not (0 <= move.col < BOARD_SIZE)
            or board.get_cell(move.row, move.col) != EMPTY
        ):
            return []

        temp_board = board.clone()

        if not temp_board.place_piece(
            move.row,
            move.col,
            player
        ):
            return []

        lines = []

        for direction in PatternAnalyzer.DIRECTIONS:

            line_info = PatternAnalyzer.get_line_info(
                temp_board,
                move.row,
                move.col,
                direction,
                player
            )

            lines.append(line_info)

        lines.sort(
            key=lambda line: (
                line.pattern,
                line.piece_count
            ),
            reverse=True
        )

        return lines

    @staticmethod
    def find_winning_moves(
        board,
        valid_moves: list[Move],
        player: int
    ) -> list[Move]:

        winning_moves = []

        for move in valid_moves:

            lines = PatternAnalyzer.analyze_move(
                board,
                move,
                player
            )

            if any(
                line.pattern == PatternType.WINNING
                for line in lines
            ):
                winning_moves.append(move)

        return winning_moves

    @staticmethod
    def find_threats(
        board,
        valid_moves: list[Move],
        player: int
    ) -> dict[PatternType, list[Move]]:

        threats = {}

        for move in valid_moves:

            lines = PatternAnalyzer.analyze_move(
                board,
                move,
                player
            )

            if not lines:
                continue

            best_pattern = lines[0].pattern

            if best_pattern == PatternType.NONE:
                continue

            if best_pattern not in threats:
                threats[best_pattern] = []

            threats[best_pattern].append(move)

        return threats

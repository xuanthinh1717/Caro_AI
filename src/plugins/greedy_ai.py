from ai.base import AIPlayer

from game.pattern import (
    PatternAnalyzer,
    PatternType
)

from game.board_analyzer import (
    BoardAnalyzer
)

from game.constants import (
    PLAYER_X,
    PLAYER_O
)


class GreedyAI(AIPlayer):

    @property
    def name(self):
        return "Greedy AI"

    def choose_move(self, state):

        valid_moves = state.get_valid_moves()

        current_player = state.current_player
        opponent = state.get_opponent()

        # ----------------------------------
        # 1. Thắng ngay
        # ----------------------------------

        winning_moves = (
            PatternAnalyzer.find_winning_moves(
                state.board,
                valid_moves,
                current_player
            )
        )

        if winning_moves:
            return winning_moves[0]

        # ----------------------------------
        # 2. Chặn đối thủ thắng ngay
        # ----------------------------------

        opponent_wins = (
            PatternAnalyzer.find_winning_moves(
                state.board,
                valid_moves,
                opponent
            )
        )

        if opponent_wins:
            return opponent_wins[0]

        # ----------------------------------
        # 3. Phân tích candidate
        # ----------------------------------

        candidates = (
            BoardAnalyzer.get_candidate_analysis(
                state.board,
                distance=2
            )
        )

        if not candidates:
            return (
                valid_moves[0]
                if valid_moves
                else None
            )

        # ----------------------------------
        # 4. Tìm nước nguy hiểm nhất của đối thủ
        # ----------------------------------

        if current_player == PLAYER_X:

            best_defense = max(
                candidates,
                key=lambda c: c.o_score
            )

            if best_defense.o_score >= 30_000:
                return best_defense.move

        else:

            best_defense = max(
                candidates,
                key=lambda c: c.x_score
            )

            if best_defense.x_score >= 30_000:
                return best_defense.move

        # ----------------------------------
        # 5. Tìm nước tấn công mạnh nhất
        # ----------------------------------

        if current_player == PLAYER_X:

            best_attack = max(
                candidates,
                key=lambda c: c.x_score
            )

            return best_attack.move

        else:

            best_attack = max(
                candidates,
                key=lambda c: c.o_score
            )

            return best_attack.move
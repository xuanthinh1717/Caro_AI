import time
import random
import io
import contextlib

from game.move import Move

from game.constants import PLAYER_X
from game.game_engine import GameEngine
from game.history import GameHistory

from evaluation.result import MatchResult


class MatchRunner:

    def run(
        self,
        player_x,
        player_o
    ) -> MatchResult:

        engine = GameEngine()

        history = GameHistory()

        history.set_initial_state(
            engine.state
        )

        # --------------------------------------------------
        # Random opening (2 nước gần trung tâm)
        # --------------------------------------------------

        center = 7

        opening_candidates = []

        for r in range(center - 1, center + 2):
            for c in range(center - 1, center + 2):
                opening_candidates.append(
                    Move(r, c)
                )

        random.shuffle(
            opening_candidates
        )

        for _ in range(2):

            valid_moves = [
                move
                for move in opening_candidates
                if engine.state.board.get_cell(
                    move.row,
                    move.col
                ) == 0
            ]

            if not valid_moves:
                break

            move = random.choice(
                valid_moves
            )

            engine.make_move(
                move
            )

            history.record_move(
                player=engine.state.get_opponent(),
                move=move,
                board_state=engine.state,
                timestamp=time.time()
            )


        x_times = []
        o_times = []

        start_time = time.perf_counter()

        while not engine.state.game_over:

            current_player_id = (
                engine.state.current_player
            )

            current_player = (
                player_x
                if current_player_id == PLAYER_X
                else player_o
            )

            think_start = time.perf_counter()

            with contextlib.redirect_stdout(
                io.StringIO()
            ):
                move = current_player.choose_move(
                    engine.state.clone()
                )

            think_time = (
                time.perf_counter()
                - think_start
            )

            success = engine.make_move(
                move
            )

            if not success:
                raise RuntimeError(
                    f"{current_player.name} "
                    f"returned invalid move: {move}"
                )

            if current_player_id == PLAYER_X:
                x_times.append(
                    think_time
                )
            else:
                o_times.append(
                    think_time
                )

            history.record_move(
                player=current_player_id,
                move=move,
                board_state=engine.state,
                timestamp=time.time()
            )

        duration = (
            time.perf_counter()
            - start_time
        )

        winner_ai = None

        if engine.state.winner is not None:

            if engine.state.winner == PLAYER_X:
                winner_ai = player_x.name
            else:
                winner_ai = player_o.name

        return MatchResult(
            ai_a_name=player_x.name,
            ai_b_name=player_o.name,
            winner_ai=winner_ai,
            move_count=history.get_move_count(),
            duration_seconds=duration,
            x_name=player_x.name,
            o_name=player_o.name,
            x_avg_move_time=(
                sum(x_times) / len(x_times)
                if x_times else 0
            ),
            o_avg_move_time=(
                sum(o_times) / len(o_times)
                if o_times else 0
            )
        )
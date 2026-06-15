from evaluation.match_runner import (
    MatchRunner
)


class TournamentRunner:

    def run(
        self,
        ai_a,
        ai_b,
        games=20
    ):

        results = []

        runner = MatchRunner()

        half = games // 2

        for _ in range(half):

            results.append(
                runner.run(
                    ai_a,
                    ai_b
                )
            )

        for _ in range(
            games - half
        ):

            results.append(
                runner.run(
                    ai_b,
                    ai_a
                )
            )

        return results
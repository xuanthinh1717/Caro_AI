from ai.loader import (
    load_ai_players
)

from evaluation.statistics import (
    StatisticsCollector
)

from evaluation.tournament_runner import (
    TournamentRunner
)

from evaluation.csv_exporter import (
    CsvExporter
)


def main():

    players = load_ai_players()

    print(
        f"Loaded {len(players)} AI(s)"
    )

    for ai in players:
        print(
            f" - {ai.name}"
        )

    print()

    tournament = (
        TournamentRunner()
    )

    csv_rows = []

    for i in range(len(players)):

        for j in range(
            i + 1,
            len(players)
        ):

            ai_a = players[i]
            ai_b = players[j]

            print("=" * 60)

            print(
                f"{ai_a.name}"
                f" vs "
                f"{ai_b.name}"
            )

            results = tournament.run(
                ai_a,
                ai_b,
                games=20
            )

            stats = (
                StatisticsCollector
                .summarize(results)
            )

            games_played = len(results)

            print("=" * 60)

            print(
                f"{stats['ai_a']} vs {stats['ai_b']}"
            )

            print(
                f"Games     : {games_played}"
            )

            print(
                f"{stats['ai_a']} Wins : "
                f"{stats['ai_a_wins']}"
            )

            print(
                f"{stats['ai_b']} Wins : "
                f"{stats['ai_b_wins']}"
            )

            print(
                f"Draws     : "
                f"{stats['draws']}"
            )

            print(
                f"Avg Moves : "
                f"{stats['avg_moves']:.2f}"
            )

            win_rate_a = (
                stats["ai_a_wins"]
                / games_played
                * 100
            )

            win_rate_b = (
                stats["ai_b_wins"]
                / games_played
                * 100
            )

            print(
                f"{stats['ai_a']} WR : "
                f"{win_rate_a:.1f}%"
            )

            print(
                f"{stats['ai_b']} WR : "
                f"{win_rate_b:.1f}%"
            )

            print(f"{stats['ai_a']} Avg Time : "
                  f"{stats['ai_a_avg_time']}"
            )

            print(f"{stats['ai_b']} Avg Time : "
                  f"{stats['ai_b_avg_time']}"
            )

            print()

            csv_rows.append(
                {
                    "AI_A": stats["ai_a"],
                    "AI_B": stats["ai_b"],
                    "AI_A_Wins": stats["ai_a_wins"],
                    "AI_B_Wins": stats["ai_b_wins"],
                    "Draws": stats["draws"],
                    "Avg_Moves": round(
                        stats["avg_moves"],
                        2
                    ),
                    "AI_A_Avg_Time": stats['ai_a_avg_time'],
                    "AI_B_Avg_Time": stats['ai_b_avg_time']
                }
            )

    CsvExporter.save_matchups(
        csv_rows,
    )

    print("=" * 60)
    print(
        f"Saved {len(csv_rows)} matchup(s) "
        f"to results.csv"
    )
    print("DONE")


if __name__ == "__main__":
    main()
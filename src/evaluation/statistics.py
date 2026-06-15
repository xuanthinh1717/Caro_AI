class StatisticsCollector:

    @staticmethod
    def summarize(results):

        ai_a_wins = 0
        ai_b_wins = 0
        draws = 0

        total_moves = 0

        ai_a_name = None
        ai_b_name = None

        total_ai_a_time = 0
        total_ai_b_time = 0

        for result in results:

            total_moves += result.move_count

            if ai_a_name is None:
                ai_a_name = result.ai_a_name

            if ai_b_name is None:
                ai_b_name = result.ai_b_name

            if result.winner_ai == ai_a_name:
                ai_a_wins += 1

            elif result.winner_ai == ai_b_name:
                ai_b_wins += 1

            else:
                draws += 1
            if result.x_name == ai_a_name:

                total_ai_a_time += (
                    result.x_avg_move_time
                )

                total_ai_b_time += (
                    result.o_avg_move_time
                )

            else:

                total_ai_a_time += (
                    result.o_avg_move_time
                )

                total_ai_b_time += (
                    result.x_avg_move_time
                )

        return {
            "ai_a": ai_a_name,
            "ai_b": ai_b_name,
            "ai_a_wins": ai_a_wins,
            "ai_b_wins": ai_b_wins,
            "draws": draws,
            "avg_moves":
                total_moves / len(results),
            "ai_a_avg_time":
                total_ai_a_time / len(results),
            "ai_b_avg_time":
                total_ai_b_time / len(results)                
        }
import csv
import os


class CsvExporter:

    @staticmethod
    def save_matchups(
        rows,
        filename="results.csv"
    ):

        output_dir = "outputs"

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        filepath = os.path.join(
            output_dir,
            filename
        )

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "AI_A",
                    "AI_B",
                    "AI_A_Wins",
                    "AI_B_Wins",
                    "Draws",
                    "Avg_Moves",
                    "AI_A_Avg_Time",
                    "AI_B_Avg_Time"
                ]
            )

            writer.writeheader()

            writer.writerows(rows)

        return filepath
from dataclasses import dataclass


@dataclass
class MatchResult:

    ai_a_name: str
    ai_b_name: str

    winner_ai: str | None

    move_count: int

    duration_seconds: float

    x_name: str
    o_name: str

    x_avg_move_time: float
    o_avg_move_time: float
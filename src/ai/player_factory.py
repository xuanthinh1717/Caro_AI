from ai.human_player import HumanPlayer
from ai.loader import load_ai_players


def create_player(player_name):

    if player_name == "Human":
        return HumanPlayer()

    for ai in load_ai_players():

        if ai.name == player_name:
            return ai

    raise ValueError(
        f"Unknown player: {player_name}"
    )
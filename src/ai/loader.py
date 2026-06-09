import inspect
import importlib
import pkgutil
import os

from ai.base import AIPlayer

def load_ai_players():

    players = []
    
    # Get plugins directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    plugins_dir = os.path.join(
        os.path.dirname(current_dir),
        "plugins"
    )

    for _, module_name, _ in pkgutil.iter_modules(
        [plugins_dir]
    ):

        try:
            module = importlib.import_module(
                f"plugins.{module_name}"
            )

            for _, obj in inspect.getmembers(
                module,
                inspect.isclass
            ):

                if (
                    issubclass(
                        obj,
                        AIPlayer
                    )
                    and obj is not AIPlayer
                ):

                    players.append(
                        obj()
                    )
        
        except Exception as e:
            # Skip modules that fail to load
            pass

    return players
from abc import ABC, abstractmethod

from abc import ABC, abstractmethod


class AIPlayer(ABC):

    @property
    def is_human(self):
        return False

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def choose_move(self, state):
        pass
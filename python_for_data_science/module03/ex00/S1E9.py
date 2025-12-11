from abc import ABC, abstractmethod


class Character(ABC):
    """Your docstring for Class"""
    def __init__(self, first_name: str, is_alive: bool = True) -> None:
        """Your docstring for Constructor"""
        self.first_name = first_name
        self.is_alive = is_alive

    @abstractmethod
    def die(self) -> None:
        """Your docstring for Method"""
        pass


class Stark(Character):
    """Your docstring for Class"""
    def die(self) -> None:
        """Your docstring for Method"""
        self.is_alive = False

from S1E7 import Baratheon, Lannister


class King(Baratheon, Lannister):
    """Representing the false king Joffrey Baratheon (diamond inheritance)."""
    def __init__(self, first_name: str) -> None:
        super().__init__(first_name=first_name)

    def set_eyes(self, value: str) -> None:
        """Set the eye color of the king."""
        self.eyes = value

    def get_eyes(self) -> str:
        """Get the eye color of the king."""
        return self.eyes

    def set_hairs(self, value: str) -> None:
        """Set the hair color of the king."""
        self.hairs = value

    def get_hairs(self) -> str:
        """Get the hair color of the king."""
        return self.hairs

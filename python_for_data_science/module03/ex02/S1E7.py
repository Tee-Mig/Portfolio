from S1E9 import Character


class Baratheon(Character):
    """Representing the Baratheon family"""
    def __init__(
        self,
        first_name: str,
        is_alive: bool = True,
        family_name: str = "Baratheon",
        eyes: str = "brown",
        hairs: str = "dark"
    ) -> None:
        self.first_name = first_name
        self.is_alive = is_alive
        self.family_name = family_name
        self.eyes = eyes
        self.hairs = hairs

    def die(self) -> None:
        """Mark the object as no longer
        alive by setting `is_alive` to False."""
        self.is_alive = False

    def __str__(self) -> str:
        """Return a user-friendly string representation of the object."""
        return f"Vector: ('Baratheon', '{self.eyes}', '{self.hairs}')"

    def __repr__(self) -> str:
        """Return an unambiguous string
        representation of the object for developers."""
        return f"Vector: ('Baratheon', '{self.eyes}', '{self.hairs}')"


class Lannister(Character):
    """Representing the Lannister family"""
    def __init__(
        self,
        first_name: str,
        is_alive: bool = True,
        family_name: str = "Lannister",
        eyes: str = "blue",
        hairs: str = "light"
    ) -> None:
        self.first_name = first_name
        self.is_alive = is_alive
        self.family_name = family_name
        self.eyes = eyes
        self.hairs = hairs

    def die(self) -> None:
        """Mark the object as no longer
        alive by setting `is_alive` to False."""
        self.is_alive = False

    def __repr__(self) -> str:
        """Return a user-friendly string representation of the object."""
        return f"Vector: ('Lannister', '{self.eyes}', '{self.hairs}')"

    def __str__(self) -> str:
        """Return an unambiguous string
        representation of the object for developers."""
        return f"Vector: ('Lannister', '{self.eyes}', '{self.hairs}')"

    @classmethod
    def create_lannister(
        cls,
        first_name: str,
        is_alive: bool = True
    ) -> "Lannister":
        """Factory method to create a Lannister
        with the given name and alive status."""
        return cls(first_name, is_alive)

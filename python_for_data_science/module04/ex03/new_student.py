import random
import string
from dataclasses import dataclass, field


def generate_id() -> str:
    """Generate a random 15-character lowercase identifier"""
    return "".join(random.choices(string.ascii_lowercase, k=15))


@dataclass
class Student:
    """
    Simple student record.

    Attributes:
        name: Student first name
        surname: Student surname
        active: Whether the student is active (always True at creation)
        login: Computed as first letter of name (uppercase) + surname
        id: Random 15-character lowercase identifier
    """

    name: str
    surname: str
    active: bool = True
    login: str = field(init=False)
    id: str = field(init=False, default_factory=generate_id)

    def __post_init__(self) -> None:
        """Compute login from name and surname after initialization."""
        if not self.name or not self.surname:
            raise ValueError("name and surname must be non-empty")
        self.login = f"{self.name[0].upper()}{self.surname}"

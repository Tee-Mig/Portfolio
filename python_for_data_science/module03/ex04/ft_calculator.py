class calculator:
    """A simple vector calculator with static methods."""

    @staticmethod
    def dotproduct(V1: list[float], V2: list[float]) -> None:
        """Compute and print dot product of two vectors."""
        result = sum([a * b for a, b in zip(V1, V2)])
        print(f"Dot product is: {result}")

    @staticmethod
    def add_vec(V1: list[float], V2: list[float]) -> None:
        """Compute and print element-wise addition of two vectors."""
        result = [float(a + b) for a, b in zip(V1, V2)]
        print(f"Add Vector is: {result}")

    @staticmethod
    def sous_vec(V1: list[float], V2: list[float]) -> None:
        """Compute and print element-wise subtraction of two vectors."""
        result = [float(a - b) for a, b in zip(V1, V2)]
        print(f"Sous Vector is: {result}")

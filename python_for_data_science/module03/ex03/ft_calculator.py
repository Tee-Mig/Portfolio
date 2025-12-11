class calculator:
    def __init__(self, values: list = None):
        """A simple calculator class for arithmetic
        operations on a list of numbers."""
        if values is None:
            values = []
        self.result = values

    def __add__(self, object) -> None:
        """Initialize the calculator with an optional list of numbers."""
        self.result = [num + object for num in self.result]
        print(self.result)

    def __mul__(self, object) -> None:
        """Add a number to each element in the result list."""
        self.result = [num * object for num in self.result]
        print(self.result)

    def __sub__(self, object) -> None:
        """Subtract a number from each element in the result list."""
        self.result = [num - object for num in self.result]
        print(self.result)

    def __truediv__(self, object) -> None:
        """Divide each element in the result
        list by a number, unless dividing by zero."""
        if object != 0:
            self.result = [num / object for num in self.result]
            print(self.result)
        else:
            print("It's impossible to divide by 0")

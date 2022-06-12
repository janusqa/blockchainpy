class Food:
    # class variables
    name = None
    kind = None

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def describe(self):
        print(f"{self.name} is a kind of {self.kind}")

    @classmethod
    def describe_class(cls):
        print(f"{cls.name} is a kind of {cls.kind}")

    @staticmethod
    def describe_static(name, kind):
        print(f"{name} is a kind of {kind}")

    def __repr__(self):
        return str(self.__dict__)


class Meat(Food):
    def __init__(self, name):
        super().__init__(name, "meat")

    def cook(self):
        print(f"Cook {self.name}")


class Fruit(Food):
    def __init__(self, name):
        super().__init__(name, "fruit")

    def clean(self):
        print(f"clean {self.name}")


# instance
peach = Food("peach", "fruit")
peach.describe()

# classmethod
Food.name = "peach"
Food.kind = "fruit"
Food.describe_class()

# static
Food.describe_static("peach", "fruit")

peach = Fruit("peach")
peach.describe()
peach.clean()

chicken = Meat("chicken")
chicken.describe()
chicken.cook()

print(peach, chicken)

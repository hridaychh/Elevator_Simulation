"""ELEVATOR SIMULATION - People and Elevators

"""
from __future__ import annotations
from python_ta.contracts import check_contracts
from ES_visualizer import PersonSprite, ElevatorSprite


@check_contracts
class Person(PersonSprite):
    """A person in the elevator simulation.

    Instance Attributes:
    - start: the floor this person started on
    - target: the floor this person wants to go to
    - wait_time: the number of rounds this person has been waiting

    Representation Invariants:
    - self.start >= 1
    - self.target >= 1
    - self.start != self.target
    - self.wait_time >= 0
    """
    start: int
    target: int
    wait_time: int

    def __init__(self, start: int, target: int) -> None:
        """Initialize a person with the given start and target floor.

        A person's waiting time always starts at 0.

        Preconditions:
        - start >= 1
        - target >= 1
        """
        self.wait_time = 0
        self.start = start
        self.target = target
        PersonSprite.__init__(self)

    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
        - Level 0: waiting 0-2 rounds
        - Level 1: waiting 3-4 rounds
        - Level 2: waiting 5-6 rounds
        - Level 3: waiting 7-8 rounds
        - Level 4: waiting >= 9 rounds

        >>> my_person = Person(1, 5)
        >>> my_person.wait_time = 5
        >>> my_person.get_anger_level()
        2
        """
        x = self.wait_time
        if x in [0, 1, 2]:
            return 0
        elif x in [3, 4]:
            return 1
        elif x in [5, 6]:
            return 2
        elif x in [7, 8]:
            return 3
        else:
            return 4

    def __repr__(self) -> str:
        """Return a string representation of this Person.

        >>> my_person = Person(1, 5)
        >>> my_person
        Person(start=1, target=5, wait_time=0)
        """
        return f'Person(start={self.start}, target={self.target}, wait_time={self.wait_time})'


@check_contracts
class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Instance Attributes:
    - capacity: The maximum number of people on this elevator
    - current_floor: The floor this elevator is on
    - passengers:
        The passengers of this elevator
    - target_floor: the floor this elevator is headed towards

    Representation Invariants:
    - self.current_floor >= 1
    - self.capacity > 0
    - len(self.passengers) <= self.capacity
    - self.target_floor >= 1
    """
    capacity: int
    current_floor: int
    passengers: list[Person]
    target_floor: int

    def __init__(self, capacity: int) -> None:
        """Initialize a new elevator with the given capacity.

        Elevators always start with a current and target floor of 1, and no passengers.

        Preconditions:
        - capacity > 0
        """
        self.capacity = capacity
        self.current_floor = 1
        self.target_floor = 1
        ElevatorSprite.__init__(self)

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

        >>> my_elevator = Elevator(10)
        >>> my_elevator.fullness()
        0.0
        """
        return len(self.passengers) / self.capacity


if __name__ == '__main__':
    import doctest
    doctest.testmod()

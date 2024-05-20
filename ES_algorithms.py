"""ELEVATOR SIMULATION - Algorithms

"""
import csv
from python_ta.contracts import check_contracts
from ES_entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
@check_contracts
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    Instance Attributes:
    - max_floor: The maximum floor number for the building.
        Generated people must not have a starting or target floor
        beyond this floor.

    Representation Invariants:
    - self.max_floor >= 2
    """
    max_floor: int

    def __init__(self, max_floor: int) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
        - max_floor >= 2
        """
        self.max_floor = max_floor

    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        If there two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Preconditions:
        - round_num >= 0
        """
        raise NotImplementedError


@check_contracts
class SingleArrivals(ArrivalGenerator):
    """An arrival generator that adds one person to floor 1 each round.

    SingleArrivals.generate algorithm description:

    - This implementation always generates exactly ONE Person per round.
    - The new Person always has a starting floor of 1.
    - At round 0, the new Person has a target floor of 2.
    - At each subsequent round, the new Person has a target floor one greater than
      the previous round, until self.max_floor is reached. At the next round, the target floor
      starts back at 2.
    - For example, if self.max_floor == 4:
        - Round 0: target floor 2
        - Round 1: target floor 3
        - Round 2: target floor 4
        - Round 3: target floor 2
        - Round 4: target floor 3
        - Round 5: target floor 4
        - Round 6: target floor 2
        - etc.
    """
    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        If there are two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Preconditions:
        - round_num >= 0

        >>> my_generator = SingleArrivals(4)
        >>> my_arrivals = my_generator.generate(0)
        >>> len(my_arrivals) == 1
        True
        >>> print(my_arrivals[1])
        [Person(start=1, target=2, wait_time=0)]
        """
        dic = {}
        tgt_flr = (round_num % (self.max_floor - 1)) + 2
        p = Person(1, tgt_flr)
        if p.start not in dic:
            dic[p.start] = [p]
        else:
            dic[p.start].append(p)
        return dic


@check_contracts
class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    Instance Attributes:
    - arrival_data: the arrivals parsed from the given csv file.

    Representation Invariants:
    - Every key in self._arrival_data is >= 0

    """
    arrival_data: dict[int, list[Person]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm.
        """
        ArrivalGenerator.__init__(self, max_floor)
        self.arrival_data = {}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.arrival_data[int(line[0])] = []
                for i in range(1, len(line), 2):
                    self.arrival_data[int(line[0])].append(Person(int(line[i]), int(line[i + 1])))

    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        If there are two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Preconditions:
        - round_num >= 0

        >>> my_generator = FileArrivals(5, 'data/sample_arrivals.csv')
        >>> round0_arrivals = my_generator.generate(0)
        >>> len(round0_arrivals)  # Only two floors in the dictionary
        2
        >>> print(round0_arrivals[1])
        [Person(start=1, target=4, wait_time=0)]
        >>> print(round0_arrivals[5])
        [Person(start=5, target=3, wait_time=0)]
        """
        if round_num not in self.arrival_data:
            self.arrival_data[round_num] = []
        people = self.arrival_data[round_num]
        dic = {}
        for p in people:
            if p.start not in dic:
                dic[p.start] = [p]
            else:
                dic[p.start].append(p)
        return dic

###############################################################################
# Elevator moving algorithms
###############################################################################


@check_contracts
class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.

    IMPORTANT: this algorithm doesn't actually move the elevators, i.e., it doesn't change
    their current floor. Instead, it only updates the target_floor attribute of each elevator
    (or leaves it unchanged). The actual moving should be done in Simulation.move_elevators.

    """
    def update_target_floors(self,
                             elevators: list[Elevator],
                             waiting: dict[int, list[Person]],
                             max_floor: int) -> None:
        """Updates elevator target floors.

        The parameters are:
        - elevators: a list of the system's elevators
        - waiting: a dictionary mapping floor number to the list of people waiting on that floor
        - max_floor: the maximum floor number in the simulation

        Preconditions:
        - elevators, waiting, and max_floor are from the same simulation run
        """
        raise NotImplementedError


@check_contracts
class EndToEndLoop(MovingAlgorithm):
    """A moving algorithm that causes every elevator to move between the bottom and top floors.

    Algorithm description:

    - For each elevator:
        - If the elevator's current floor is 1, the target_floor is set to the max_floor.
        - If the elevator's current floor is max_floor, the target_floor is set to 1.
        - In all other cases, the elevator's target_floor is unchanged.
    - This algorithm behaves the same way for all elevators.
    - This algorithm IGNORES the passengers on the elevators, and the people
      who are waiting for an elevator.
    """
    def update_target_floors(self,
                             elevators: list[Elevator],
                             waiting: dict[int, list[Person]],
                             max_floor: int) -> None:
        """Updates elevator target floors.

        The parameters are:
        - elevators: a list of the system's elevators
        - waiting: a dictionary mapping floor number to the list of people waiting on that floor
        - max_floor: the maximum floor number in the simulation

        Preconditions:
        - elevators, waiting, and max_floor are from the same simulation run
        """
        for e in elevators:
            if e.current_floor == 1:
                e.target_floor = max_floor
            elif e.current_floor == max_floor:
                e.target_floor = 1


@check_contracts
class FurthestFloor(MovingAlgorithm):
    """A moving algorithm that chooses far-away target floors.

    Algorithm description:

    For *each* elevator:

    - *Case 1*: If the elevator has at least one passenger, set the elevator's target floor
      to be the floor that is a passenger's target floor and is the furthest away from the
      elevator's current floor.
    - *Case 2*: If the elevator has no passengers and is idle, set the elevator's target floor
      to be the floor that has at least one passenger waiting and is the furthest away from the
      elevator's current floor.
        - If there are no waiting people at all, set the elevator's target floor to the
          current floor. The elevator remains idle and does not move this round.
    - *Case 3*: If the elevator has no passengers and is not idle, do not change the target floor.

    Note: In Cases 1 and 2, if there is a tie, always pick the *lowest* floor.
    """
    def update_target_floors(self,
                             elevators: list[Elevator],
                             waiting: dict[int, list[Person]],
                             max_floor: int) -> None:
        """Updates elevator target floors.

        The parameters are:
        - elevators: a list of the system's elevators
        - waiting: a dictionary mapping floor number to the list of people waiting on that floor
        - max_floor: the maximum floor number in the simulation

        Preconditions:
        - elevators, waiting, and max_floor are from the same simulation run
        """
        for e in elevators:
            if len(e.passengers) != 0:
                dist = []
                for p in e.passengers:
                    dist.append(abs(e.current_floor - p.target))
                max_dist = max(dist)
                note = []
                for d in dist:
                    if max_dist == d:
                        note.append(dist.index(d))
                list_floor = []
                for index_max_dist in note:
                    list_floor.append(e.passengers[index_max_dist].target)
                e.target_floor = min(list_floor)
            else:
                if e.target_floor == e.current_floor:
                    dist = []
                    f = []
                    for floor in waiting:
                        if len(waiting[floor]) != 0:
                            f.append(floor)
                    if len(f) == 0:
                        e.target_floor = e.current_floor
                    else:
                        for item in f:
                            dist.append(abs(item - e.current_floor))
                        max_dist = max(dist)
                        note = []
                        for d in dist:
                            if max_dist == d:
                                note.append(dist.index(d))
                        list_floor = []
                        for index_max_dist in note:
                            list_floor.append(f[index_max_dist])
                        e.target_floor = min(list_floor)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

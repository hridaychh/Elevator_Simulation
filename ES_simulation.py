"""ELEVATOR SIMULATION - Simulation

"""
from typing import Any
from python_ta.contracts import check_contracts

import ES_algorithms
from ES_entities import Person, Elevator
from ES_visualizer import Direction, Visualizer


@check_contracts
class Simulation:
    """The main simulation class.

    Instance Attributes:
    - arrival_generator: the algorithm used to generate new arrivals.
    - elevators: a list of the elevators in the simulation
    - moving_algorithm: the algorithm used to decide how to move elevators
    - num_floors: the number of floors
    - visualizer: the Pygame visualizer used to visualize this simulation
    - waiting: a dictionary of people waiting for an elevator, where:
        - The keys are floor numbers from 1 to num_floors, inclusive
        - Each corresponding value is the list of people waiting at that floor
          (could be an empty list)
    - total_people: a list of people that arrived at some point during the simulation
    - reached_dest: the number of people who reached their target destination by the end of
                    the simulation

    Representation Invariants:
    - len(self.elevators) >= 1
    - self.num_floors >= 2
    - list(self.waiting.keys()) == list(range(1, self.num_floors + 1))
    """
    arrival_generator: ES_algorithms.ArrivalGenerator
    elevators: list[Elevator]
    moving_algorithm: ES_algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: dict[int, list[Person]]
    total_people: list[Person]
    reached_dest: list[Person]

    def __init__(self,
                 config: dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration.

        Preconditions:
        - config is a dictionary in the format found on the assignment handout
        - config['num_floors'] >= 2
        - config['elevator_capacity'] >= 1
        - config['num_elevators'] >= 1

        """

        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']
        temp_lst = []
        for i in range(config['num_elevators']):
            temp_lst.append(Elevator(config['elevator_capacity']))
        self.elevators = temp_lst
        self.num_floors = config['num_floors']
        temp_dic = {}
        for i in range(self.num_floors):
            floor = i + 1
            temp_dic[floor] = []
        self.waiting = temp_dic
        self.visualizer = Visualizer(self.elevators, self.num_floors,
                                     config['visualize'])
        self.total_people = []
        self.reached_dest = []

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> dict[str, int]:
        """Run the simulation for the given number of rounds.

        Preconditions:
        - num_rounds >= 1
        - This method is only called once for each Simulation instance
        """
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: elevator disembarking
            self.handle_disembarking()

            # Stage 2: new arrivals
            self.generate_arrivals(i)

            # Stage 3: elevator boarding
            self.handle_boarding()

            # Stage 4: move the elevators
            self.move_elevators()

            # Stage 5: update wait times
            self.update_wait_times()

            # Pause for 1 second
            self.visualizer.wait(1)

        # The following line waits until the user closes the Pygame window
        self.visualizer.wait_for_exit()
        return self._calculate_stats(num_rounds)

    def handle_disembarking(self) -> None:
        """Handle people leaving elevators.
        """
        for e in self.elevators:
            temp = []
            for p in e.passengers:
                if e.current_floor == p.target:
                    self.reached_dest.append(p)
                    temp.append(p)
            for p1 in temp:
                e.passengers.remove(p1)
                self.visualizer.show_disembarking(p1, e)

    def generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        my_generator = self.arrival_generator
        my_arrivals = my_generator.generate(round_num)
        for key in my_arrivals:
            self.waiting[key].extend(my_arrivals[key])
            self.total_people.extend(my_arrivals[key])
        self.visualizer.show_arrivals(my_arrivals)

    def handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for e in self.elevators:
            boarded = {}
            for key in self.waiting:
                if e.current_floor == key:
                    for p in self.waiting[key]:
                        if ((key > p.target) and (e.target_floor <= key)) or (
                                (key < p.target) and (e.target_floor >= key)):
                            if len(e.passengers) < e.capacity:
                                e.passengers.append(p)
                                self.visualizer.show_boarding(p, e)
                                if key not in boarded:
                                    boarded[key] = [p]
                                else:
                                    boarded[key].append(p)
            for f in boarded:
                for person in boarded[f]:
                    self.waiting[f].remove(person)

    def move_elevators(self) -> None:
        """Update elevator target floors and then move them."""
        self.moving_algorithm.update_target_floors(self.elevators, self.waiting, self.num_floors)
        directions = []
        for e in self.elevators:
            if e.current_floor > e.target_floor:
                e.current_floor -= 1
                directions.append(Direction.DOWN)
            elif e.current_floor < e.target_floor:
                e.current_floor += 1
                directions.append(Direction.UP)
            else:
                directions.append(Direction.STAY)
        self.visualizer.show_elevator_moves(self.elevators, directions)

    def update_wait_times(self) -> None:
        """Update the waiting time for every person waiting in this simulation.

        Note that this includes both people waiting for an elevator AND people
        who are passengers on an elevator. It does not include people who have
        reached their target floor.
        """
        for e in self.elevators:
            for p in e.passengers:
                p.wait_time += 1
        for key in self.waiting:
            for p1 in self.waiting[key]:
                p1.wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self, num_rounds: int) -> dict[str, int]:
        """Report the statistics for the current run of this simulation, including
        <num_rounds>.

        Preconditions:
        - This method is only called after the simulation rounds have finished
        """
        if len(self.reached_dest) == 0:
            max_time = -1
            avg_time = -1
        else:
            wait_times = []
            for p in self.reached_dest:
                wait_times.append(p.wait_time)
            max_time = max(wait_times)
            sum_ = sum(wait_times)
            avg_time = int((sum_ / len(wait_times)))

        return {
            'num_rounds': num_rounds,
            'total_people': len(self.total_people),
            'people_completed': len(self.reached_dest),
            'max_time': max_time,
            'avg_time': avg_time
        }


###############################################################################
# Simulation runner
###############################################################################
def run_example_simulation() -> dict[str, int]:
    """Run a sample simulation, and return the simulation statistics.

    """
    num_floors = 6
    num_elevators = 2
    elevator_capacity = 2

    config = {
        'num_floors': num_floors,
        'num_elevators': num_elevators,
        'elevator_capacity': elevator_capacity,
        'arrival_generator': ES_algorithms.FileArrivals(num_floors, 'data/sample_arrivals_ten.csv'),
        'moving_algorithm': ES_algorithms.FurthestFloor(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    sample_run_stats = run_example_simulation()
    print(sample_run_stats)

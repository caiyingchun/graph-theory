from graph import Graph
import itertools

__description__ = """

This is the slight more advanced example with time windows.

Transshipment problems form a subgroup of transportation problems, where 
transshipment is allowed. In transshipment, transportation may or must go 
through intermediate nodes, possibly changing modes of transport.

Transshipment or Transhipment is the shipment of goods or containers to an 
intermediate destination, and then from there to yet another destination. One 
possible reason is to change the means of transport during the journey (for 
example from ship transport to road transport), known as transloading. Another 
reason is to combine small shipments into a large shipment (consolidation), 
dividing the large shipment at the other end (deconsolidation). Transshipment 
usually takes place in transport hubs. Much international transshipment also 
takes place in designated customs areas, thus avoiding the need for customs 
checks or duties, otherwise a major hindrance for efficient transport.

[1](https://en.wikipedia.org/wiki/Transshipment_problem)

Prologue: Scheduling!
------------------------------------------------------------------------------
The proposal is to treat the jobs as actors instead of objects.

The N-machine scheduling problem is thereby a problem defined as:

Determine the solution with minimum total slack time (from start to end)
subject to the constraints:
1. total ordering given by completeness of each order as a set.
   (All items required in an order must be packed and shipped together)
2. The capacity constraints of each machine.
3. The route of each job through the network of machines.

The emphasis is therefore on the proposition that jobs need to search for
paths to reach their required destination within a time-window and book
their space on the machines as required.

Think of this a person attempting to travel from Oxford University to MIT,
Boston: The trip contains a number of route options:
    1. fly from London Heathrow or from Birmingham to Boston Logan
    2. drive to the airport or take train, taxi, ...
    3. rent a car, take a taxi, ... at the destination airport.

A job is thereby a path through a number of waypoints.
The job will face resource constraints (travel time, time windows)

Likewise the machinery involved will face a number of constraints, and if
it's completely utilised, it will not care one bit whether it handles one
job or another. A taxi driver however will care if one job provides the
opportunity for a return trip whilst another doesn't.

However attempting to let the Taxi determine the optimal schedule, in
contrast to the travel, seems intuitively like a bad a idea. Yet that is
what many scheduling methods attempt to do.

Conclusion: Jobs are actors, not objects.
"""


class Traveller(object):
    def __init__(self, network, trips=None):
        """
        
        :param network: graph of the network 
        :param trips: 
        """
        self.network = network
        self.itinerary = []
        if trips is not None:
            self._add_trips(trips)

    def _add_trips(self, list_of_trips):
        """
        Helper for adding trips.
        :param list_of_trips: list of tuples. Each tuple must comply to
                              Trip.__init__()
        """
        assert isinstance(list_of_trips, list)
        for trip in list_of_trips:
            self.itinerary.append(Trip(network=self.network, *trip))


class Trip(object):
    def __init__(self, network, start, end, available=None, deadline=None, begin=None, complete=None, path=None):
        """
        :param network: graph of the network 
        :param start: start of the journey
        :param end: end of the journey
        :param a: _available_ to travel from this time.
        :param d: _deadline_ for arrival at destination
        :param b: _begin_ journey
        :param c: _complete_ journey

        Illustrated
        |------------------------------>  time
        |     A <----------------> D      available from - to deadline
        |               B <-----> C       valid schedule

        :param path: (optional) path for the journey (if not shortest path)
        """
        assert start in network
        assert end in network
        if path is None:
            self.path = network.shortest_path(start, end)
        else:
            self.path = path
        self.start = start
        self.end = end
        self.available = available  # available from
        self.begin = begin          # start
        self.complete = complete    # finish
        self.deadline = deadline    # latest arrival


class Shuttle(object):
    FILO = 1
    FIFO = 2

    def __init__(self, network, start, stops=None, capacity=float('inf'), order=None):
        """
        :param network: graph of the network
        :param start: a (location) node in the network.
        :param stops: Set of nodes to which this shuttle has access.
                      if `None`, then shuttle can stop at all nodes.
        :param capacity: the number of passengers that can board.
        :param order: the dis-/embarkation order for passengers. Options:
                      None: No ordering.
                      Shuttle.FILO: 1
                      Shuttle.FIFO: 2
        """
        assert isinstance(network, Graph)
        assert start in network
        self._current_location = start
        assert isinstance(stops, set)
        assert all([n in network for n in stops])
        if stops is None:
            stops = set(network.nodes())
        self.stops = stops
        self.itinerary = []

    def schedule(self, passengers):
        """
        :param jobs:
        :return:
        """


def schedule_all_trips(shuttles, travellers):
    """
    Iterative over the trains until a feasible schedule is found.

    1. Each device loop through the jobs:
        select all relevant jobs.
        create itinerary items on the jobs.
        when all itineraries are complete, return the schedule.

    """
    pass


def schedule(graph, start, jobs):
    """
    The best possible path is a circuit.
    First we'll find all circuits and attempt to remove them from
    the equation.

    Once no more circuits can be found, the best solution is to look for
    alternative combinations that provide improvement.

    :return:
    """
    new_schedule = []
    jobs_to_plan = jobs[:]
    while jobs_to_plan:
        circuit_path = find_perfect_circuit(graph=graph, start=start, jobs=jobs_to_plan)
        if circuit_path:
            job_sequence = jobs_from_path(circuit_path)
        else:  # circuit not possible.
            shortest_path = []
            shortest_distance = float('inf')
            for perm in itertools.permutations(jobs_to_plan, len(jobs_to_plan)):
                path = path_from_schedule(jobs=perm, start=start)
                distance = graph.distance_from_path(path)
                if distance < shortest_distance:
                    shortest_distance = distance
                    shortest_path = path
            job_sequence = jobs_from_path(shortest_path)
        # remove planned jobs from options:
        for job in job_sequence:
            if job in jobs_to_plan:
                jobs_to_plan.remove(job)
                new_schedule.append(job)
    return new_schedule


def jobs_from_path(path):
    """ helper for finding jobs from path"""
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


def path_from_schedule(jobs, start):
    """ The evaluation is based on building the travel path.
    For example in the network A,B,C with 4 trips as:
        1 (A,B), 2 (A,C), 3 (B,A), 4 (C,A)
    which have the travel path: [A,B,A,C,B,A,C,A]

    The shortest path for these jobs is: [A,C,A,B,A] which uses the order:
        2 (A,C), 4 (C,A), 1 (A,B), 3(B,A)
    """
    path = [start]
    for A, B in jobs:
        if A != path[-1]:
            path.append(A)
        path.append(B)
    return path


def find_perfect_circuit(graph, start, jobs):
    """ A perfect circuit is a path that starts and ends at the same place
    and where every movement includes a job.

    :param: start: starting location.
    :param: jobs: list of movements [(A1,B1), (A2,B2,) ....]
    :return path [A1,B1, ..., A1]
    """
    g = Graph()
    for A, B in jobs:
        try:
            g[A][B]
        except KeyError:
            d, p = graph.shortest_path(A, B)
            g.add_edge(A, B, d)

    new_starts = [B for A, B in jobs if A == start]
    for A in new_starts:
        _, p = g.breadth_first_search(A, start)  # path back to start.
        if p:
            return [start] + p
    return []




import numpy as np
from datetime import datetime
from random import choice
from random import seed


class Soluzione :
    def __init__(self, percorsi, camion, matrice_dist):
        self.routes = percorsi[0:len(percorsi)]
        self.truck_count = camion
        self.calcola_fitness(matrice_dist)

    def calcola_fitness(self,matrice):
        self.fitness = 0
        for n in range(len(self.routes) - 1):
            if self.routes[n].number != self.routes[n + 1].number :
                self.fitness += matrice[self.routes[n].number, self.routes[n + 1].number ]


class Algoritmo_genetico:
    def __init__(self, cvrptw_istance):
        self.istanza = cvrptw_istance            # Local CVRPTW istance
        self.popolazione = []

    def gen_popolazione_iniziale(self):
        unsorted_nodes = self.istanza.nodes
        due_dates = []
        for i in unsorted_nodes:
            due_dates.append(i.due_date)

        arg_sort = np.argsort(due_dates)
        nodes_left = []
        buff_truck = []
        routes_of_routes = []
        static_sorted = []
        for i in arg_sort:
            if i != 0:
                static_sorted.append(unsorted_nodes[i])

        current_node = 0
        t = 0
        remaining_capacity = self.istanza.capacity
        route = [unsorted_nodes[0]]
        j = 0

        #now = datetime.now().time().microsecond
        seed(1)

        for z in range(50):
            routes = []
            stop = 0
            truck_count = 0
            nodes_left = static_sorted[0:len(static_sorted)]
            buff_truck = static_sorted[0:len(static_sorted)]

            while stop == 0:
                if buff_truck:
                    if j % (z + 3) == 0:
                        next_node = choice(buff_truck)
                    else:
                        next_node = buff_truck[0]
                    if next_node.demand <= remaining_capacity and (
                            t + self.istanza.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        route.append(next_node)
                        buff_truck.remove(next_node)
                        nodes_left.remove(next_node)
                        remaining_capacity = remaining_capacity - next_node.demand
                        if (t + self.istanza.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                            t = next_node.rdy_time + next_node.service_time
                        else:
                            t = t + self.istanza.travel_times[current_node, next_node.number] + next_node.service_time
                        current_node = next_node.number
                        j = j + 1
                    else:
                        buff_truck.remove(next_node)
                else:
                    route.append(unsorted_nodes[0])
                    routes.append(route)
                    route = [unsorted_nodes[0]]
                    truck_count = truck_count + 1
                    t = 0
                    current_node = 0
                    remaining_capacity = self.istanza.capacity
                    if len(nodes_left) != 0:
                        buff_truck = nodes_left[0:len(nodes_left)]
                    else:
                        stop = 1

            temp = []
            for r in routes:
                temp.extend(r)
            routes_of_routes.extend(temp)
            self.popolazione.append(Soluzione(routes_of_routes, truck_count, self.istanza.distances))
            routes_of_routes = []


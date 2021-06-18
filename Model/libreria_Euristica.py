import numpy as np
from datetime import datetime
from random import choice
from random import seed


class Euristica:
    def __init__(self, cvrptw_istance):
        self.istanza = cvrptw_istance            # Local CVRPTW istance

    def calcola_soluzioni(self):
        unsorted_nodes = self.istanza.nodes
        due_dates = []
        for i in unsorted_nodes:
            due_dates.append(i.due_date)

        arg_sort = np.argsort(due_dates)
        # print(arg_sort)
        nodes_left = []
        buff_truck = []
        static_sorted = []
        for i in arg_sort:
            if i != 0:
                static_sorted.append(unsorted_nodes[i])

        current_node = 0
        t = 0
        remaining_capacity = self.istanza.capacity
        routes_of_routes = []
        obj_values = []
        trucks_count = []
        route = [0]
        j = 0

        now = datetime.now().time().microsecond
        seed(now)

        for z in range(50):
            routes = []
            stop = 0
            truck_count = 0
            for k in static_sorted:
                nodes_left.append(k)
                buff_truck.append(k)

            while stop == 0:
                if buff_truck:
                    if j % (z + 3) == 0:
                        next_node = choice(buff_truck)
                    else:
                        next_node = buff_truck[0]
                    if next_node.demand <= remaining_capacity and (
                            t + self.istanza.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        route.append(next_node.number)
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
                    route.append(0)
                    routes.append(route)
                    route = [0]
                    truck_count = truck_count + 1
                    t = 0
                    current_node = 0
                    remaining_capacity = self.istanza.capacity
                    if len(nodes_left) != 0:
                        for i in nodes_left:
                            buff_truck.append(i)
                    else:
                        stop = 1
            val_f_ob = 0
            for r in routes:
                # print(r)
                for n in range(len(r) - 1):
                    val_f_ob = val_f_ob + self.istanza.distances[r[n], r[n + 1]]

        routes_of_routes.append((routes[:], routes[0]))
        trucks_count.append(truck_count)
        obj_values.append(val_f_ob)

        return routes_of_routes, trucks_count, obj_values
"""""
            print(z + 1, "---> Truck : [ ", truck_count, " ]\n")
            if truck_count > self.istanza.num_vehicle:
                print("**************************************** TROPPI CAMION ***********************************",
                      "\n")
                return 0
            print("Valore funzione obiettivo : ", val_f_ob, "\n")
"""""





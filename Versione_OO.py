import library_CVRPTW as lib
import numpy as np
from datetime import datetime
from random import choice
from random import randint
from random import seed
"""
import gurobipy as gb
from gurobipy import *
import re
from random import *
import matplotlib.pyplot as plt
import networkx as nx
#plt.rcParams["figure.figsize"] = (20,10)
"""


file = "VRPTW-Instances/Solomon/C101.txt"
istanza = lib.CVRPTW(file)
soluzione = istanza.optimize()
#istanza.print_solution(soluzione[0])

#-------------------------------- Generazione della popolazione di soluzioni iniziali ----------------------------------

unsorted_nodes = istanza.nodes
due_dates = []
for i in unsorted_nodes:
    due_dates.append(i.due_date)

arg_sort = np.argsort(due_dates)
#print(arg_sort)
nodes_left =[]
buff_truck = []
static_sorted = []
for i in arg_sort:
    if i != 0:
        static_sorted.append(unsorted_nodes[i])

current_node = 0
t = 0
remaining_capacity = istanza.capacity
routes = []
route = [0]
j = 0

now = datetime.now().time().microsecond
seed(now)

for z in range(50) :
    routes = []
    stop = 0
    truck_count = 0
    for k in static_sorted:
        nodes_left.append(k)
        buff_truck.append(k)

    while stop == 0:
        if buff_truck:
            if j%(z+3) == 0:
                next_node = choice(buff_truck)
            else:
                next_node = buff_truck[0]
            if next_node.demand <= remaining_capacity  and  (t + istanza.travel_times[current_node, next_node.number]) <= next_node.due_date :
                route.append(next_node.number)
                buff_truck.remove(next_node)
                nodes_left.remove(next_node)
                remaining_capacity = remaining_capacity - next_node.demand
                if (t + istanza.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                    t = next_node.rdy_time + next_node.service_time
                else:
                    t = t + istanza.travel_times[current_node, next_node.number] + next_node.service_time
                current_node = next_node.number
                j = j+1
            else:
                buff_truck.remove(next_node)
        else:
            route.append(0)
            routes.append(route)
            route = [0]
            truck_count = truck_count+1
            t = 0
            current_node = 0
            remaining_capacity = istanza.capacity
            if len(nodes_left) != 0:
                for i in nodes_left:
                    buff_truck.append(i)
            else:
                stop = 1
    val_f_ob = 0
    for r in routes:
        print(r)
        for n in range(len(r)-1):
            val_f_ob = val_f_ob + istanza.distances[r[n], r[n+1]]

    print(z+1,"---> Truck : [ ",truck_count," ]\n")
    if truck_count > istanza.num_vehicle:
        print("**************************************** TROPPI CAMION ***********************************","\n")
    print("Valore funzione obiettivo : ", val_f_ob, "\n")

"""    
Graph2 = lib.nx.DiGraph()
list_nodes = list(range(istanza.num_nodes))
Graph2.add_nodes_from(list_nodes)
for route in routes:
        for j in range(len(route)-1):
            Graph2.add_edge(route[j], route[j+1])

coordinate = {}
for i in range(istanza.num_nodes):
    coordinate[i] = istanza.nodes[i].coordinate

lib.nx.draw_networkx(Graph2, coordinate, font_size=8, font_color='k', node_color='green', edgecolors='k',
                 node_size=200)
lib.nx.draw_networkx_edges(Graph2, coordinate, arrowsize=7, arrowstyle='->', edge_color='black')
#lib.plt.show()

#istanza.print_solution(soluzione[0])
"""
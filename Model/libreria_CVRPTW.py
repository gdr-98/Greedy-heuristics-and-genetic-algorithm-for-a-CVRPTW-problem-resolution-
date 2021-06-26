import gurobipy as gb
from gurobipy import *
import re
import matplotlib.pyplot as plt
import networkx as nx

# plt.rcParams["figure.figsize"] = (20,10)

# ****************************************************** CLASSI ********************************************************


class Node:
    def __init__(self, number, coordinate, demand, rdy_time, due_date, serv_time):
        self.number = number
        self.coordinate = coordinate
        self.demand = demand
        self.rdy_time = rdy_time
        self.due_date = due_date
        self.service_time = serv_time
# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo della distanza dal nodo passato come parametro
    def distance(self, node):
        i = self.coordinate
        j = node.coordinate
        diff = (i[0] - j[0], i[1] - j[1])
        return math.sqrt(diff[0] * diff[0] + diff[1] * diff[1])

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo della tempo di viaggio per arrivare nel nodo passato come parametro
    def travel_time(self, node):
        return round(self.distance(node), 1)

# ----------------------------------------------------------------------------------------------------------------------
    # Overload della print
    def __str__(self):
        return "\n" + "Numero nodo : " + str(self.number) + "\n" + "Coordinate : " \
               + str(self.coordinate) + "\n" + "Domanda : " + str(self.demand) + "\n" + "Ready time : " + \
               str(self.rdy_time)  + "\n" + "Due date : " + str(self.due_date) + "\n" + "Tempo di servizio : " + \
               str(self.service_time) + "\n"


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class CVRPTW:
    def __init__(self, file_name):
        self.nodes_num = 0
        self.nodes = []
        self.name_instance = 'nome_istanza'
        self.num_vehicle = 0
        self.capacity = 0


        f = open(file_name, "r")
        line = f.readline()
        line.strip("\n")
        self.name_instance = line

        for i in range (3) :
            line = f.readline()   #Salto 3 linee

        line = f.readline()
        data = re.findall(r"[-+]?\d.\d+|\d+", line)
        self.num_vehicle = int(data[0])
        self.capacity = int(data[1])

        for i in range(4):
            line = f.readline()  #Salto altre 4 linee

        line = f.readline()
        while not line.startswith("EOF"):
            data = re.findall(r"[-+]?\d.\d+|\d+", line)
            coordinate = (int(data[1]), int(data[2]))
            demand = int(data[3])
            rdy_time = int(data[4])
            due_date = int(data[5])
            serv_time = int(data[6])
            self.nodes.append(Node(self.nodes_num, coordinate, demand, rdy_time, due_date, serv_time))
            self.nodes_num = self.nodes_num + 1
            line = f.readline()
        f.close()

        self.calculate_distances()
        self.calculate_travel_times()

# ----------------------------------------------------------------------------------------------------------------------
    # Overload della print
    def __str__(self):
        return "\n" + "Nome istanza : " + self.name_instance + "Numero nodi : " + str(self.nodes_num) \
               + "\n" + "Numero massimo di camion : " + str(self.num_vehicle) + "\n" + "Capacità camion : " \
               + str(self.capacity) + "\n"

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo della matrice di distanze : elemento i,j --> distanza tra i e j
    def calculate_distances(self):
        self.distances = {(i, j): self.nodes[i].distance(self.nodes[j]) for i in range(self.nodes_num) for j in
                          range(self.nodes_num) if i != j}

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo della matrice dei tempi di viaggio (stessa struttura della matrice di distanze)
    def calculate_travel_times(self):
        self.travel_times = {(i, j): round(self.distances[i, j], 1) for i in range(self.nodes_num) for j in
                             range(self.nodes_num) if i != j}

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo delle liste di percorsi a partire dal vettore di variabili x_ij (x_ij = 1 se l'arco da i a j è utilizzato
    # da un camion
    def calculate_routes_from_model(self, x):
        node = []
        for i in range(1, self.nodes_num):
            if x[0, i] > 0:
                node.append(i)

        route = []
        self.routes = []
        for k in node:
            next = k
            route.append(k)
            stop = 1
            while stop:
                for i in range(self.nodes_num):
                    if i == 0 and x[next, i] == 1:
                        stop = 0
                    elif x[next, i] == 1:
                        route.append(i)
                        next = i

            self.routes.append(route)
            route = []

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo della soluzione ottima attraverso il solutore Gurobi
    def optimize(self):

        mod = gb.Model('CVRP')
        x = mod.addVars(range(self.nodes_num), range(self.nodes_num), vtype=GRB.BINARY, name="X")
        u = mod.addVars(range(self.nodes_num), vtype=GRB.INTEGER, name="U")
        a = mod.addVars(range(self.nodes_num), vtype=GRB.INTEGER, name="A")

        mod.addConstrs((gb.quicksum(x.select(i, '*')) - gb.quicksum(x.select('*', i)) == 0 for i in range(self.nodes_num)), "Trasporto")
        mod.addConstr(gb.quicksum(x.select(0, '*')) <= self.num_vehicle, "NumeroVeicoli")
        mod.addConstrs((gb.quicksum(x.select(i, '*')) == 1 for i in range(1, self.nodes_num)), "VeicoliCliente")
        mod.addConstr((u[0] == 0), "DomandaIniziale")
        mod.addConstrs((u[i] <= self.capacity for i in range(self.nodes_num)), "CapacitàMassima")
        mod.addConstrs((u[j] - u[i] >= self.nodes[j].demand * x[i, j] - self.capacity * (1 - x[i, j]) for i in range(self.nodes_num) for j in
                        range(self.nodes_num) if i != j and j != 0), "Sottogiri&capacità")
        mod.addConstrs((x[i, i] == 0 for i in range(self.nodes_num)), "ArchiRicorsivi")
        mod.addConstrs((a[j] >= (a[i] + self.nodes[i].service_time + self.travel_times[i,j]) - self.nodes[0].due_date * (1 - x[i, j]) for i in
                        range(self.nodes_num) for j in range(1, self.nodes_num) if i != j), "FinestreTemporali1")
        mod.addConstrs((a[j] <= self.nodes[j].due_date for j in range(self.nodes_num)), "FinestreTemporali2")
        mod.addConstrs((a[j] >= self.nodes[j].rdy_time for j in range(self.nodes_num)), "FinestreTemporali3")
        mod.addConstr((a[0] == 0), "FinestreTemporali4")
        mod.addConstrs(((a[i] + self.nodes[i].service_time + self.travel_times[i, 0]) <= 10000 * (1 - x[i, 0]) + self.nodes[0].due_date * x[i, 0] for i in
                        range(1, self.nodes_num)), "FinestreTemporali5")

        obj = (gb.quicksum(self.distances[i, j] * x[i, j] for i in range(self.nodes_num) for j in range(self.nodes_num) if i != j))
        mod.setObjective(obj, GRB.MINIMIZE)
        mod.optimize()

        X = mod.getAttr('x', x)
        U = mod.getAttr('x', u)
        A = mod.getAttr('x', a)

        return [X,U,A]

# ----------------------------------------------------------------------------------------------------------------------
    # Stampa del grafico archi-nodi della soluzione
    def print_solution(self, x_solution):

        Graph = nx.DiGraph()
        list_nodes = list(range(self.nodes_num))
        Graph.add_nodes_from(list_nodes)
        for i in range(self.nodes_num):
            for j in range(self.nodes_num):
                if i != j and x_solution[i, j] == 1:
                    Graph.add_edge(i, j)

        coordinate = {}
        for i in range(self.nodes_num):
            coordinate[i] = self.nodes[i].coordinate

        nx.draw_networkx(Graph, coordinate, font_size=8, font_color='k', node_color='green', edgecolors='k',
                         node_size=300)
        nx.draw_networkx_edges(Graph, coordinate, arrowsize=7, arrowstyle='->', edge_color='black')
        # nx.draw_networkx_labels(Graph,coordinate,labels= dict_dem, font_color ='k', horizontalalignment=
        # 'left',verticalalignment='bottom')
        plt.show()

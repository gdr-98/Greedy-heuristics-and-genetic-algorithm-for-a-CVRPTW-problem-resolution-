import gurobipy as gb
from gurobipy import *
import re
from random import *
import matplotlib.pyplot as plt
import networkx as nx

def distance(city1, city2):
    i = coordinate[city1]
    j = coordinate[city2]
    diff = (i[0]-j[0], i[1]-j[1])
    return math.sqrt(diff[0]*diff[0]+diff[1]*diff[1])

num_nodes = 100

#********************************************************* Lettura file ************************************************
f = open("VRPTW-Instances/Solomon/C101.txt", "r")
for i in range(4) :
    line = f.readline()    #   | Salto le prime 4 linee

line = f.readline()
data  = re.findall(r"[-+]?\d*\.\d+|\d+", line)

num_vehicle = int(data[0])
capacity = int(data[1])
for i in range(4) :
    line = f.readline()    #   | Salto altre 4 linee

demand = []
time_window = {}
coordinate = {}
serv_time = []

for i in range(num_nodes) :
    line = f.readline()
    data = re.findall(r"[-+]?\d*\.\d+|\d+", line)
    coordinate[i] = (int(data[1]), int(data[2]))
    demand.append(int(data[3]))
    time_window[i] = (int(data[4]), int(data[5]))
    serv_time.append(int(data[6]))
f.close()
"""
x = []
y = []
for i in range(num_nodes) :
    x.append(coordinate[i][0])
    y.append(coordinate[i][1])
plt.scatter(x,y)
plt.show()
"""

dist = {(i,j): distance(i, j) for i in range(num_nodes) for j in range(num_nodes) if i != j }
travel_time = {(i,j): round(dist[i,j],1) for i in range(num_nodes) for j in range(num_nodes) if i != j}

#****************************************** Modellazione *****************************************************************
mod = gb.Model('CVRP')
x = mod.addVars(range(num_nodes), range(num_nodes),vtype=GRB.BINARY, name="X")
u = mod.addVars(range(num_nodes),vtype=GRB.INTEGER, name="Y")
a = mod.addVars(range(num_nodes),vtype=GRB.INTEGER, name="A")

mod.addConstrs((gb.quicksum(x.select(i,'*')) - gb.quicksum(x.select('*',i))  == 0 for i in range(num_nodes)), name="Trasporto")
mod.addConstr(gb.quicksum(x.select(0,'*')) == num_vehicle, name="NumeroVeicoli")
mod.addConstrs((gb.quicksum(x.select(i,'*')) == 1 for i in range(1,num_nodes)), name="VeicoliCliente")
mod.addConstr(u[0] == 0, name="DomandaIniziale")
mod.addConstrs((u[i] <= capacity for i in range(num_nodes)), "CapacitàMassima")
mod.addConstrs((u[j] - u[i] >= demand[j]*x[i,j] - capacity*(1-x[i,j]) for i in range(num_nodes) for j in range(num_nodes) if i!=j and j!=0), name = "sottogiri&capacità")
mod.addConstrs((x[i,i] == 0 for i in range (num_nodes)), "ArchiRicorsivi")
mod.addConstrs((a[j] >= (a[i] + serv_time[i] + travel_time[i,j]) - time_window[0][1]*(1 - x[i,j]) for i in range(num_nodes) for j in range(1,num_nodes) if i!=j), "TimeWindows1")
mod.addConstrs((a[j] <= time_window[j][1] for j in range(num_nodes)), "TimeWindows2")
mod.addConstrs((a[j] >= time_window[j][0] for j in range(num_nodes)), "TimeWindows3")
mod.addConstr((a[0] == 0) , "TimeWindows4")
mod.addConstrs(((a[i] + serv_time[i] + travel_time[i,0]) <= 10000*(1-x[i,0]) + time_window[0][1]*x[i,0] for i in range(1,num_nodes)), "TimeWindows5")

obj = (gb.quicksum(dist[i,j]*x[i,j] for i in range(num_nodes) for j in range(num_nodes) if i!=j))
mod.setObjective(obj, GRB.MINIMIZE)
mod.optimize()

"""
U = mod.getAttr('x', u)
print(U)

A = mod.getAttr('x', a)
print(A)


X = mod.getAttr('x',x)
for i in range(num_nodes) :
    for j in range(num_nodes):
        if X[i,j] == 1 :
            print("(%g,%g) : %g" %(i,j,X[i,j]))
"""

Graph = nx.DiGraph()
list_nodes = list(range(num_nodes))
Graph.add_nodes_from(list_nodes)
for i in range(num_nodes):
    for j in range(num_nodes) :
        if i!=j and x[i,j].x == 1 :
            Graph.add_edge(i,j)

dict_dem = {}
for i in range(num_nodes) :
    dict_dem[i] = demand[i]


# Draw the nodes
nx.draw_networkx(Graph,coordinate, font_size = 10,font_color ='k' , node_color = 'green',edgecolors ='k', node_size=300)
# Draw the edges
nx.draw_networkx_edges(Graph, coordinate,edge_color= 'black')
# Show the plot
#nx.draw_networkx_labels(Graph,coordinate,labels= dict_dem, font_color ='k', horizontalalignment='left',verticalalignment='bottom')
#plt.show()

X = mod.getAttr('x', x)
    #for i in range(num_nodes):
      #  for j in range(num_nodes) :
       #     if X[i,j] > 0 :\n",
           #     print('X(%s,%s) = %g' % (i, j, X[i,j]))

node = []
for i in range(1,num_nodes):
    if X[0,i]>0:
        node.append(i)

route = []
routes = []
for k in node:
    next = k
    route.append(k)
    stop = 1
    while stop:
        for i in range(num_nodes):
            if i==0 and X[next,i] == 1:
                stop = 0
            elif X[next,i] == 1:
                route.append(i)
                next = i

    routes.append(route)
    route = []

for i in range(len(routes)) :
    print(routes[i])
    print("\n")
plt.show()

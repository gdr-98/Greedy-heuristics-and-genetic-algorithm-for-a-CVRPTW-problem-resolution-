from librerie import libreria_Alg_Genetico as gen, libreria_CVRPTW as lib

file = "..\Solomon\C101.txt"
istanza = lib.CVRPTW(file)



# ---------------------------Generazione della popolazione di soluzioni iniziali ------------------------------

def main():

    # soluzione = istanza.optimize()
    test = gen.Algoritmo_genetico(istanza)
    popolazione = test.gen_popolazione_iniziale()

    print(popolazione[0].valore_f_ob)
    print(popolazione[49].valore_f_ob)
    i = 0
    for _ in range(50):
        (sol1, sol2) = test.test()
        sol1.is_admissible()
        sol2.is_admissible()
        if sol1.truck_count <= 25 :
            print(i+1, " ", sol1.valore_f_ob, " : ", sol1.truck_count, "||| ", sol2.valore_f_ob, " : ", sol2.truck_count)
            i += 1


if __name__ == "__main__":
    main()

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

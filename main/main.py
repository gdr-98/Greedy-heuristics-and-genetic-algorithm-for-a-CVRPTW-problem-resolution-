import library_CVRPTW as lib
import library_euristica as eur

file = "C101.txt"
istanza = lib.CVRPTW(file)
# soluzione = istanza.optimize()
# istanza.print_solution(soluzione[0])

# ---------------------------Generazione della popolazione di soluzioni iniziali ------------------------------


def main():
    test = eur.Euristica(istanza)
    percorsi = []
    tracks = []
    obj_val = []
    percorsi, tracks, obj_val= test.calcola_soluzioni()

    print("Percorsi:")
    print(percorsi)
    print("Tracks:")
    print(tracks)
    print ("obj_val:")
    print(obj_val)


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

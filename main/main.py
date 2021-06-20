import time
import random
from Libraries import library_euristica as eur, library_CVRPTW as lib

file = "C101.txt"
istanza = lib.CVRPTW(file)


def BCRC(soluzione1, soluzione2, range):

    # Seed per le funzioni randomiche
    random.seed(time.time())

    # Si rimuove il deposito dai genitori
    soluzione1.routes = [i for i in soluzione1.routes if i.number != 0]
    soluzione2.routes = [i for i in soluzione2.routes if i.number != 0]

    # Si prendono due indici casuali in un range predefinito
    index1 = random.randint(0, len(soluzione1.routes)-range)
    index2 = random.randint(index1, index1+range)

    # Si costruiscono i tagli sulla base dei due indici casuali
    list1 = soluzione1.routes[index1:index2]
    list2 = soluzione2.routes[index1:index2]

    # Si rimuovono le liste dai genitori
    for j in list2:
        soluzione1.routes = [i for i in soluzione1.routes if i.number != j.number]

    for j in list1:
        soluzione2.routes = [i for i in soluzione2.routes if i.number != j.number]

    # Si calcolano le distanze dei nodi nel parente 1 per ogni nodo nella lista 2
    results = []
    # Dizionario del tipo:
    # Key -> Numero di ogni nodo i-esimo
    # Valore -> distanza calcolata del nodo i-esimo di parent dal nodo j-esimo di lista
    distances_from_list2 = {}
    for j in list2:
        temp = []
        for i in soluzione1.routes:
            # Si calcolano le distanze per ogni nodo j ed i
            distances_from_list2[i.number] = (soluzione1.istanza.nodes[j.number].distance(soluzione1.istanza.nodes[i.number]))
        # Si prende la chiave associata al minimo di queste distanze per capire dove inserire il nodo j di list2
        temp = min(distances_from_list2.values())
        # Si ha la lista dei nodi più vicini, possono essere più di uno
        results = ([key for key in distances_from_list2 if distances_from_list2[key] == temp])
        # Bisogna ora trovare l'indice del minimo. Se ce n'è più di uno, se ne sceglie uno soltanto randomicamente
        indice = 0
        for i in soluzione1.routes:
            if i.number == results[random.randint(0, len(results)-1)]:
                indice = soluzione1.routes.index(i)
                break
        # Si inserisce il minimo all'indice calcolato
        soluzione1.routes.insert(indice+1, j)

    results = []
    distances_from_list1 = {}
    for j in list1:
        temp = []
        for i in soluzione2.routes:
            distances_from_list1[i.number] = (soluzione2.istanza.nodes[j.number].distance(soluzione2.istanza.nodes[i.number]))
        temp = min(distances_from_list1.values())
        results = ([key for key in distances_from_list1 if distances_from_list1[key] == temp])
        for i in soluzione2.routes:
            if i.number == results[random.randint(0, len(results) - 1)]:
                indice = soluzione2.routes.index(i)
                break
        soluzione2.routes.insert(indice+1, j)

    return soluzione1, soluzione2


def main():
    test = eur.Algoritmo_genetico(istanza)
    test.gen_popolazione_iniziale()

    soluzione1 = test.popolazione[random.randint(0, len(test.popolazione))]
    soluzione2 = test.popolazione[random.randint(0, len(test.popolazione))]


    for i in range(0, 4):
        crossover1, crossover2 = (BCRC(soluzione1, soluzione2, 20))

        if crossover1.is_admissible() and crossover2.is_admissible():
            print("Crossover ammissibili")
        else:
            print("Crossover inammissibili")


if __name__ == "__main__":
    main()

from librerie import libreria_Alg_Genetico as gen, libreria_CVRPTW as lib

file = "..\Solomon\C101.txt"
istanza = lib.CVRPTW(file)

# ---------------------------Generazione della popolazione di soluzioni iniziali ------------------------------

def main():

    # soluzione = istanza.optimize()
    test = gen.Algoritmo_genetico(istanza)
    popolazione = test.gen_popolazione_iniziale()
    best = test.best_solution()

    best = test.start_algorithm()
    for i in test.popolazione:
        print(i.valore_f_ob )
    print(best)

if __name__ == "__main__":
    pass
main()

"""    

best = gen.Soluzione([istanza.nodes[1],istanza.nodes[2],istanza.nodes[4],istanza.nodes[5],istanza.nodes[6],istanza.nodes[7]], istanza, 0)
    worst = gen.Soluzione([istanza.nodes[7], istanza.nodes[1], istanza.nodes[6], istanza.nodes[2], istanza.nodes[4], istanza.nodes[5]],istanza, 0)
    son1,son2 = test.double_crossover(best,worst,4)

    genitore_1 = [i.number for i in best.routes]
    genitore_2 = [i.number for i in worst.routes]

    print("Genitore 1 :",genitore_1)
    print("Genitore 2 :", genitore_2)

    lista_nodi1 = [i.number for i in son1.routes]
    lista_nodi2 = [i.number for i in son2.routes]

    print("Sol 1 : ", lista_nodi1)
    print("Sol 2 : ", lista_nodi2)
    visto = []
    for i in lista_nodi1:
        if i in visto:
            print("*****************ERRORE : ", i)

        else:
            visto.append(i)
    print(visto)
    visto = []

    for i in lista_nodi2:
        if i in visto:
            print("*****************ERRORE : ", i)
        else:
            visto.append(i)
    print(visto)

"""

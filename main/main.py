from librerie import libreria_Alg_Genetico as gen, libreria_CVRPTW as lib
import time
import networkx as nx
import matplotlib.pyplot as plt
file = "..\Homberger\C1_2_1.TXT"
#file = "..\Homberger\R1_2_1.TXT"
#file = "..\Homberger\RC1_2_1.TXT"
#file = "..\Solomon\C101.txt"
#file = "..\Solomon\R101.txt"
#file = "..\Solomon\RC101.txt"

istanza = lib.CVRPTW(file)

def main():

    #print(istanza)
    #X,U,A= istanza.optimize()
    #istanza.calculate_routes_from_model(X)
    #for i in istanza.routes:
       # print(i)
    #istanza.print_solution(X)

    print("Soluzione Euristica")
    test = gen.Algoritmo_genetico(istanza)
    #start = time.time()
    #popolazione = test.Gen_starting_population_MDPDF(50, 100)
    #popolazione = test.Gen_starting_population_NF(50, 150)
    #popolazione = test.Gen_starting_population_EDF(50, 150)

    popolazione= []
    limit = 3800
    while limit > 3600:
        popolazione =[]
        test.population = []
        popolazione = test.Gen_starting_population_MDPDF(50, 50)
        best = test.Best_solution()
        limit = best.obj_fun_value
        print(limit)
    print("Soluzione accettabile")
    #for i in popolazione:
     #   print(i.obj_fun_value)
    #end = time.time()
    #best = test.Best_solution()
    #print(best.obj_fun_value, " Ammissibile : ", best.admissible)
    #print("\nTempo impiegato per generare la popolazione : ", end-start)

    dim_crossover = [10, 20, 40, 50]
    mut_prob = [0.05, 0.1, 0.2]
    dim_mut = [5, 10, 15]

    sol_list = []
    for c in dim_crossover:
        for m in mut_prob:
            for d_m in dim_mut:
                buff_list = []
                print("Probabilità mutazione : ", m, "|| Dimensione mutazione : ", d_m, "|| Dimensione crossover : ", c)
                for k in range(3):
                    test.population[0:len(popolazione)] = popolazione[0:len(popolazione)]
                    best = test.Start_algorithm(750, m, d_m, c)
                    buff_list.append(best)
                minimo = min(buff_list, key=lambda item: item.obj_fun_value)
                print("Soluzione migliore : ", minimo.obj_fun_value)
                sol_list.append(minimo)

    migliore = min(sol_list, key=lambda item: item.obj_fun_value)
    print("Migliore soluzione trovata : ", migliore.obj_fun_value)
    test.Graph_solution(migliore)

if __name__ == "__main__":
    main()

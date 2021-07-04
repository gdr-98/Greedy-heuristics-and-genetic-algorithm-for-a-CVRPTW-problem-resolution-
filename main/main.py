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
    popolazione = test.Gen_starting_population_EDF(50, 150)

    #for i in popolazione:
     #   print(i.obj_fun_value)
    #end = time.time()
    best = test.Best_solution()
    print(best.obj_fun_value, " Ammissibile : ", best.admissible)
    #print("\nTempo impiegato per generare la popolazione : ", end-start)
    best = test.Start_algorithm(30, 600, 0.2, 5, 30)
    #k = 0
    #for i in popolazione:
        #k += 1
        #print(k, " : ", i.obj_fun_value)
    print(best)
    #test.Graph_solution(best)

if __name__ == "__main__":
    main()

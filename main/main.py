from librerie import libreria_Alg_Genetico as gen, libreria_CVRPTW as lib
import networkx as nx
import matplotlib.pyplot as plt
#file = "..\Homberger\C1_2_1.TXT"
#file = "..\Homberger\R1_2_1.TXT"
#file = "..\Homberger\RC1_2_1.TXT"
#file = "..\Solomon\C101.txt"
#file = "..\Solomon\R101.txt"
file = "..\Solomon\RC101.txt"

istanza = lib.CVRPTW(file)

def main():

    print(istanza)
    #X,U,A= istanza.optimize()
    #istanza.print_solution(X)
    test = gen.Algoritmo_genetico(istanza)
    #popolazione = test.Gen_starting_population_MDPDF(20, 5)
    #popolazione = test.Gen_starting_population_NF(50, 5)
    popolazione = test.Gen_starting_population_EDF(50, 5)
    #for i in popolazione:
     #   print(i.obj_fun_value)

    best = test.Best_solution()
    print(best)
    #print(best,"Indice soluzione : ", test.population.index(best))
    best = test.Start_algorithm(20, 0, 0.01, 10, 80)

    for i in popolazione:
        print(i.obj_fun_value)
    print(best)
    #test.Graph_solution(best)

if __name__ == "__main__":
    pass
main()

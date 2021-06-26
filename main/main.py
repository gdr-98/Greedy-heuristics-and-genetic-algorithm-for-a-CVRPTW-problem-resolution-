from librerie import libreria_Alg_Genetico as gen, libreria_CVRPTW as lib

file = "..\Homberger\C1_2_1.TXT"
#file = "..\Solomon\C101.txt"
istanza = lib.CVRPTW(file)

# ---------------------------Generazione della popolazione di soluzioni iniziali ------------------------------

def main():

    print(istanza)
    #X,U,A= istanza.optimize()
    #istanza.print_solution(X)
    test = gen.Algoritmo_genetico(istanza)
    popolazione = test.Gen_starting_population_NF_EDF(50,5)
    #popolazione = test.Gen_starting_population_NF(50, 5)
    #popolazione = test.Gen_starting_populationEDF(50, 5)
    best = test.Best_solution()
    print(best)
    best = test.Start_algorithm(10, 200, 0.3, 5, 20)

    for i in popolazione:
        print(i.obj_fun_value)
    print(best)
    #test.Graph_solution(best)


if __name__ == "__main__":
    pass
main()

import numpy as np
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import time
import random
from random import choice
from random import seed



# ****************************************************** CLASSI ********************************************************


class Solution:
    def __init__(self, routes_row, cvrptw_instance, trucks=0):
        self.instance = cvrptw_instance
        self.routes = routes_row[0:len(routes_row)]
        self.truck_count = trucks
        self.obj_fun_value = self.Compute_obj_fun_value(cvrptw_instance.distances)
        self.fitness = 1/self.obj_fun_value
        self.admissible = 1

# ----------------------------------------------------------------------------------------------------------------------
    # Calcolo del valore della funzione obiettivo per la soluzione in questione
    def Compute_obj_fun_value(self, distances_matrix):
        obj_fun_val = 0
        for n in range(len(self.routes) - 1):
            if self.routes[n].number != self.routes[n + 1].number :
                obj_fun_val += distances_matrix[self.routes[n].number, self.routes[n + 1].number]
        return obj_fun_val

# ----------------------------------------------------------------------------------------------------------------------
    # Verifica dell'ammissibilità della funzione
    def Is_admissible(self):
        # Attenzione!
        # Funziona solo con Solution da cui è stato rimosso il deposito (nodo 0)
        # Se bisogna usarla per soluzioni con 0, è necessario inserire un controllo all'inizio
        current_time = 0
        truck_number = 0
        current_node = 0
        self.routes.insert(current_node, self.instance.nodes[0])
        remaining_capacity = self.instance.capacity
        nodes_checked_count = 0

        i = 1
        # Per ogni nodo di routes
        while nodes_checked_count < self.instance.nodes_num - 1:
            # Current_node -> deposito fittizio
            # next_node -> routes[i] per i che parte da 0
            next_node = self.routes[i]

            # Verifica vincoli di capacità e temporali
            if next_node.demand <= remaining_capacity and (
                    current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.due_date:
                remaining_capacity = remaining_capacity - next_node.demand
                if (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                    current_time = next_node.rdy_time + next_node.service_time
                else:
                    current_time = current_time + self.instance.travel_times[current_node, next_node.number] + next_node.service_time
                # Se è tutto ok, si incrementano current_node e next_node
                current_node = next_node.number
                i += 1
                nodes_checked_count += 1
            # Altrimenti:
            # truck_number ++ -> parte un nuovo camion, se ne incrementa il conteggio
            # current_time = 0 -> si resetta il tempo, partendo da un nuovo deposito
            # si resetta la capacità
            # current_node = 0 -> nuovo deposito fittizio
            else:
                truck_number += 1
                self.routes.insert(i, self.instance.nodes[0])
                current_time = 0
                i += 1
                remaining_capacity = self.instance.capacity
                current_node = 0

        # Condizione di ammissibilità = numero di camion minore al numero consentito
        self.routes.append(self.instance.nodes[0])
        truck_number += 1

        if truck_number > self.instance.num_vehicle:
            admissible = 1
            self.admissible = 0
            self.truck_count = truck_number
            self.obj_fun_value = self.Compute_obj_fun_value(self.instance.distances) + 100*(truck_number - self.instance.num_vehicle)
            self.fitness = 1/self.obj_fun_value

        else:
            self.truck_count = truck_number
            self.obj_fun_value = self.Compute_obj_fun_value(self.instance.distances)
            self.fitness = 1/self.obj_fun_value
            self.admissible = 1
            admissible = 1

        return admissible

# ----------------------------------------------------------------------------------------------------------------------
    # Overload della funzione di print
    def __str__(self):
        print("Routes : ")
        for i in range(len(self.routes)):
            if i == 0 or self.routes[i].number != 0:
                print(self.routes[i].number, end=", ")
            else:
                print("0")
        return "\n" + "Valore funzione obiettivo : " + str(self.obj_fun_value) + "\n" + "Numero Camion : " \
               + str(self.truck_count) + "\n" + "Ammissibile : " + str(self.admissible) + "\n"

# ----------------------------------------------------------------------------------------------------------------------
    # Overload della stampa per console
    def __repr__(self):
        return self.__str__(self)

# ----------------------------------------------------------------------------------------------------------------------
    # Sovrascrittura dell'istanza
    def Copy(self, solution_to_Copy):
        self.instance = solution_to_Copy.instance
        self.routes = solution_to_Copy.routes[0:len(solution_to_Copy.routes)]
        self.truck_count = solution_to_Copy.truck_count
        self.obj_fun_value = solution_to_Copy.obj_fun_value
        self.fitness = solution_to_Copy.fitness
        self.admissible = solution_to_Copy.admissible


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Algoritmo_genetico:
    def __init__(self, cvrptw_istance):
        self.instance = cvrptw_istance            # Local CVRPTW istance
        self.population = []

# ----------------------------------------------------------------------------------------------------------------------
    # Generazione della popolazione iniziale di soluzioni ordinando per somma : deadline+tempo di spostamento
    def Gen_starting_population_MDPDF(self, pop_dim = 50, randomness = 10):

        # Salvataggio della lista di nodi del grafo (non ordinata)
        unsorted_nodes = self.instance.nodes[0:self.instance.nodes_num]

        # Inizializzazione variabili
        current_node = 0            # Ultimo nodo aggiunto al percorso corrente  (si parte sempre dal nodo deposito)
        current_time = 0            # Tempo trascorso per arruvare al current_node
        remaining_capacity = self.instance.capacity     # Capacità rimanente del camion (il camion parte con capacità massima)
        route = [self.instance.nodes[0]]             # Percorso del camion che si sta analizzando (un camion parte sempre dal deposito)
        j = 0                       # "j" serve alla scelta casuale che renderà le soluzioni eterogenee

        now = datetime.now().time().microsecond
        seed(now)

        # Ciclo for : ogni iterazione genera una Solution nuova
        for sol_count in range(pop_dim):
            routes = []         # Routes è la lista contente i percorsi dei vari camion quindi la Solution effettiva
            stop = 0            # Condizione di terminazione del while seguente
            truck_count = 0     # Truck_count riporta il numero di camion della Solution trovata (va inizializzato a 0)
            nodes_left = unsorted_nodes[1:len(unsorted_nodes)]        # Nodes_left rappresenta l'insieme dei nodi non
                                                                      # ancora raggiunti da nessun camion (escluso il deposito)
            buff_truck = unsorted_nodes[1:len(unsorted_nodes)]        # Buff_truck rappresenta la lista dei nodi usata da
            # un camion per tracciare il suo percorso (escluso il deposito); Esempio : per vincoli temporali o di capacità un nodo può essere
            # eliminato da questa buff_truck (in quanto non raggiungibile dal camion in questione) ma non verrà eliminato
            # dalla lista nodes_left siccome un altro camion potrebbe raggiungerlo

            while stop == 0:
                if buff_truck:          # Se buff_truck non è vuoto = ci sono altri nodi analizzabili dal camion attuale
                    if j % (sol_count + randomness) == 0 :    # Ogni sol_count + randomness nodi aggiunti si sceglie
                        next_node = choice(buff_truck)                      # casualmente il prossimo nodo da analizzare
                    else:
                        min_distance_time = 1000000000  #Upper bound per il settaggio iniziale della distanza minima 
                        for i in buff_truck:
                            if self.instance.distances[current_node, i.number] + i.due_date < min_distance_time:
                                index_best_choice = i.number
                                min_distance_time = self.instance.distances[current_node, i.number] + i.due_date
                        next_node = self.instance.nodes[index_best_choice]

                    if next_node.demand <= remaining_capacity and (
                            current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        # Il nodo può essere aggiunto al percorso se non richiede più capacità di quella rimasta e se è
                        # possibile spostarsi in esso dal nodo corrente senza superare la sua due date

                        route.append(next_node)            # Aggiungo il nodo al percorso del camion
                        buff_truck.remove(next_node)       # Il nodo è stato raggiunto quindi va eliminato da buff_truck e nodes_left
                        nodes_left.remove(next_node)

                        remaining_capacity = remaining_capacity - next_node.demand      # Aggiornamento capacità

                        if (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                            current_time = next_node.rdy_time + next_node.service_time    # Se arrivo nel next_node prima
                            # del suo ready time dovrò aspettare il ready time per servirlo quindi potrò lasciare il next_node
                            # al tempo : ready_time del next node + tempo di servizio del next_node

                        else:
                            current_time = current_time + self.instance.travel_times[current_node, next_node.number] + next_node.service_time
                            # Se arrivo dopo il ready time posso iniziare subito a servire il nodo

                        current_node = next_node.number  # Aggiornamento nodo corrente
                        j = j + 1  # Aggiornamento parametro per scelta casuale
                    else:
                        buff_truck.remove(next_node)    #Se il nodo non è raggiungibile dal camion attuale lo elimino dalla
                        # lista buff_truck, tale nodo sarà raggiunto da qualche altro camion

                else:
                    # Se buff_truck è vuoto vuol dire che il camion attuale non può coprire nessun altro nodo quindi dovrà
                    # tornare nel deposito
                    route.append(self.instance.nodes[0])
                    routes.append(route[0:len(route)])        # Aggiungo il percorso all'insieme di percorsi rappresentante la Solution
                    route = []                  # Ripristino la lista route (riparto dal deposito con un nuovo camion)
                    truck_count = truck_count + 1   # Aggiornamento numero camion
                    current_time = 0                # Ripristino current_node
                    current_node = 0                # Ripristino tempo e capacità
                    remaining_capacity = self.instance.capacity
                    if nodes_left:        # Se ci sono ancora nodi da raggiungere li copio in buff_truck
                        buff_truck = nodes_left[0:len(nodes_left)]
                    else:               # Se non ci sono nodi in nodes_left vuol dire che i camion hanno coperto tutti
                                        # i clienti quindi la Solution è completa
                        stop = 1

            # Adattamento del formato della Solution : la Solution così come è stata calcolata è una lista di percorsi
            # quindi una lista di liste, tuttavia per facilitare il crossover la Solution sarà trasformata in una lista
            # di nodi messi in ordine secondo i percorsi dei camion
            temp = []
            for r in routes:
                temp.extend(r)
            single_row_routes = temp[0:len(temp)]
            self.population.append(Solution(single_row_routes, self.instance, truck_count))

        return self.population[0:len(self.population)]

# ----------------------------------------------------------------------------------------------------------------------
    # Generazione della popolazione iniziale di soluzioni ordinando per tempo di spostamento più basso
    def Gen_starting_population_NF(self, pop_dim=50, randomness = 10):  

        # Salvataggio della lista di nodi del grafo 
        unsorted_nodes = self.instance.nodes[0:self.instance.nodes_num]

        # Inizializzazione variabili
        current_node = 0  # Ultimo nodo aggiunto al percorso corrente  (si parte sempre dal nodo deposito)
        current_time = 0  # Tempo trascorso per arrivare al current_node
        remaining_capacity = self.instance.capacity  # Capacità rimanente del camion (il camion parte con capacità massima)
        route = [self.instance.nodes[0]]  # Percorso del camion che si sta analizzando (un camion parte sempre dal deposito)

        j = 0  # "j" serve alla scelta casuale che renderà le soluzioni eterogenee
        now = datetime.now().time().microsecond
        seed(now)

        # Ciclo for : ogni iterazione genera una Solution nuova
        for sol_count in range(pop_dim):
            routes = []  # Routes è la lista contente i percorsi dei vari camion quindi la Solution effettiva
            stop = 0  # Condizione di terminazione del while seguente
            truck_count = 0  # Truck_count riporta il numero di camion della Solution trovata (va inizializzato a 0)
            nodes_left = unsorted_nodes[1:len(unsorted_nodes)]  # Nodes_left rappresenta l'insieme dei nodi non
            # ancora raggiunti da nessun camion (escluso il deposito)
            buff_truck = unsorted_nodes[1:len(unsorted_nodes)]  # Buff_truck rappresenta la lista dei nodi usata da
            # un camion per tracciare il suo percorso (escluso il deposito); Esempio : per vincoli temporali o di capacità un nodo può essere
            # eliminato da questa buff_truck (in quanto non raggiungibile dal camion in questione) ma non verrà eliminato
            # dalla lista nodes_left siccome un altro camion potrebbe raggiungerlo

            while stop == 0:
                if buff_truck:  # Se buff_truck non è vuoto = ci sono altri nodi analizzabili dal camion attuale
                    if j % (sol_count + randomness) == 0:  # Ogni sol_count + randomness nodi aggiunti si sceglie
                        next_node = choice(buff_truck)  # casualmente il prossimo nodo da analizzare
                    else:
                        min_distance_time = 1000000000      #Upper bound per il settaggio iniziale della distanza minima 
                        for i in buff_truck:
                            if self.instance.distances[current_node, i.number] < min_distance_time:
                                index_nearest_node = i.number
                                min_distance_time = self.instance.distances[current_node, i.number]
                        next_node = self.instance.nodes[index_nearest_node]

                    if next_node.demand <= remaining_capacity and (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        # Il nodo può essere aggiunto al percorso se non richiede più capacità di quella rimasta e se è
                        # possibile spostarsi in esso dal nodo corrente senza superare la sua due date

                        route.append(next_node)  # Aggiungo il nodo al percorso del camion
                        buff_truck.remove(next_node)  # Il nodo è stato raggiunto quindi va eliminato da buff_truck e nodes_left
                        nodes_left.remove(next_node)

                        remaining_capacity = remaining_capacity - next_node.demand  # Aggiornamento capacità

                        if (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                            current_time = next_node.rdy_time + next_node.service_time  # Se arrivo nel next_node prima
                            # del suo ready time dovrò aspettare il ready time per servirlo quindi potrò lasciare il next_node
                            # al tempo : ready_time del next node + tempo di servizio del next_node

                        else:
                            current_time = current_time + self.instance.travel_times[current_node, next_node.number] + next_node.service_time
                            # Se arrivo dopo il ready time posso iniziare subito a servire il nodo
                            
                        current_node = next_node.number  # Aggiornamento nodo corrente
                        j = j + 1  # Aggiornamento parametro per scelta casuale
                    else:
                        buff_truck.remove(next_node)  # Se il nodo non è raggiungibile dal camion attuale lo elimino dalla
                        # lista buff_truck, tale nodo sarà raggiunto da qualche altro camion

                else:
                    # Se buff_truck è vuoto vuol dire che il camion attuale non può coprire nessun altro nodo quindi dovrà
                    # tornare nel deposito
                    route.append(self.instance.nodes[0])
                    routes.append(route[0:len(route)])  # Aggiungo il percorso all'insieme di percorsi rappresentante la Solution
                    route = []  # Ripristino la lista route (riparto dal deposito con un nuovo camion)
                    truck_count = truck_count + 1  # Aggiornamento numero camion
                    current_time = 0  # Ripristino current_node
                    current_node = 0  # Ripristino tempo e capacità
                    remaining_capacity = self.instance.capacity
                    if nodes_left:  # Se ci sono ancora nodi da raggiungere li copio in buff_truck
                        buff_truck = nodes_left[0:len(nodes_left)]
                    else:  # Se non ci sono nodi in nodes_left vuol dire che i camion hanno coperto tutti
                        # i clienti quindi la Solution è completa
                        stop = 1

            # Adattamento del formato della Solution : la Solution così come è stata calcolata è una lista di percorsi
            # quindi una lista di liste, tuttavia per facilitare il crossover la Solution sarà trasformata in una lista
            # di nodi messi in ordine secondo i percorsi dei camion
            temp = []
            for r in routes:
                temp.extend(r)
            single_row_routes = temp[0:len(temp)]
            self.population.append(Solution(single_row_routes, self.instance, truck_count))

        return self.population[0:len(self.population)]

# ----------------------------------------------------------------------------------------------------------------------
    # Generazione della popolazione iniziale di soluzioni ordinando per deadline più imminente
    def Gen_starting_population_EDF(self, pop_dim = 50, randomness = 5):  

        # Salvataggio della lista di nodi del grafo (non ordinata)
        unsorted_nodes = self.instance.nodes
        # Generazione della lista che ha come elemento i il due date del nodo i-esimo del grafo
        due_dates = []
        for i in unsorted_nodes:
            due_dates.append(i.due_date)

        # Ordinamento della lista due date (senso crescente) e salvataggio degli indici in arg_sort
        arg_sort = np.argsort(due_dates)

        # Dichiarazione di liste buffer utili in seguito
        static_sorted = []
        # Generazione della lista di nodi (senza il deposito) ordinata per due date
        for i in arg_sort:
            if i != 0:
                static_sorted.append(unsorted_nodes[i])

        # Inizializzazione variabili
        current_node = 0  # Ultimo nodo aggiunto al percorso corrente  (si parte sempre dal nodo deposito)
        current_time = 0  # Tempo trascorso per arruvare al current_node
        remaining_capacity = self.instance.capacity  # Capacità rimanente del camion (il camion parte con capacità massima)
        route = [unsorted_nodes[0]]  # Percorso del camion che si sta analizzando (un camion parte sempre dal deposito)
        j = 0  # "j" serve alla scelta casuale che renderà le soluzioni eterogenee

        now = datetime.now().time().microsecond
        seed(now)

        # Ciclo for : ogni iterazione genera una Solution nuova
        for sol_count in range(pop_dim):
            routes = []  # Routes è la lista contente i percorsi dei vari camion quindi la Solution effettiva
            stop = 0  # Condizione di terminazione del while seguente
            truck_count = 0  # Truck_count riporta il numero di camion della Solution trovata (va inizializzato a 0)
            nodes_left = static_sorted[0:len(static_sorted)]  # Nodes_left rappresenta l'insieme dei nodi non
            # ancora raggiunti da nessun camion
            buff_truck = static_sorted[0:len(static_sorted)]  # Buff_truck rappresenta la lista dei nodi usata da
            # un camion per tracciare il suo percorso; Esempio : per vincoli temporali o di capacità un nodo può essere
            # eliminato da questa buff_truck (in quanto non raggiungibile dal camion in questione) ma non verrà eliminato
            # dalla lista nodes_left siccome un altro camion potrebbe raggiungerlo

            while stop == 0:
                if buff_truck:  # Se buff_truck non è vuoto = ci sono altri nodi analizzabili dal camion attuale
                    if j % (sol_count + randomness) == 0:  # Ogni sol_count + randomness nodi aggiunti si sceglie casualmente il prossimo nodo da analizzare
                        next_node = choice(buff_truck)
                    else:
                        next_node = buff_truck[0]  # Le restanti volte il nodo da analizzare è quello con due date più imminente

                    if next_node.demand <= remaining_capacity and (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        # Il nodo può essere aggiunto al percorso se non richiede più capacità di quella rimasta e se è
                        # possibile spostarsi in esso dal nodo corrente senza superare la sua due date

                        route.append(next_node)  # Aggiungo il nodo al percorso del camion
                        buff_truck.remove(next_node)  # Il nodo è stato raggiunto quindi va eliminato da buff_truck e nodes_left
                        nodes_left.remove(next_node)
                        remaining_capacity = remaining_capacity - next_node.demand  # Aggiornamento capacità
                        if (current_time + self.instance.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                            current_time = next_node.rdy_time + next_node.service_time  # Se arrivo nel next_node prima
                            # del suo ready time dovrò aspettare il ready time per servirlo quindi potrò lasciare il next_node
                            # al tempo : ready_time del next node + tempo di servizio del next_node

                        else:
                            current_time = current_time + self.instance.travel_times[current_node, next_node.number] + next_node.service_time
                            # Se arrivo dopo il ready time posso iniziare subito a servire il nodo

                        current_node = next_node.number  # Aggiornamento nodo corrente
                        j = j + 1  # Aggiornamento parametro per scelta casuale

                    else:
                        buff_truck.remove(next_node)  # Se il nodo non è raggiungibile dal camion attuale lo elimino dalla
                        # lista buff_truck, tale nodo sarà raggiunto da qualche altro camion
                else:
                    # Se buff_truck è vuoto vuol dire che il camion attuale non può coprire nessun altro nodo quindi dovrà
                    # tornare nel deposito
                    route.append(unsorted_nodes[0])
                    routes.append(route[0:len(route)])  # Aggiungo il percorso all'insieme di percorsi rappresentate la Solution
                    route = []  # Ripristino la lista route (riparto dal deposito con un nuovo camion)
                    truck_count = truck_count + 1  # Aggiornamento numero camion
                    current_time = 0  # Ripristino current_node
                    current_node = 0  # Ripristino tempo e capacità
                    remaining_capacity = self.instance.capacity
                    if len(nodes_left) != 0:  # Se ci sono ancora nodi da raggiungere li copio in buff_truck
                        buff_truck = nodes_left[0:len(nodes_left)]
                    else:  # Se non ci sono nodi in nodes_left vuol dire che i camion hanno coperto tutti
                        # i clienti quindi la Solution è completa
                        stop = 1

            # Adattamento del formato della Solution : la Solution così come è stata calcolata è una lista di percorsi
            # quindi una lista di liste, tuttavia per facilitare il crossover la Solution sarà trasformata in una lista
            # di nodi messi in ordine secondo i percorsi dei camion
            temp = []
            for r in routes:
                temp.extend(r)
            single_row_routes = temp[0:len(temp)]
            self.population.append(Solution(single_row_routes, self.instance, truck_count))

        return self.population

# ----------------------------------------------------------------------------------------------------------------------
    # Avvio dell'algoritmo genetico
    def Start_algorithm(self, tolerance, max_iterations = 200, mut_prob = 0.5, mut_dim = 20, crossover_dim = 20 ):
        best = self.Best_solution()
        worst = self.Worst_solution()
        mutation_probability = mut_prob
        k = 0
        while k < max_iterations or worst.obj_fun_value - best.obj_fun_value > tolerance:  # Genera nuove soluzioni finché il peggior individuo della
            # popolazione non dista meno di "tolerance" dal peggiore
            k += 1
            # Effettua una possibile mutazione
            seed(time.time())
            p = random.uniform(0, 1)
            if p < mutation_probability:
                # effettua una mutazione
                index_cavy = random.randint(0, len(self.population) - 1)
                if self.population[index_cavy] != best:
                    #parent_mut = self.__Mutation(self.population[index_cavy], mut_dim)
                    parent_mut = self.__Simple_mutation(self.population[index_cavy], mut_dim)
                    if parent_mut.Is_admissible() == 1:
                        self.population[index_cavy].Copy(parent_mut)
                        #print("Mutazione avvenuta")
                    #else:
                        #print("Mutazione non avvenuta")

            ## Estrazione con la simulazione montecarlo degli indici dei due genitori dalla popolazione
            (index_parent1, index_parent2) = self.__Montecarlo_simulation()
            # Estrazione con la simulazione Torneo degli indici dei due genitori dalla popolazione
            #(index_parent1, index_parent2) = self.__Tournament_simulation()

            ##Estrazione Casuale
            #index_parent2 = 0
            #index_parent1 = 0
            #while index_parent1 == index_parent2:
             #   index_parent1 = random.randint(0, len(self.population) - 1)
              #  index_parent2 = random.randint(0, len(self.population) - 1)

            # Crossover tra i due genitori
            (child_1, child_2) = self.__BCRC(self.population[index_parent1], self.population[index_parent2], crossover_dim)
            # (child_1, child_2) = self.__Double_crossover(self.population[index_parent1], self.population[index_parent2], 10)

            # Estrazione delle 2 soluzioni peggiori, eventualmente da sostituire
            (index_worst1, index_worst2) = self.__Two_Worst_solutions()

            # Aggiornamento della popolazione con i nuovi individui, se vantaggioso
            outcome = self.__Update_population(index_worst1, index_worst2, child_1, child_2)

            if outcome == 1:
                print("Generate due soluzioni inammissibili")

            # Calcolo la nuova soluzione migliore e la nuova soluzione peggiore
            best = self.Best_solution()
            worst = self.Worst_solution()

        return self.Best_solution()

# ----------------------------------------------------------------------------------------------------------------------
    # Generazione della lista di fitness cumulate utile alla simulazione Montecarlo
    def __Compute_cumulative_fitness(self, lista_fitness):

        cumulative_fitness = []
        F = sum(lista_fitness)
        for i in range(len(lista_fitness)):
            F_i = sum(lista_fitness[0:i + 1]) / F
            cumulative_fitness.append(F_i)

        return cumulative_fitness

# ----------------------------------------------------------------------------------------------------------------------
    #Simulazione Montecarlo
    def __Montecarlo_simulation(self):
        cumulative_fitness = self.__Compute_cumulative_fitness([k.fitness for k in self.population])
        #  for i in range(len(cumulative_fitness)):
        #     print(i," ", cumulative_fitness[i])

        seed(time.time())
        index_a = 0
        index_b = 0

        while index_a == index_b:
            a = random.uniform(0, 1)
            b = random.uniform(0, 1)
            stop_a = 0
            stop_b = 0
            i = 0
            while stop_a == 0 or stop_b == 0:
                if stop_a == 0 and cumulative_fitness[i] > a:
                    stop_a = 1
                    index_a = i
                if stop_b == 0 and cumulative_fitness[i] > b:
                    stop_b = 1
                    index_b = i
                i += 1

        # print("a : ", a, "index_a: ", index_a, "b: ", b, "index_b : ", index_b, "\n")
        return index_a, index_b

# ----------------------------------------------------------------------------------------------------------------------
    # Simulazione Torneo
    def __Tournament_simulation(self):
        index = [0, 0]

        while index[0] == index[1]:
            for i in range(2):
                tmp_index1 = 0
                tmp_index2 = 0
                tmp_index3 = 0
                tmp_index4 = 0
                tmp_index5 = 0

                while tmp_index1 == tmp_index2 or tmp_index2 == tmp_index3 or tmp_index3 == tmp_index4 or tmp_index4 == tmp_index5:
                    seed(datetime.now().time().microsecond)
                    tmp_index1 = random.randint(0, len(self.population)-1)
                    tmp_index2 = random.randint(0, len(self.population)-1)
                    tmp_index3 = random.randint(0, len(self.population)-1)
                    tmp_index4 = random.randint(0, len(self.population)-1)
                    tmp_index5 = random.randint(0, len(self.population)-1)

                tmp_population = [self.population[tmp_index1], self.population[tmp_index2], self.population[tmp_index3],self.population[tmp_index4], self.population[tmp_index5]]
                index[i] = self.population.index(min(tmp_population, key=lambda item: item.obj_fun_value))

        return index[0], index[1]

# ----------------------------------------------------------------------------------------------------------------------
    # Best Cost Route Crossover (revisionato)
    def __BCRC(self, solution1, solution2, range):  # Crossover

        # Seed per le funzioni randomiche
        seed(time.time())

        # Si rimuove il deposito dai genitori
        tmp_routes1 = [i for i in solution1.routes if i.number != 0]
        tmp_routes2 = [i for i in solution2.routes if i.number != 0]

        # Si prendono due indici casuali in un range predefinito
        index1 = random.randint(0, len(tmp_routes1) - range)
        index2 = random.randint(index1, index1 + range)

        # Si costruiscono i tagli sulla base dei due indici casuali
        list1 = tmp_routes1[index1:index2]
        list2 = tmp_routes2[index1:index2]

        # Si rimuovono le liste dai genitori
        for j in list2:
            tmp_routes1 = [i for i in tmp_routes1 if i.number != j.number]

        for j in list1:
            tmp_routes2 = [i for i in tmp_routes2 if i.number != j.number]

        # Si calcolano le distanze dei nodi nel parente 1 per ogni nodo nella lista 2
        results = []
        # Dizionario del tipo:
        # Key -> Numero di ogni nodo i-esimo
        # Valore -> dinstance calcolata del nodo i-esimo di parent dal nodo j-esimo di lista
        distances_from_list2 = {}
        for j in list2:
            temp = []
            for i in tmp_routes1:
                # Si calcolano le distanze per ogni nodo j ed i
                distances_from_list2[i.number] = (
                    solution1.instance.nodes[j.number].distance(solution1.instance.nodes[i.number]))
            # Si prende la chiave associata al minimo di queste distanze per capire dove inserire il nodo j di list2
            temp = min(distances_from_list2.values())
            # Si ha la lista dei nodi più vicini, possono essere più di uno
            results = ([key for key in distances_from_list2 if distances_from_list2[key] == temp])
            # Bisogna ora trovare l'indice del minimo. Se ce n'è più di uno, se ne sceglie uno soltanto randomicamente
            index_min = 0
            for i in tmp_routes1:
                if i.number == results[random.randint(0, len(results) - 1)]:
                    index_min = tmp_routes1.index(i)
                    break
            # Si inserisce il minimo all'indice calcolato
            tmp_routes1.insert(index_min + 1, j)

        results = []
        distances_from_list1 = {}
        for j in list1:
            temp = []
            for i in tmp_routes2:
                distances_from_list1[i.number] = (
                    solution2.instance.nodes[j.number].distance(solution2.instance.nodes[i.number]))
            temp = min(distances_from_list1.values())
            results = ([key for key in distances_from_list1 if distances_from_list1[key] == temp])
            for i in tmp_routes2:
                if i.number == results[random.randint(0, len(results) - 1)]:
                    index_min = tmp_routes2.index(i)
                    break
            tmp_routes2.insert(index_min + 1, j)

        new_solution1 = Solution(tmp_routes1,self.instance)
        new_solution2 = Solution(tmp_routes2,self.instance)

        return new_solution1, new_solution2

# ----------------------------------------------------------------------------------------------------------------------
    # Crossover TSP
    def __Double_crossover(self, sol1, sol2, r):
        # Seed per le funzioni randomiche
        seed(time.time())
        # Si rimuove il deposito dai genitori
        tmp_routes1 = [i.number for i in sol1.routes if i.number != 0]
        tmp_routes2 = [i.number for i in sol2.routes if i.number != 0]
        # Si prende un indice casuale che taglia la stringa
        index1 = random.randint(0, len(tmp_routes1) - r)
        index2 = random.randint(index1, index1 + r)

        # Si costruiscono i tagli sulla base dei due indici casuali
        list1 = tmp_routes1[index1:index2]
        list2 = tmp_routes2[index1:index2]

        # eseguo il crossover
        tmp_routes1[index1:index2] = list2
        tmp_routes2[index1:index2] = list1

        # filtro le nuove soluzioni con il metodo del TSP
        for i in range(0, index1):
            k = tmp_routes1[i]
            while k in list2:
                index = list2.index(k)
                k = list1[index]
            tmp_routes1[i] = k
        for i in range(index2, len(tmp_routes1)):
            k = tmp_routes1[i]
            while k in list2:
                index = list2.index(k)
                k = list1[index]
            tmp_routes1[i] = k

        for i in range(0, index1):
            k = tmp_routes2[i]
            while k in list1:
                index = list1.index(k)
                k = list2[index]
            tmp_routes2[i] = k
        for i in range(index2, len(tmp_routes1)):
            k = tmp_routes2[i]
            while k in list1:
                index = list1.index(k)
                k = list2[index]
            tmp_routes2[i] = k

        # Costruzione della lista di Soluzioni
        nodes = []
        for i in tmp_routes1:
            nodes.append(self.instance.nodes[i])
        new_sol1 = Solution(nodes, self.instance)
        nodes = []
        for i in tmp_routes2:
            nodes.append(self.instance.nodes[i])
        new_sol2 = Solution(nodes, self.instance)

        return new_sol1, new_sol2

# ----------------------------------------------------------------------------------------------------------------------
    # Mutazione a blocco : inversione del blocco
    def __Mutation(self, sol, r):
        seed(time.time())

        # Si rimuove il deposito dalla soluzione
        tmp_routes = [i.number for i in sol.routes if i.number != 0]
        index1 = random.randint(0, len(tmp_routes) - r)
        index2 = random.randint(index1, index1 + r)

        # Si inverte l'oridine nel taglio centrale
        mut = tmp_routes[index1:index2]
        tmp_routes[index1:index2] = mut[::-1]

        nodes = []
        for i in tmp_routes:
            nodes.append(self.instance.nodes[i])
        new_sol = Solution(nodes, self.instance)
        return new_sol

# ----------------------------------------------------------------------------------------------------------------------
    # Mutazione a elemento : scambio di swap_count elementi
    def __Simple_mutation(self, sol, swap_count):

        # Si rimuove il deposito dalla soluzione
        tmp_routes = [i.number for i in sol.routes if i.number != 0]
        for _ in range(swap_count):
            swap_index1 = 0
            swap_index2 = 0

            while swap_index1 == swap_index2:
                seed(time.time())
                swap_index1 = random.randint(0, len(tmp_routes) - 1)
                swap_index2 =  random.randint(0, len(tmp_routes) - 1)

            # Si invertono i due nodi
            buff = tmp_routes[swap_index2]
            tmp_routes[swap_index2] = tmp_routes[swap_index1]
            tmp_routes[swap_index1] = buff

        nodes = []
        for i in tmp_routes:
            nodes.append(self.instance.nodes[i])
        new_sol = Solution(nodes, self.instance)
        return new_sol

# ----------------------------------------------------------------------------------------------------------------------
    # Estrazione delle due soluzioni peggiori
    def __Two_Worst_solutions(self):      # Ritorna gli indici delle 2 soluzioni con fitenss più bassa
        fitness = []
        for i in self.population:
            fitness.append(i.fitness)
        arg_sort = np.argsort(fitness)
        return arg_sort[0],arg_sort[1]

# ----------------------------------------------------------------------------------------------------------------------
    # Aggiornamento della popolazione con new_sol_1 e new_sol_2
    def __Update_population(self, index_old_sol_1, index_old_sol_2, new_sol_1, new_sol_2):

        if self.population[index_old_sol_1].fitness > self.population[index_old_sol_2].fitness:
            index_worst_old = index_old_sol_2  # index_worst_old è la Solution migliore di quelle scelte per essere eliminate
            index_best_old = index_old_sol_1  # index_best_old è la Solution migliore delle due scelte per essere eliminate
        else:
            index_worst_old = index_old_sol_1
            index_best_old = index_old_sol_2

        sol1_acceptable = new_sol_1.Is_admissible()
        sol2_acceptable = new_sol_2.Is_admissible()

        if sol1_acceptable and sol2_acceptable:

            if new_sol_1.fitness > new_sol_2.fitness:
                best_new = new_sol_1                # best_new è la Solution migliore delle due scelte per essere inserite
                worst_new = new_sol_2               # worst_new è la Solution migliore delle due scelte per essere inserite
            else:
                best_new = new_sol_2
                worst_new = new_sol_1

            if best_new.fitness <= self.population[index_worst_old].fitness:  # Se la peggiore delle soluzioni da rimuovere
                # ha una fitness migliore della migliore delle soluzioni nuove allora non si possono effettuare scambi
                return 0

            else:
                if best_new.fitness > self.population[index_best_old].fitness and worst_new.fitness > self.population[index_worst_old].fitness:
                    self.population[index_best_old].Copy(best_new)
                    self.population[index_worst_old].Copy(worst_new)
                    #if new_sol_1.admissible or new_sol_2.admissible:
                     #   print("Aggiunta soluzione inammissibile ")

                elif worst_new.fitness <= self.population[index_worst_old].fitness:
                    self.population[index_worst_old].Copy(best_new)
                    #if worst_new.admissible :
                     #   print("Aggiunta soluzione inammissibile ")
                return 0

        elif sol1_acceptable:

            if new_sol_1.fitness > self.population[index_worst_old].fitness:
                self.population[index_worst_old].Copy(new_sol_1)
                #if new_sol_1.admissible:
                 #   print("Aggiunta soluzione inammissibile ")
            return 0

        elif sol2_acceptable:

            if new_sol_2.fitness > self.population[index_worst_old].fitness:
                self.population[index_worst_old].Copy(new_sol_2)
                #if new_sol_2.admissible:
                 #   print("Aggiunta soluzione inammissibile ")
            return 0

        else:
            return 1

# ----------------------------------------------------------------------------------------------------------------------
    # Estrazione della soluzione peggiore della popolazione
    def Worst_solution(self):                   # Ritorna la Solution della population con fitness più bassa
        return max(self.population, key=lambda item: item.obj_fun_value)

# ----------------------------------------------------------------------------------------------------------------------
    # Estrazione della soluzione migliore della popolazione
    def Best_solution(self):                    # Ritorna la Solution della population con fitness più alta
        return min(self.population, key=lambda item: item.obj_fun_value)

# ----------------------------------------------------------------------------------------------------------------------
    # Grafico nodi-archi della soluzione passata come parametro
    def Graph_solution(self, solution):

        Graph = nx.DiGraph()
        list_nodes = list(range(self.instance.nodes_num))
        Graph.add_nodes_from(list_nodes)
        for i in range(len(solution.routes)-1):
            Graph.add_edge(solution.routes[i].number, solution.routes[i+1].number)

        coordinates = {}
        for i in range(self.instance.nodes_num):
            coordinates[i] = self.instance.nodes[i].coordinate

        nx.draw_networkx(Graph, coordinates, font_size=8, font_color='k', node_color='green', edgecolors='k',
                         node_size=300)
        nx.draw_networkx_edges(Graph, coordinates, arrowsize=7, arrowstyle='->', edge_color='black')

        plt.show()

        return 0

import numpy as np
from datetime import datetime
import time
import random
from random import choice
from random import seed


# ********************************************************* CLASSI *****************************************************


class Soluzione:
    def __init__(self, percorsi, cvrptw_istanza, camion=0):
        self.istanza = cvrptw_istanza
        self.routes = percorsi[0:len(percorsi)]
        self.truck_count = camion
        self.valore_f_ob = self.calcola_val_f_ob(cvrptw_istanza.distances)
        self.fitness = 1/self.valore_f_ob
        self.admissible = 1

    def calcola_val_f_ob(self, matrice_distanze):
        val_f_ob = 0
        for n in range(len(self.routes) - 1):
            if self.routes[n].number != self.routes[n + 1].number :
                val_f_ob += matrice_distanze[self.routes[n].number, self.routes[n + 1].number]
        return val_f_ob

    # Attenzione!
    # Funziona solo con soluzione da cui è stato rimosso il deposito (nodo 0)
    # Se bisogna usarla per soluzioni con 0, è necessario inserire un controllo all'inizio
    def is_admissible(self):
        current_time = 0
        truck_number = 0
        current_node = 0
        self.routes.insert(current_node, self.istanza.nodes[0])
        remaining_capacity = self.istanza.capacity
        i = 0
        k = 0
        ammissibile = 1

        # Per ogni nodo di routes
        while k < 99 :
            # Current_node -> deposito fittizio
            # next_node -> routes[i] per i che parte da 0
            next_node = self.routes[i+1]

            # Verifica vincoli di capacità e temporali
            if next_node.demand <= remaining_capacity and (
                    current_time + self.istanza.travel_times[current_node, next_node.number]) <= next_node.due_date:
                remaining_capacity = remaining_capacity - next_node.demand
                if (current_time + self.istanza.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                    current_time = next_node.rdy_time + next_node.service_time
                else:
                    current_time = current_time + self.istanza.travel_times[current_node, next_node.number] + next_node.service_time
                # Se è tutto ok, si incrementano current_node e next_node
                current_node = next_node.number
                i += 1
                k += 1
            # Altrimenti:
            # truck_number ++ -> parte un nuovo camion, se ne incrementa il conteggio
            # current_time = 0 -> si resetta il tempo, partendo da un nuovo deposito
            # si resetta la capacità
            # current_node = 0 -> nuovo deposito fittizio
            else:
                truck_number += 1
                self.routes.insert(i, self.istanza.nodes[0])
                current_time = 0
                i += 1
                remaining_capacity = self.istanza.capacity
                current_node = 0

        # Condizione di ammissibilità = numero di camion minore al numero consentito
        self.routes.append(self.istanza.nodes[0])
        truck_number += 1
        if truck_number > self.istanza.num_vehicle:
            ammissibile = 0
            self.admissible = 0
            self.truck_count = truck_number
        else:
            self.truck_count = truck_number
            self.valore_f_ob = self.calcola_val_f_ob(self.istanza.distances)
            self.fitness = 1/self.valore_f_ob
            self.admissible = 1
            ammissibile = 1

        return ammissibile

    def __str__(self):
        print("Percorsi : ")
        for i in range(len(self.routes)):
            if i == 0  or self.routes[i].number != 0:
                print(self.routes[i].number, end=", ")
            else:
                print("0")
        return "\n" + "Valore funzione obiettivo : " + str(self.valore_f_ob) + "\n" + "Numero Camion : " + str(self.truck_count) + "\n"

    def __repr__(self):
        return self.__str__(self)

    def copy(self, solution_to_copy):
        self.istanza = solution_to_copy.istanza
        self.routes = solution_to_copy.routes[0:len(solution_to_copy.routes)]
        self.truck_count = solution_to_copy.truck_count
        self.valore_f_ob = solution_to_copy.valore_f_ob
        self.fitness = solution_to_copy.fitness



class Algoritmo_genetico:
    def __init__(self, cvrptw_istance):
        self.istanza = cvrptw_istance            # Local CVRPTW istance
        self.popolazione = []

    def gen_popolazione_iniziale(self):         # Generazione della popolazione iniziale di soluzioni (50 soluzioni)

        # Salvataggio della lista di nodi del grafo (non ordinata)
        unsorted_nodes = self.istanza.nodes
        # Generazione della lista che ha come elemento i il due date del nodo i-esimo del grafo
        due_dates = []
        for i in unsorted_nodes:
            due_dates.append(i.due_date)

        # Ordinamento della lista due date (senso crescente) e salvataggio degli indici in arg_sort
        arg_sort = np.argsort(due_dates)

        # Dichiarazione di liste buffer utili in seguito
        nodes_left = []
        buff_truck = []
        single_row_routes = []
        static_sorted = []
        # Generazione della lista di nodi (senza il deposito) ordinata per due date
        for i in arg_sort:
            if i != 0:
                static_sorted.append(unsorted_nodes[i])

        # Inizializzazione variabili
        current_node = 0            # Nodo che si sta analizzando nel percorso corrente  (si parte sempre dal nodo deposito)
        current_time = 0            # Tempo trascorso per arruvare al current_node
        remaining_capacity = self.istanza.capacity     # Capacità rimanente del camion (il camion parte con capacità massima)
        route = [unsorted_nodes[0]]             # Percorso del camion che si sta analizzando (un camion parte sempre dal deposito)
        j = 0                       # "j" serve alla scelta casuale che renderà le soluzioni eterogenee

        #now = datetime.now().time().microsecond
        seed(1)

        # Ciclo for : ogni iterazione genera una soluzione nuova
        for z in range(50):
            routes = []         # Routes è la lista contente i percorsi dei vari camion quindi la soluzione effettiva
            stop = 0            # Condizione di terminazione del while seguente
            truck_count = 0     # Truck_count riporta il numero di camion della soluzione trovata (va inizializzato a 0)
            nodes_left = static_sorted[0:len(static_sorted)]        # Nodes_left rappresenta l'insieme dei nodi non
            # ancora raggiunti da nessun camion
            buff_truck = static_sorted[0:len(static_sorted)]        # Buff_truck rappresenta la lista dei nodi usata da
            # un camion per tracciare il suo percorso; Esempio : per vincoli temporali o di capacità un nodo può essere eliminato
            # da questa buff_truck (in quanto non raggiungibile dal camion in questione) ma non verrà eliminato dalla
            # lista nodes_left siccome un altro camion potrebbe raggiungerlo

            while stop == 0:
                if buff_truck:          # Se buff_truck non è vuoto = ci sono altri nodi analizzabili dal camion attuale
                    if j % (z + 3) == 0:    # Ogni z+3 nodi aggiunti si sceglie casualmente il prossimo nodo da analizzare
                        next_node = choice(buff_truck)
                    else:
                        next_node = buff_truck[0]   # Le restanti volte il nodo da analizzare è quello con due date più imminente

                    if next_node.demand <= remaining_capacity and (
                            current_time + self.istanza.travel_times[current_node, next_node.number]) <= next_node.due_date:
                        # Il nodo può essere aggiunto al percorso se non richiede più capacità di quella rimasta e se è
                        # possibile spostarsi in esso dal nodo corrente senza superare la sua due date

                        route.append(next_node)            # Aggiungo il nodo al percorso del camion
                        buff_truck.remove(next_node)       # Il nodo è stato raggiunto quindi va eliminato da buff_truck e nodes_left
                        nodes_left.remove(next_node)
                        remaining_capacity = remaining_capacity - next_node.demand      # Aggiornamento capacità
                        if (current_time + self.istanza.travel_times[current_node, next_node.number]) <= next_node.rdy_time:
                            current_time = next_node.rdy_time + next_node.service_time    # Se arrivo nel next_node prima
                            # del suo ready time dovrò aspettare il ready time per servirlo quindi potrò lasciare il next_node
                            # al tempo : ready_time del next node + tempo di servizio del next_node

                        else:
                            current_time = current_time + self.istanza.travel_times[current_node, next_node.number] + next_node.service_time
                            # Se arrivo dopo il ready time posso iniziare subito a servire il nodo

                        current_node = next_node.number  # Aggiornamento nodo corrente
                        j = j + 1       # Aggiornamento parametro per scelta casuale

                    else:
                        buff_truck.remove(next_node)    #Se il nodo non è raggiungibile dal camion attuale lo elimino dalla
                        # lista buff_truck, tale nodo sarà raggiunto da qualche altro camion
                else:
                    # Se buff_truck è vuoto vuol dire che il camion attuale non può coprire nessun altro nodo quindi dovrà
                    # tornare nel deposito
                    route.append(unsorted_nodes[0])
                    routes.append(route)        # Aggiungo il percorso all'insieme di percorsi rappresentate la soluzione
                    route = []                  # Ripristino la lista route (riparto dal deposito con un nuovo camion)
                    truck_count = truck_count + 1   # Aggiornamento numero camion
                    current_time = 0                # Ripristino current_node
                    current_node = 0                # Ripristino tempo e capacità
                    remaining_capacity = self.istanza.capacity
                    if len(nodes_left) != 0:        # Se ci sono ancora nodi da raggiungere li copio in buff_truck
                        buff_truck = nodes_left[0:len(nodes_left)]
                    else:               # Se non ci sono nodi in nodes_left vuol dire che i camion hanno coperto tutti
                                        # i clienti quindi la soluzione è completa
                        stop = 1

            # Adattamento del formato della soluzione : la soluzione così come è stata calcolata è una lista di percorsi
            # quindi una lista di liste, tuttavia per facilitare il crossover la soluzione sarà trasformata in una lista
            # di nodi messi in ordine secondo i percorsi dei camion
            temp = []
            for r in routes:
                temp.extend(r)
            single_row_routes.extend(temp)
            self.popolazione.append(Soluzione(single_row_routes, self.istanza, truck_count))
            single_row_routes = []

        return self.popolazione

    def start_algorithm(self):
        best = self.best_solution()
        worst = self.worst_solution()
        while worst.valore_f_ob - best.valore_f_ob > 150:
            (index_parent1, index_parent2) = self.__simulazione_montecarlo()
            (child_1,child_2) = self.__BCRC(self.popolazione[index_parent1], self.popolazione[index_parent2], 30)
            (index_worst1, index_worst2) = self.__estrai_soluzioni_peggoiri()
            outcome = self.__aggiorna_popolazione(index_worst1, index_worst2, child_1, child_2)
            if outcome == 1:
                print("Generate entrambe soluzioni non ammissibili")

        return self.best_solution()

    def __calcola_fitness_cumulata(self, lista_fitness):
        fitness_cumulata = []
        F = sum(lista_fitness)
        for i in range(len(lista_fitness)):
            F_i = sum(lista_fitness[0:i + 1]) / F
            fitness_cumulata.append(F_i)

        return fitness_cumulata

    def __simulazione_montecarlo(self):
        fitness_cumulata = self.__calcola_fitness_cumulata([k.fitness for k in self.popolazione])
        #  for i in range(len(fitness_cumulata)):
        #     print(i," ", fitness_cumulata[i])

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
                if stop_a == 0 and fitness_cumulata[i] > a:
                    stop_a = 1
                    index_a = i
                if stop_b == 0 and fitness_cumulata[i] > b:
                    stop_b = 1
                    index_b = i
                i += 1

        # print("a : ", a, "index_a: ", index_a, "b: ", b, "index_b : ", index_b, "\n")
        return index_a, index_b

    def __BCRC(self, soluzione1, soluzione2, range):  # Crossover

        # Seed per le funzioni randomiche
        seed(time.time())

        # Si rimuove il deposito dai genitori
        tmp_routes1 = [i for i in soluzione1.routes if i.number != 0]
        tmp_routes2 = [i for i in soluzione2.routes if i.number != 0]

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
        # Valore -> distanza calcolata del nodo i-esimo di parent dal nodo j-esimo di lista
        distances_from_list2 = {}
        for j in list2:
            temp = []
            for i in tmp_routes1:
                # Si calcolano le distanze per ogni nodo j ed i
                distances_from_list2[i.number] = (
                    soluzione1.istanza.nodes[j.number].distance(soluzione1.istanza.nodes[i.number]))
            # Si prende la chiave associata al minimo di queste distanze per capire dove inserire il nodo j di list2
            temp = min(distances_from_list2.values())
            # Si ha la lista dei nodi più vicini, possono essere più di uno
            results = ([key for key in distances_from_list2 if distances_from_list2[key] == temp])
            # Bisogna ora trovare l'indice del minimo. Se ce n'è più di uno, se ne sceglie uno soltanto randomicamente
            indice = 0
            for i in tmp_routes1:
                if i.number == results[random.randint(0, len(results) - 1)]:
                    indice = tmp_routes1.index(i)
                    break
            # Si inserisce il minimo all'indice calcolato
            tmp_routes1.insert(indice + 1, j)

        results = []
        distances_from_list1 = {}
        for j in list1:
            temp = []
            for i in tmp_routes2:
                distances_from_list1[i.number] = (
                    soluzione2.istanza.nodes[j.number].distance(soluzione2.istanza.nodes[i.number]))
            temp = min(distances_from_list1.values())
            results = ([key for key in distances_from_list1 if distances_from_list1[key] == temp])
            for i in tmp_routes2:
                if i.number == results[random.randint(0, len(results) - 1)]:
                    indice = tmp_routes2.index(i)
                    break
            tmp_routes2.insert(indice + 1, j)

        new_solution1 = Soluzione(tmp_routes1,self.istanza)
        new_solution2 = Soluzione(tmp_routes2,self.istanza)

        return  new_solution1,new_solution2

    def __estrai_soluzioni_peggoiri(self):      # Ritorna gli indici delle 2 soluzioni con fitenss più bassa
        fitness = []
        for i in self.popolazione:
            fitness.append(i.fitness)
        arg_sort = np.argsort(fitness)
        return arg_sort[0],arg_sort[1]

    def __aggiorna_popolazione(self, index_old_sol_1, index_old_sol_2, new_sol_1, new_sol_2):

        if self.popolazione[index_old_sol_1].fitness > self.popolazione[index_old_sol_2].fitness:
            index_worst_old = index_old_sol_2  # index_worst_old è la soluzione migliore di quelle scelte per essere eliminate
            index_best_old = index_old_sol_1  # index_best_old è la soluzione migliore delle due scelte per essere eliminate
        else:
            index_worst_old = index_old_sol_1
            index_best_old = index_old_sol_2

        sol1_acceptable = new_sol_1.is_admissible()
        sol2_acceptable = new_sol_2.is_admissible()

        if sol1_acceptable and sol2_acceptable:

            if new_sol_1.fitness > new_sol_2.fitness:
                best_new = new_sol_1                # best_new è la soluzione migliore delle due scelte per essere inserite
                worst_new = new_sol_2               # worst_new è la soluzione migliore delle due scelte per essere inserite
            else:
                best_new = new_sol_2
                worst_new = new_sol_1

            if best_new.fitness <= self.popolazione[index_worst_old].fitness:  # Se la peggiore delle soluzioni da rimuovere
                # ha una fitness migliore della migliore delle soluzioni nuove allora non si possono effettuare scambi
                return 0

            else:
                if best_new.fitness > self.popolazione[index_best_old].fitness and worst_new.fitness > self.popolazione[index_worst_old].fitness:
                    self.popolazione[index_best_old].copy(best_new)
                    self.popolazione[index_worst_old].copy(worst_new)

                elif worst_new.fitness <= self.popolazione[index_worst_old].fitness:
                    self.popolazione[index_worst_old].copy(best_new)

                return 0

        elif sol1_acceptable:

            if new_sol_1.fitness > self.popolazione[index_worst_old].fitness:
                self.popolazione[index_worst_old].copy(new_sol_1)

            return 0

        elif sol2_acceptable:

            if new_sol_2.fitness > self.popolazione[index_worst_old].fitness:
                self.popolazione[index_worst_old].copy(new_sol_2)

            return 0

        else:
            return 1

    def worst_solution(self):                   # Ritorna la soluzione della popolazione con fitness più bassa
        return min(self.popolazione, key=lambda item: item.fitness)

    def best_solution(self):                    # Ritorna la soluzione della popolazione con fitness più alta
        return max(self.popolazione, key=lambda item: item.fitness)

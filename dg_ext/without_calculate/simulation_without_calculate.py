import sequential_without_calculate
import pandas as pd
import networkx as nx
import copy
import csv
from igraph import *
from timeit import default_timer as timer
from datetime import timedelta
import random
import sys
sys.path.insert(0, '..')


# metoda oblicza h-index
def selectSeeds(graph, forSequential):
    start = timer()

    degrees = [node for (node, val) in sorted(createNxGraph(graph).degree, key=lambda pair: pair[1], reverse=True)]
    degrees = degrees[0: forSequential]

    end = timer()

    return degrees, timedelta(seconds=end-start)
    # return degrees[0:forSequential], timedelta(seconds=end-start)


# metoda do wycięcia grafu jedynie z niezainfekowanymi węzłami
def selectSeedsUninfected(graph, forSequential):

    # wyrzucam tutaj z sieci zainfekowane węzły
    try:
        to_delete_ids = [v.index for v in graph.vs if 1 is v['infected']]
    except:
        to_delete_ids = []

    # print(to_delete_ids)

    uninfectedGraph = copy.copy(graph)

    # usunięcie po idkach ale pamiętać że ciągle kierujemy się attr NAME!!!!
    uninfectedGraph.delete_vertices(to_delete_ids)

    return selectSeeds(graph = uninfectedGraph, forSequential = forSequential)

def mapEdgeList(graph, edgeList):
    mapped = []

    for edge in edgeList:
        mapped.append([graph.vs.select(edge[0])[0]['name'], graph.vs.select(edge[1])[0]['name']])

    return mapped

def createNxGraph(graph):
    A = mapEdgeList(graph, graph.get_edgelist())
    return nx.Graph(A)


def selectSeedsRandomly(uninfectedNodes, forSequential):
    if(len(uninfectedNodes) >= forSequential):
        return random.choices(uninfectedNodes, k=forSequential)
    else:
        return uninfectedNodes

def calculateUninfected(graph):
    uninfected = [v['name'] for v in graph.vs if 0 is v['infected']]
    return uninfected


def calculateLimiForSeeding(graph, limit):
    return int(int(len(graph.vs) * limit)/100)

def calculateNumberOfSeeds(graph):
    seeds = [v.index for v in graph.vs if 1 is v['isSeed']]
    return len(seeds)

def flatten(t):
    return [item for sublist in t for item in sublist]


def simulation(pp, seeds, graph, coordinatedExecution, numberOfCoordinatedExecution, name, limit):

    step = 1;

    copyGraph = copy.copy(graph)

    timeArray = []
    seedsArray = []

    limitForSeeding = calculateLimiForSeeding(graph, limit)

    # robimy tylko 1 ranking na początku!! :)
    seedsForSequnetial, time = selectSeedsUninfected(graph = copyGraph, forSequential = graph.vcount())

    # seedsArray.append(seedsForSequnetial)

    timeArray.append(time)

    uninfected = [0, 0]

    while(len(uninfected) > 0 and len(flatten(seedsArray)) < limitForSeeding):


        if(len(seedsForSequnetial) > seeds):
            if(len(flatten(seedsArray)) + seeds > limitForSeeding):
                selectedSeeds = copy.copy(seedsForSequnetial[:limitForSeeding-len(flatten(seedsArray))])
            else:
                selectedSeeds = copy.copy(seedsForSequnetial[:seeds])

            seedsArray.append(selectedSeeds)
        else:
            if(len(flatten(seedsArray)) + seeds > limitForSeeding):
                selectedSeeds = selectSeedsRandomly(uninfected, forSequential=limitForSeeding-len(flatten(seedsArray)))
            else:
                selectedSeeds = selectSeedsRandomly(uninfected, forSequential=seeds)
            seedsArray.append(selectedSeeds)

        #     selectedSeeds = copy.copy(seedsForSequnetial)

        infectedNodesBySequential = set()
        copyGraph, step, totalInfected, timeArray = sequential_without_calculate.sequential(nr = numberOfCoordinatedExecution, network = name, pp = pp, step = step, graph = copyGraph, infectedNodes = infectedNodesBySequential, coordinatedExecution = coordinatedExecution, seeds = selectedSeeds, time = time, limit = limit, timeArray = timeArray)

        #zlicz niezainfekowanych
        uninfected = copy.copy(calculateUninfected(copyGraph))

        # usuwam wykorzystane seedy z tablicy
        if (len(seedsForSequnetial) > seeds):
            del seedsForSequnetial[:seeds]
        else:
            seedsForSequnetial = []

        seedsForSequnetial = [node for node in seedsForSequnetial if node not in infectedNodesBySequential]
        # usunięcie zainfekowanych węzłów z listy seedów
        # for i in reversed(range(len(seedsForSequnetial))):
        #     seedName = seedsForSequnetial[i]
        #     node = copyGraph.vs.select(name=seedName)[0]
        #
        #     if node['infected'] == 1:
        #         del seedsForSequnetial[i]

        # newSeedsForSequential = []
        #
        # for seed in seedsForSequnetial:
        #     node = copyGraph.vs.select(name=seed)[0]
        #
        #     if node['infected'] != 1:
        #         newSeedsForSequential.append(seed)
        #
        # seedsForSequnetial = newSeedsForSequential


    myFields = ['nr', 'nazwa', 'pp', 'numberOfSeeds', 'seeds', 'totalNumberOfSeeds', 'numberOfNodes', 'steps', 'infectedTotal', 'infectedTotalPercentage', 'computionalTime', 'limitPercentage']

    myFile = open(str(pp) + '_' + str(limit) + '_results_without_calculate_last.csv', 'a')
    with myFile:
        writer = csv.DictWriter(myFile, fieldnames=myFields)
        writer.writerow({'nr': numberOfCoordinatedExecution, 'nazwa': name, 'pp': pp, 'numberOfSeeds': seeds, 'seeds': seeds,
                         'totalNumberOfSeeds': calculateNumberOfSeeds(copyGraph), 'numberOfNodes': len(copyGraph.vs), 'steps': step, 'infectedTotal': len(totalInfected),
                         'infectedTotalPercentage': len(totalInfected) / len(copyGraph.vs) * 100, 'computionalTime': [], 'limitPercentage': limit})
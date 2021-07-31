import sequential_with_calculate
import pandas as pd
import networkx as nx
import copy
import csv
from timeit import default_timer as timer
from datetime import timedelta
import random
import sys
sys.path.insert(0, '..')


def checkIsUniqeAndOverwrite(vote_rank, forSequential, graph):
    # print('checkIsUniqeAndOverwrite', vote_rank)

    if len(set(vote_rank)) == len(vote_rank):
        return vote_rank
    else:
        new_vote_rank = (list(set(vote_rank)) + selectSeedsRandomly(graph, 1))
        return checkIsUniqeAndOverwrite(new_vote_rank, forSequential, graph)

# metoda oblicza h-index
def selectSeeds(graph, forSequential):
    start = timer()



    # vote_rank = nx.voterank(createNxGraph(graph), int(forSequential))
    degrees = [node for (node, val) in sorted(createNxGraph(graph).degree, key=lambda pair: pair[1], reverse=True)]
    degrees = degrees[0: forSequential]

    end = timer()



    if(len(degrees) < forSequential):
        degrees = selectSeedsRandomly(graph, forSequential)


    degrees = checkIsUniqeAndOverwrite(copy.copy(degrees), forSequential, graph)


    return degrees, timedelta(seconds=end-start)
    # return degrees[0:forSequential], timedelta(seconds=end-start)


def selectSeedsRandomly(graph, forSequential):
    ids = [v['name'] for v in graph.vs]


    if(len(ids) >= forSequential):
        return random.choices(ids, k=forSequential)
    else:
        return ids


# metoda do wycięcia grafu jedynie z niezainfekowanymi węzłami
def selectSeedsUninfected(graph, forSequential):

    # wyrzucam tutaj z sieci zainfekowane węzły
    try:
        to_delete_ids = [v.index for v in graph.vs if 1 is v['infected']]
    except:
        to_delete_ids = []

    uninfectedGraph = copy.copy(graph)

    # usunięcie po idkach ale pamiętać że ciągle kierujemy się attr NAME!!!!
    uninfectedGraph.delete_vertices(to_delete_ids)

    return selectSeeds(graph = uninfectedGraph, forSequential = forSequential)


# metoda a właściwie marshaller do reprezentacji nie przez indexy a przez nazwy, (ciągle kierujemy się nazwami a nie idkami!!!)
def mapEdgeList(graph, edgeList):
    mapped = []

    for edge in edgeList:
        mapped.append([graph.vs.select(edge[0])[0]['name'], graph.vs.select(edge[1])[0]['name']])

    return mapped

# metoda do utowrzenia grafu zrozumiałego przez networkx w celu obliczenia voteranka
def createNxGraph(graph):
    A = mapEdgeList(graph, graph.get_edgelist())
    return nx.Graph(A)

def calculateLimiForSeeding(graph, limit):
    return int(int(len(graph.vs) * limit)/100)

def calculateNumberOfSeeds(graph):
    if(len(graph.vs) > 0):
        seeds = [v.index for v in graph.vs if 1 is v['isSeed']]
        # print('SEEDS', seeds, len(seeds))
    else:
        seeds = []
    return len(seeds)


def flatten(t):
    return [item for sublist in t for item in sublist]


def simulation(pp, seeds, graph, coordinatedExecution, numberOfCoordinatedExecution, name, limit):

    copyGraph = copy.copy(graph)
    step = 1;
    seedsArray = []
    timeArray = []

    limitForSeeding = calculateLimiForSeeding(copyGraph, limit)

    if (seeds > limitForSeeding):
        seedsForSequnetial, time = selectSeedsUninfected(graph = copyGraph, forSequential = limitForSeeding)
    else:
        seedsForSequnetial, time = selectSeedsUninfected(graph = copyGraph, forSequential = seeds)

    seedsArray.append(seedsForSequnetial)
    timeArray.append(time)

    # print('limitForSeeding', limitForSeeding)
    # print('seedsArray', seedsArray)


    while(len(seedsForSequnetial) > 0 and len(flatten(seedsArray)) <= limitForSeeding):

        infectedNodesBySequential = []
        copyGraph, step, totalInfected, timeArray = sequential_with_calculate.sequential(nr = numberOfCoordinatedExecution, network = name, pp = pp, step = step, graph = copyGraph, infectedNodes = infectedNodesBySequential, coordinatedExecution = coordinatedExecution, seeds = seedsForSequnetial, time = time, limit = limit, timeArray = timeArray)

        # przeliczam co krok ranking
        if(len(flatten(seedsArray)) + seeds > limitForSeeding):
            seedsForSequnetial, time = selectSeedsUninfected(graph = copyGraph, forSequential=limitForSeeding-len(flatten(seedsArray)))
        else:
            seedsForSequnetial, time = selectSeedsUninfected(graph = copyGraph, forSequential=seeds)
        seedsArray.append(seedsForSequnetial)
        timeArray.append(time)
        # print('seedsForSequnetial', seedsForSequnetial, time)

        # print('seedsForSequnetial', seedsForSequnetial)

    myFields = ['nr', 'nazwa', 'pp', 'numberOfSeeds', 'seeds', 'totalNumberOfSeeds', 'numberOfNodes', 'steps',
                'infectedTotal', 'infectedTotalPercentage', 'computionalTime', 'limitPercentage']

    myFile = open(str(pp) + '_' + str(limit) + '_results_with_calculate_last.csv', 'a')
    with myFile:
        writer = csv.DictWriter(myFile, fieldnames=myFields)
        writer.writerow(
            {'nr': numberOfCoordinatedExecution, 'nazwa': name, 'pp': pp, 'numberOfSeeds': seeds, 'seeds': seeds,
             'totalNumberOfSeeds': calculateNumberOfSeeds(copyGraph), 'numberOfNodes': len(copyGraph.vs), 'steps': step,
             'infectedTotal': len(totalInfected),
             'infectedTotalPercentage': len(totalInfected) / len(copyGraph.vs) * 100, 'computionalTime': [],
             'limitPercentage': limit})
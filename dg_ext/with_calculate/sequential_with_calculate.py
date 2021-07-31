from igraph import *
import random
import csv

def calculateNumberOfSeeds(graph):
    seeds = [v.index for v in graph.vs if 1 is v['isSeed']]
    return len(seeds)

def sequential(nr, network, pp, step, graph, infectedNodes, coordinatedExecution, seeds, time, limit, timeArray):


    myFields = ['nr', 'nazwa', 'pp', 'numberOfSeeds', 'seeds','totalNumberOfSeeds', 'step', 'infectedPerStep', 'infectedTotal', 'infectedTotalPercentage', 'computionalTime', 'limitPercentage']

    nodes = Graph.vcount(graph)



    # print('number of nodes => ', nodes)
    # print('pp => ', pp)
    if(step == 1):
        for i in range(0, nodes):
            graph.vs[i]["infected"] = 0
            graph.vs[i]["used"] = 0
            graph.vs[i]["stepinfected"] = 0
            graph.vs[i]["isSeed"] = 0

    infections = 0
    isInfecting = True

    # for index, node in seeds.iterrows():
    for name in seeds:

        node = graph.vs.select(name=name)[0]
        # print(node, graph.neighbors(name, mode="out"))

        node["infected"] = 1

        if(step > 1):
            node["stepinfected"] = step
        else:
            node["stepinfected"] = 0

        node["used"] = 0
        node["color"] = "green"
        node["isSeed"] = 1


    infections = 0;

    # for v in graph.vs:
    #     print('in sequential', v)

    while(isInfecting):

        infecting = infections
        infectionsPerStep = 0

        for j in range(0, nodes):

            if (graph.vs[j]["infected"] == 1 and graph.vs[j]["used"] == 0 and graph.vs[j]["stepinfected"] != step):

                graph.vs[j]["used"] = 1
                neighborstab = graph.neighbors(j, mode="out")

                if (len(neighborstab) > 0):

                    n = 0
                    notinfected = []
                    for i in range(0, len(neighborstab)):
                        if (graph.vs[neighborstab[i]]["infected"] == 0):
                            notinfected.append(neighborstab[i])

                    numberofneighbors = len(notinfected)

                    if notinfected:
                        for k in notinfected:

                            if (numberofneighbors >= 1):

                                x = coordinatedExecution.loc[((coordinatedExecution['source'] == graph.vs[j]['name']) & (
                                        coordinatedExecution['target'] == graph.vs[[k]]['name'][0])), 'weight'].iloc[0]

                                if x <= pp:
                                    # print('zarażony')

                                    graph.vs[k]["infected"] = 1
                                    graph.vs[k]["stepinfected"] = step
                                    graph.vs[k]["used"] = 0
                                    graph.vs[k]["color"] = "blue"

                                    infections = infections + 1
                                    infectionsPerStep = infectionsPerStep + 1

                                    infectedNodes.append(graph.vs[k]['name'])

            # TODO: TO DO WYNIESIENIA

        totalInfected = [v.index for v in graph.vs if 1 is v['infected']]

        myFile = open(str(pp) + '_' + str(limit) + '_results_with_calculate.csv', 'a')
        with myFile:
            writer = csv.DictWriter(myFile, fieldnames=myFields)
            writer.writerow({'nr': nr, 'nazwa': network, 'pp': pp, 'numberOfSeeds': len(seeds), 'seeds': seeds, 'totalNumberOfSeeds': calculateNumberOfSeeds(graph), 'step': step,
                             'infectedPerStep': infectionsPerStep, 'infectedTotal': len(totalInfected),  'infectedTotalPercentage': len(totalInfected) / nodes * 100, 'computionalTime': [],
                             'limitPercentage': limit})

            # TUTAJ????
            timeArray.append(time)

        step = step + 1

        if (infecting == infections):
            isInfecting = False

    # plot(graph)
    # print('infections', infections + len(seeds))
    # print('infections', (infections + len(seeds)) / nodes * 100)
    # print('infectedNodes', infectedNodes)

    return graph, step, totalInfected, timeArray

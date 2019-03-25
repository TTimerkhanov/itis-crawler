import json
import math
import os

import numpy as np
import pandas


def create_nodes(matrix):
    nodes = set()
    for colKey in matrix:
        nodes.add(colKey)
    for rowKey in matrix.T:
        nodes.add(rowKey)
    return nodes


def read_in(adj_list):
    transition_mat = []

    for i in range(len(adj_list) + 1):
        transition_mat.append([0] * (len(adj_list) + 1))
        if str(i) in adj_list:
            links = adj_list[str(i)]
            for link in links:
                transition_mat[i][int(link)] = float(1.0)
        else:
            transition_mat[i] = list(map(lambda x: 1 / len(transition_mat[i]), transition_mat[i]))

    array = np.array(transition_mat)
    return array


def pageRank(transition_matrix, max_iterations, epsilon):
    transition_matrix = pandas.DataFrame(transition_matrix)
    # creating initial graph
    nodes = set()
    for colKey in transition_matrix:
        nodes.add(colKey)
    for rowKey in transition_matrix.T:
        nodes.add(rowKey)

    # makes sure values are positive
    matrix = transition_matrix.T
    for colKey in matrix:
        if matrix[colKey].sum() == 0.0:
            matrix[colKey] = pandas.Series(np.ones(len(matrix[colKey])), index=matrix.index)
    transition_matrix = matrix.T

    # normalization
    normalize = 1.0 / float(len(nodes))
    P_matrix = pandas.Series({node: normalize for node in nodes})

    # normalizes the rows
    transitionProbs = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)

    # iterate until convergence
    for iteration in range(max_iterations):
        old = P_matrix.copy()
        P_matrix = P_matrix.dot(transitionProbs)
        delta = P_matrix - old
        if math.sqrt(delta.dot(delta)) < epsilon:
            break

    return P_matrix


MAX_ITERATIONS = 100
EPSILON = 0.01
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_DIR, 'adjList.json')
MAPPING_PATH = os.path.join(CURRENT_DIR, 'IdUrlMapping.json')

if __name__ == "__main__":
    adj_list = json.load(open(FILE_PATH))
    array = read_in(adj_list)
    pr = pageRank(array, max_iterations=MAX_ITERATIONS, epsilon=EPSILON)

    print(pr.sort_values(ascending=False))

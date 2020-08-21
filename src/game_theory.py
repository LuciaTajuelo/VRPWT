
from itertools import permutations
from itertools import combinations
import math
import bisect
import pandas as pd
import sys
import os as os
import time as time 

import src.read as read

def power_set(List):
    return [tuple(j) for i in range(len(List)) for j in combinations(List, i+1)]

def compute_shapley_value(n, l_characteristic_function):

    # Compute combinations
    l_comb = power_set(range(1,n+1))
    l_permutation = [list(i) for i in list(permutations(range(1,n+1),n))]

    # Parse characteristic function values
    d_characteristic_function = {l_comb[i]:l_characteristic_function[i+1] for i in range(len(l_comb))}
    d_characteristic_function = \
        {iPermutation: d_characteristic_function[i] \
            for i in [iKey for iKey in d_characteristic_function.keys()] \
            for iPermutation in list(permutations(i,len(i)))}
    d_characteristic_function[tuple([])] = l_characteristic_function[0]

    # Compute Shapley value
    l_shapley = [sum([d_characteristic_function[tuple(iPermutation[0:iPermutation.index(iCustomer)+1])] \
        - d_characteristic_function[tuple(iPermutation[0:(iPermutation.index(iCustomer))])]
        for iPermutation in l_permutation]) for iCustomer in range(1, n+1)]

    return [round(i / math.factorial(n), 2) for i in l_shapley]

def compute_EPM(n_customer, l_characteristic_function):

    l_coalition = power_set(range(1,n_customer+1))
    l_permutation = list(permutations(range(1,n_customer+1),2))

    # Parse characteristic function values
    d_characteristic_function = {l_coalition[i]:l_characteristic_function[i+1] for i in range(len(l_coalition))}
    d_characteristic_function = \
        {iPermutation: d_characteristic_function[i] \
            for i in [iKey for iKey in d_characteristic_function.keys()] \
            for iPermutation in list(permutations(i,len(i)))}
    d_characteristic_function[tuple([])] = l_characteristic_function[0]

    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("EPM2", LpMinimize)

    # A dictionary called 'ingredient_vars' is created to contain the referenced Variables
    y_vars = LpVariable.dicts("y",range(1,n_customer+1),0)
    f = LpVariable.dicts("f",range(1),0)

    # The objective function is added to 'prob' first
    prob += lpSum(f)

    # Constraint 1
    for iPermutation in l_permutation:
        prob += (y_vars[iPermutation[0]]*(1/l_characteristic_function[iPermutation[0]])\
            - y_vars[iPermutation[1]]*(1/l_characteristic_function[iPermutation[1]])) <= f, "c1" + str(iPermutation)

    # Constraint 2
    for iColation in l_coalition[:-2]:
        prob += lpSum([y_vars[i] for i in iColation]) <= d_characteristic_function[iColation] , "c2" + str(iColation)

    prob += lpSum([y_vars[i] for i in l_coalition[-1]]) == d_characteristic_function[l_coalition[-1]] , "c2" + str('grancolition')

    # The problem data is written to an .lp file
    prob.writeLP("EMP.lp")

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The status of the solution is printed to the screen
    print ("Status:", LpStatus[prob.status])

    return [v.varValue for v in prob.variables() if v.name != 'f_0']

def compute_Lorenz(n_customer, l_characteristic_function):

    l_coalition = power_set(range(1,n_customer+1))
    l_permutation = list(permutations(range(1,n_customer+1),2))

    # Parse characteristic function values
    d_characteristic_function = {l_coalition[i]:l_characteristic_function[i+1] for i in range(len(l_coalition))}
    d_characteristic_function = \
        {iPermutation: d_characteristic_function[i] \
            for i in [iKey for iKey in d_characteristic_function.keys()] \
            for iPermutation in list(permutations(i,len(i)))}
    d_characteristic_function[tuple([])] = l_characteristic_function[0]

    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("Lorenz", LpMinimize)

    # A dictionary called 'ingredient_vars' is created to contain the referenced Variables
    y_vars = LpVariable.dicts("y",range(1,n_customer+1),0)
    f = LpVariable.dicts("f",range(1),0)

    # The objective function is added to 'prob' first
    prob += lpSum(f)

    # Constraint 1
    for iPermutation in l_permutation:
        prob += (y_vars[iPermutation[0]] - y_vars[iPermutation[1]]) <= f, "c1" + str(iPermutation)

    # Constraint 2
    for iColation in l_coalition[:-2]:
        prob += lpSum([y_vars[i] for i in iColation]) <= d_characteristic_function[iColation] , "c2" + str(iColation)

    prob += lpSum([y_vars[i] for i in l_coalition[-1]]) == d_characteristic_function[l_coalition[-1]] , "c2" + str('grancolition')

    # The problem data is written to an .lp file
    prob.writeLP("EMP.lp")

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The status of the solution is printed to the screen
    print ("Status:", LpStatus[prob.status])

    return [v.varValue for v in prob.variables() if v.name != 'f_0']

def main(file_name, l_solution_route, value):

    # Read data
    d_instance_data = read.read_file(file_name)

    d_values = {}
    for route_initial in l_solution_route:

        number_customer_route = len(route_initial)-2
    
        # Compute characteristic function
        l_comb = power_set([i for i in route_initial if i != 0])
        l_characteristic_function = [round(sum([ d_instance_data['distance'][\
                    [i for i in route_initial if i in list(iComb)+[0]][i],
                    [i for i in route_initial if i in list(iComb)+[0]][i + 1]]\
                    for i in range(0, len([i for i in route_initial if i in list(iComb)+[0]])-1)]),2) for iComb in l_comb]
        l_characteristic_function.insert(0,0)

        # Compute Shapley value
        if value == 'Shapley':
            l_value = compute_shapley_value(number_customer_route, l_characteristic_function)
        elif value == 'EPM':
            l_value = compute_EPM(number_customer_route, l_characteristic_function)
        elif value == 'Lorenz':
            l_value = compute_Lorenz(number_customer_route, l_characteristic_function)

        print(route_initial)
        print(', '.join([str(route_initial[i]) +': '+str(l_value[i-1]) for i in range(1,len(route_initial)-1)]))
        print(', '.join([str(l_value[i-1]) for i in range(1,len(route_initial)-1)]))
        for i in range(len(l_value)):
            d_values[route_initial[i+1]]=l_value[i]
        print('min value:', min(list(d_values.values())))
        print('max value:', max(list(d_values.values())))
        print('standar deviation:', min(np.stdlist(d_values.values()))))

    return d_values


file_name = 'C:\\Users\\lucia\\Desktop\\Desktop\\TFM-VRP\\src\\data\\solomon_100\\RC105.txt'
l_solution_route=[[0,90, 53, 66, 56,0], [0,63, 62, 67, 84, 51, 85, 91,0],\
    [0,72, 71, 81, 41, 54, 96, 94, 93,0],\
    [0,65, 82, 12, 11, 87, 59, 97, 75 ,58,0],\
    [0,33, 76, 89, 48, 21, 25, 24,0],\
    [0,98, 14, 47, 15, 16, 9 ,10, 13, 17,0],\
    [0,42, 61, 8, 6, 46 ,4 ,3, 1, 100,0],\
    [0,39, 36, 44, 38, 40, 37, 35, 43, 70,0],\
    [0,83, 19, 23, 18, 22, 49, 20, 77,0],\
    [0,31, 29, 27, 30, 28, 26, 32, 34, 50, 80,0],\
    [0,92, 95, 64, 99, 52, 86, 57, 74,0],\
    [0,69, 88, 78, 73, 60, 0],\
    [0,2, 45, 5, 7, 79, 55, 68,0]]

t0 = time.time()
HOLA = main(file_name, l_solution_route, 'Lorenz')
t1 = time.time()
t1 -t0

t00 = time.time()
HOLA1 = main(file_name, l_solution_route, 'EPM')
t11 = time.time()
t11 -t00

t000 = time.time()
HOLA2 = main(file_name, l_solution_route, 'Shapley')
t111 = time.time()
t111 -t000

import numpy as np

np.std(list(HOLA.values()))
max(list(HOLA.values()))
min(list(HOLA.values()))


np.std(list(HOLA1.values()))
max(list(HOLA1.values()))
min(list(HOLA1.values()))



HOLA
for ii in range(1,len(HOLA1)+1, 4):
    print(' & '.join([ str(i) + ' & ' + str(round(HOLA1[i], 2)) for i in range(ii, ii + 4)] ))

    
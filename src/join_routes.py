
import pandas as pd
import copy as cp
import pickle as pickle
import xlrd as xlrd
import src.read as read
import src.initial_solution as initial_solution
import src.improve_solution as join
import src.Kernighan_Lin as LK
import os as os

import src.solution_data as arrival
import src.unfeasible as check
import time as time

import numpy as np
import src.common_functions as fun
import src.solution_data as arrival
import src.unfeasible as check
import time as time

def create_solution_new(file_name, df_new_sol, size, folder, l_beta):

    d_instance_data = read.read_file(os.path.join('src', 'data', 'solomon_'+  str(size), file_name))

    t0 = time.time()
    d_config = {
        'n_cluster': 1,
        'alpha1': 1,
        'alpha2': 0,
        'alpha3': 0,
        'nu': 1,
        'beta': 1,
        'MaxIter': 200,
        'criterio' : [['n_truck','dist'], [True, True]]
    }

    d_solution = initial_solution.main_cluster(d_instance_data, d_config)

    k = 0
    stop = 0
    n_iter = 0

    iter_value = {
        'n_truck' : d_solution['n_truck'],
        'dist' : d_solution['dist']
    }

    d_config['alpha1'] = 1
    d_config['alpha2'] = 0
    d_config['alpha3'] = 0
    
    k = 0
    stop = 0
    n_iter = 0
    no_solution = 0

    d_list_solution = {}
    d_list_solution[0] = d_solution
    k_sol = 1

    while n_iter < len(l_beta):
        stop = 0
        d_config['beta'] = l_beta[n_iter]
        d_solution = join.main_join(d_instance_data, d_solution, d_config)

        n_iter = n_iter + 1

    t1 = time.time()

    d_solution['time'] = t1-t0

    file_name_output = file_name.replace('txt', 'pickle')
    file_name_output = os.path.join(folder, file_name_output)  

    if no_solution == 0:
        d_solution['l_beta'] = l_beta
        with open(file_name_output + '.pickle', 'wb') as f:
            pickle.dump(d_solution, f)

        df_new_sol.append([
            file_name.replace('txt', ''),
            iter_value['n_truck'],
            iter_value['dist'],
            t1-t0, ' '.join([str(i) for i in l_beta])
        ])

    return df_new_sol

def join_route(d_instance_data, d_solution, iTruck1, iTruck2, d_config):

    d_solution_improve = cp.deepcopy(d_solution)

    k = 0
    k_iter = 0
    stop_route = 0

    while stop_route == 0:
            
        StopAlgoritmo = 0

        while StopAlgoritmo != -1:

            stop = 1
            matrix = create_insertion_matrix(d_instance_data, d_solution_improve, iTruck1, iTruck2)
            mParametrosInsercion = matrix['mParametrosInsercion']
            StopAlgoritmo = matrix['StopAlgoritmo']

            while stop != 0 and StopAlgoritmo != -1:

                if len(mParametrosInsercion)>1:
                    iRow = fun.get_random_number(len(mParametrosInsercion['SC11']), d_config['beta'])
                else:
                    iRow = 0

                iPosition1 = int(mParametrosInsercion.iloc[iRow]['customer1'])
                iPosition2 = int(mParametrosInsercion.iloc[iRow]['customer2'])
                iCandidate = d_solution_improve['truck'][iTruck1][iPosition1]

                d_solution_improve_temp = cp.deepcopy(d_solution_improve)
                d_solution_improve_temp['truck'][iTruck1].remove(iCandidate)
                d_solution_improve_temp['truck'][iTruck2].insert(iPosition2 + 1, iCandidate)

                d_solution_improve_temp = arrival.arrival_time(d_instance_data, d_solution_improve_temp)
                stop = check.basic_check(d_instance_data, d_solution_improve_temp)

                if stop == 0:
                    d_solution_improve = cp.deepcopy(d_solution_improve_temp)
                    k = k + 1
                else:
                    mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])

                if len(d_solution_improve['truck'][iTruck1]) <= 2:
                    StopAlgoritmo = -1
                if len(mParametrosInsercion) == 0:
                    StopAlgoritmo = -1

        if k_iter < k:
            k_iter = cp.deepcopy(k)
        else:
            stop_route = 1

    d_solution_improve = arrival.remove_empty_routes(d_solution_improve)
    d_solution_improve = arrival.arrival_time(d_instance_data, d_solution_improve)
    d_solution_improve = arrival.solution_metric(d_instance_data, d_solution_improve)
    d_solution_improve['k'] = k

    return d_solution_improve

def create_insertion_matrix(d_instance_data, d_solution, iTruck1, iTruck2):

    mParametrosInsercion = []
    StopAlgoritmo = 0
    dist = arrival.solution_metric(d_instance_data, d_solution)
    for iCustomer1 in range(1, len(d_solution['truck'][iTruck1]) - 1):
        for iCustomer2 in range(len(d_solution['truck'][iTruck2]) - 1):

            iClienteSinVisitar = d_solution['truck'][iTruck1][iCustomer1]
            iClienteEnRoutedo = d_solution['truck'][iTruck2][iCustomer2]
            iClienteEnRoutedo2 = d_solution['truck'][iTruck2][iCustomer2+1]
            
            d_solution_temp = cp.deepcopy(d_solution)
            d_solution_temp['truck'][iTruck1].remove(d_solution['truck'][iTruck1][iCustomer1])
            d_solution_temp['truck'][iTruck2].insert(iCustomer2 + 1, d_solution['truck'][iTruck1][iCustomer1])
            dist_iter = arrival.solution_metric(d_instance_data, d_solution_temp)
        

            SC12 = d_instance_data['distance'][iClienteEnRoutedo, iClienteSinVisitar] \
                    + d_instance_data['distance'][iClienteEnRoutedo2, iClienteSinVisitar]\
                    + d_instance_data['service_time'][iClienteSinVisitar]\
                    - d_instance_data['distance'][iClienteEnRoutedo, iClienteEnRoutedo2]
            
            SC13 = d_instance_data['late_time'][iClienteSinVisitar] \
                - (d_solution['arrival']['truck'][iTruck2][iCustomer2] \
                + d_instance_data['distance'][iClienteEnRoutedo, iClienteSinVisitar])

            dist_df = dist_iter['dist'] - dist['dist']

            mParametrosInsercion.append([iCustomer1, iCustomer2, dist_df, SC12, SC13])

    if len(mParametrosInsercion) == 0:
        StopAlgoritmo = -1
    else:

        mParametrosInsercion = pd.DataFrame(mParametrosInsercion, 
        columns = ['customer1', 'customer2' ,'SC11', 'SC12','SC13'])
        
        mParametrosInsercion = fun.get_index(mParametrosInsercion, 'SC11', False)

        mParametrosInsercion = mParametrosInsercion.sort_values(by = ['SC11'])
        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

    return {
        'mParametrosInsercion' : mParametrosInsercion,
        'StopAlgoritmo' : StopAlgoritmo
    }

def get_center(d_instance_data, d_solution):

    d_center = {}
    for iKey in d_solution['truck'].keys():
        l_node = list(set(d_solution['truck'][iKey]))
        l_node.remove(0)

        l_x = [d_instance_data['cord_x'][iNode] for iNode in l_node]
        l_y = [d_instance_data['cord_y'][iNode] for iNode in l_node]
        d_center[iKey] = {
            'cord_x' : np.mean(l_x),
            'cord_y' : np.mean(l_y)
        }

    df_combinations = []
    for iKey1 in d_center.keys():
        for iKey2 in range(iKey1 + 1, len(d_center.keys())):
            if len(d_solution['truck'][iKey1]) == 2:
                len1 = 1
            else:
                len1 = len(d_solution['truck'][iKey1]) - 2
            if len(d_solution['truck'][iKey2]) == 2:
                len2 = 1
            else:
                len2= len(d_solution['truck'][iKey1]) - 2

            frac1 = ( 1 / len1) + (1 / len2)
            frac2 = 1 / (len1 + len2)

            df_combinations.append([ iKey1, iKey2, 
                ( \
                (d_center[iKey1]['cord_x'] - d_center[iKey2]['cord_x']) ** 2 \
                + \
                (d_center[iKey1]['cord_y'] - d_center[iKey2]['cord_y']) ** 2 \
                ) ** (1 / 2)]) 

    df_combinations = pd.DataFrame(df_combinations)
    df_combinations = df_combinations.sort_values(by = [2])

    return df_combinations

def kerninghan_insertsdasdas(d_instance_data, route, d_config, iCandidate):

    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    StopAlgoritmo = 0
    stop = 1
    mParametrosInsercion = []

    dist_ini = arrival.route_metric(d_instance_data, route)
    
    for iCustomer1 in range(1, len(route) - 3):
        for iCustomer2 in range(iCustomer1, len(route) - 2):
            for iCustomer3 in range(iCustomer2, len(route) - 1):
                if iCustomer1 != iCustomer3:
                    route_aux = cp.deepcopy(route)
                    route_aux[iCustomer1] = cp.deepcopy(route[iCustomer3])
                    route_aux[iCustomer3] = cp.deepcopy(route[iCustomer1])

                    route_aux.insert(iCustomer2, iCandidate)
                    
                    dist_iter = arrival.route_metric(d_instance_data, route_aux) - dist_ini
                    mParametrosInsercion.append([iCustomer1, iCustomer2, iCustomer3, dist_iter])
    
    while stop != 0 and StopAlgoritmo != -1 :
        # Se ordenan
        mParametrosInsercion = pd.DataFrame(mParametrosInsercion)
        mParametrosInsercion = mParametrosInsercion.sort_values(by=[3], ascending= True)

        if (len(mParametrosInsercion)>1):
            iRow = fun.get_random_number(len(mParametrosInsercion[0]), d_config['beta'])
        else:
            iRow = 0

        iPosicion1 = int(mParametrosInsercion.iloc[iRow][0])
        iPosicion2 = int(mParametrosInsercion.iloc[iRow][1])
        iPosicion3 = int(mParametrosInsercion.iloc[iRow][2])

        route_aux = cp.deepcopy(route)
        route_aux[iPosicion1] = cp.deepcopy(route[iPosicion3])
        route_aux[iPosicion3] = cp.deepcopy(route[iPosicion1])

        route_aux.insert(iPosicion2, iCandidate)
        
        d_arrival = arrival.arrival_time_route(d_instance_data, route_aux)
        d_arrival['truck'] = {}
        d_arrival['truck'][0] = route_aux

        stop = check.basic_check(d_instance_data, d_arrival)

        if stop == 0:

            route_aux = arrival.arrival_time(d_instance_data, d_arrival)
            route_aux = arrival.solution_metric(d_instance_data, route_aux)

            route = cp.deepcopy(route_aux['truck'][0])

        else:
            mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])
        
        if len(mParametrosInsercion)==0:
            StopAlgoritmo = -1
    
    return {
        'route': route,
        'stop' : stop
    }


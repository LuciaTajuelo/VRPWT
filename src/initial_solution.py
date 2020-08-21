
import sklearn.cluster as cl
import pandas as pd
import numpy as np
import copy as cp

import src.solution_data as arrival
import src.unfeasible as check
import src.common_functions as fun
import src.Kernighan_Lin as LK

def dummy_solution(d_instance_data):

    d_solution = {}
    d_solution['truck'] = {\
        iCliente - 1 : [0, iCliente, 0] \
            for iCliente in range(1, d_instance_data['n_customer'] + 1)}

    d_solution = arrival.remove_empty_routes(d_solution)
    d_solution = arrival.arrival_time(d_instance_data, d_solution)
    d_solution['error'] = check.complete_check(d_instance_data, d_solution)
    d_solution = arrival.solution_metric(d_instance_data, d_solution)

    return d_solution

def cluster(d_instance_data, d_config):
    """
    Crea una d_solution agrupando clientes y siguiendo el criterio de insercion de Solomon en cada uno de los grupos

    :param file: archivo a resolver
    :param nCluster: numero de grupos
    :param ParametrosCluster: parametros de insercion y probabilistico
    :return
    - d_solution inicial
    """

    # Clustering
    df_cord = [[d_instance_data['cord_x'][iCustomer], d_instance_data['cord_y'][iCustomer]]\
        for iCustomer in range(1, d_instance_data['n_customer'] + 1)]

    kmeans = cl.KMeans(d_config['n_cluster'])
    kmeans.fit(df_cord)
    cluster = kmeans.fit_predict(df_cord)

    d_customer_cluster = {\
        i: cluster[i]\
        for i in range(0, len(df_cord))}

    d_cluster_customer = {\
            iCluster: [iCliente + 1 for iCliente, iiCluster in d_customer_cluster.items()\
            if iiCluster == iCluster] for iCluster in range(0, d_config['n_cluster'])
        }

    # Declaracion inicial
    sVisit = d_cluster_customer
    sVisitedCustomer = []
    
    d_solution = {}
    d_solution['truck'] = {}

    d_solution_aux = {}
    d_solution_aux['truck'] = {}

    NoFeasibleroute = 0

    # Para cada cluster se calcula una d_solution
    for iCluster in d_cluster_customer.keys():
        # Se inicializa la d_solution del cluster
        d_solution['truck'][iCluster] = [0,0]
        d_solution = arrival.arrival_time(d_instance_data, d_solution)

        stop = 0

        while stop == 0 and NoFeasibleroute != 1 and len (sVisit[iCluster])>0:

            # Se calcula los parametros de insercicion
            df_insertion_criteria = [
                [d_instance_data['distance'][d_solution['truck'][iCluster][i], iClienteSinVisitar] \
                    + d_instance_data['distance'][d_solution['truck'][iCluster][i+1], iClienteSinVisitar]\
                    - d_config['nu'] * d_instance_data['distance'][d_solution['truck'][iCluster][i], d_solution['truck'][iCluster][i+1]],
                d_instance_data['distance'][d_solution['truck'][iCluster][i], iClienteSinVisitar] \
                    + d_instance_data['distance'][d_solution['truck'][iCluster][i+1], iClienteSinVisitar]\
                    + d_instance_data['service_time'][iClienteSinVisitar]\
                    - d_instance_data['distance'][d_solution['truck'][iCluster][i], d_solution['truck'][iCluster][i+1]],
                d_instance_data['late_time'][iClienteSinVisitar] \
                    - (d_solution['arrival']['truck'][iCluster][i] \
                    + d_instance_data['distance'][d_solution['truck'][iCluster][i], iClienteSinVisitar]),
                iClienteSinVisitar, i + 1]
                for i in range(0, len(d_solution['truck'][iCluster])-1) \
                for iClienteSinVisitar in d_cluster_customer[iCluster]
            ]
            #Se ordenan
            df_insertion_criteria = pd.DataFrame(df_insertion_criteria, \
                columns = ['SC11', 'SC12', 'SC13', 'customer', 'location'])

            df_insertion_criteria = df_insertion_criteria[df_insertion_criteria['SC13'] >= 0]

            df_insertion_criteria['coef'] = \
                d_config['alpha1'] * df_insertion_criteria['SC11'] \
                + d_config['alpha2'] * df_insertion_criteria['SC12'] \
                + d_config['alpha3'] * df_insertion_criteria['SC13'] 

            df_insertion_criteria = df_insertion_criteria.sort_values(by = ['coef'])

            #Se escoge el candidato por aleatorizacion sesgada
            stop = 1
            if len(df_insertion_criteria) == 0 :
                NoFeasibleroute = 1

            while stop == 1 and NoFeasibleroute != 1:
                if len(df_insertion_criteria)>1:
                    iRow = fun.get_random_number(len(df_insertion_criteria['SC11']), d_config['beta'])

                else:
                    iRow = 0

                iCustomer = int(df_insertion_criteria.iloc[int(iRow)]['customer'])
                iPosition = int(df_insertion_criteria.iloc[int(iRow)]['location'])

                d_solution_aux = cp.deepcopy(d_solution)
                d_solution_aux['truck'][iCluster].insert(iPosition, iCustomer)
                
                #Comprobar restricciones
                d_solution_aux = arrival.arrival_time(d_instance_data, d_solution_aux)
                stop = check.basic_check(d_instance_data, d_solution_aux)

                if len(df_insertion_criteria) == 1 and stop == 1:
                   NoFeasibleroute = 1

                if stop == 0:
                    
                    d_solution = cp.deepcopy(d_solution_aux)
                    sVisit[iCluster].remove(iCustomer)

                if len(df_insertion_criteria) > 1:
                    df_insertion_criteria = df_insertion_criteria.drop(df_insertion_criteria.index[int(iRow)])

    d_solution = arrival.remove_empty_routes(d_solution)
    d_solution = arrival.arrival_time(d_instance_data, d_solution)
    d_solution['error'] = check.complete_check(d_instance_data, d_solution)
    d_solution = arrival.solution_metric(d_instance_data, d_solution)
    
    return d_solution

def main_cluster(d_instance_data, d_config):

    stop = 0

    while stop == 0:
        d_solution = cluster(d_instance_data, d_config)
        if d_solution['error'] == 0:
            stop = 1
        else:
            d_config['n_cluster'] = d_config['n_cluster'] + 1

    return d_solution
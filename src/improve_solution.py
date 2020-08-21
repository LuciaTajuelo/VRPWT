
import copy as cp
import src.solution_data as solution_data
import pandas as pd
import numpy as np
import src.Kernighan_Lin as LK

import src.solution_data as arrival
import src.unfeasible as check
import src.common_functions as fun

def main_join(d_instance_data, d_solution, d_config):

    d_solution_saved = cp.deepcopy(d_solution)

    d_solution = cp.deepcopy(d_solution_saved)

    iter_value = {
        'n_truck' : d_solution['n_truck'],
        'dist' : d_solution['dist']
        }

    stop = 0

    while stop == 0:
        Mejora = {}
        
        Mejora[0] = insert_routes(d_instance_data, d_solution, d_config,'ascending')
        Mejora[1] = insert_routes(d_instance_data, d_solution, d_config,'descending')
        Mejora[2] = exchange_routes2(d_instance_data, d_solution, d_config)
        Mejora[3] = LK.main_kerninghan_lin(d_instance_data, d_solution, d_config)

        mMejoras = [
            [iKey, Mejora[iKey]['n_truck'], Mejora[iKey]['dist']]
            for iKey in Mejora.keys()
        ]

        mMejoras = pd.DataFrame(mMejoras)
        mMejoras = mMejoras.sort_values(by=[1,2], ascending  = [True, True])

        if Mejora[mMejoras.index[0]]['n_truck'] < iter_value['n_truck']:
            d_solution = cp.deepcopy(Mejora[mMejoras.index[0]])
        elif Mejora[mMejoras.index[0]]['n_truck'] == iter_value['n_truck']:
            
            if mMejoras.iloc[0][2] < iter_value['dist']:
                d_solution = cp.deepcopy(Mejora[mMejoras.index[0]])
            else:
                stop = 1
        else:
            stop = 1
            print('error')
        
        iter_value = {
        'n_truck' : d_solution['n_truck'],
        'dist' : d_solution['dist']
        }

        print(iter_value)

    return d_solution

def exchange_routes(d_instance_data, d_solution, d_config, order):
    """
        Inserta cliente de una ruta en otro, con el fin de reducir el numero de rutas

        :param Ruta: Ruta a mejorar
        :param file: archivo a resolver

        :param ParametrosCluster: parametros de insercion y probabilistico

        :param orden: criterio para ordenar las rutas en funcion de su numero de clientes
            0 no se ordena
            1 ascendiente
            2 decreciente

        :param Criterio: seleccion candidado por distancia u horario pronto

        :return
        - Ruta
         """

    d_solution_saved = cp.deepcopy(d_solution)
    d_solution = solution_data.order_solution(d_instance_data, d_solution, order)

    mov_prov = {}
    for i in range(d_instance_data['n_customer'] + 1):
        mov_prov[i] = 0

    Mejora = {}
    Mejora[0] = d_solution_saved
    k = 1

    for iTruck1 in d_solution['truck'].keys():

        StopAlgoritmo = 0
        mov_prov[0] = 0

        while StopAlgoritmo != -1:

            stop = 1
            mParametrosInsercion = []

            for iCustomer1 in range(1, len(d_solution['truck'][iTruck1]) - 1):
                if mov_prov[d_solution['truck'][iTruck1][iCustomer1]] == 0:
                    for iTruck2 in range(iTruck1 + 1, len(d_solution['truck'].keys())):
                        for iCustomer2 in range(1, len(d_solution['truck'][iTruck2])-1):
                            if mov_prov[d_solution['truck'][iTruck2][iCustomer2]] == 0:
                                Ahorro = 0

                                Ahorro1 = d_instance_data['distance'][ \
                                                d_solution['truck'][iTruck1][iCustomer1 - 1], \
                                                d_solution['truck'][iTruck1][iCustomer1]] \
                                            + d_instance_data['distance'][ \
                                                d_solution['truck'][iTruck1][iCustomer1], \
                                                d_solution['truck'][iTruck1][iCustomer1 + 1]] \
                                            + d_instance_data['distance'][ \
                                                d_solution['truck'][iTruck2][iCustomer2], \
                                                d_solution['truck'][iTruck2][iCustomer2 - 1]] \
                                             + d_instance_data['distance'][ \
                                                d_solution['truck'][iTruck2][iCustomer2], \
                                                d_solution['truck'][iTruck2][iCustomer2 + 1]] \
                                            - ( d_instance_data['distance'][
                                                d_solution['truck'][iTruck1][iCustomer1 - 1], \
                                                d_solution['truck'][iTruck2][iCustomer2]]
                                            + d_instance_data['distance'][
                                                    d_solution['truck'][iTruck2][iCustomer2], \
                                                    d_solution['truck'][iTruck1][iCustomer1 + 1]]
                                            + d_instance_data['distance'][
                                                    d_solution['truck'][iTruck2][iCustomer2 + 1], \
                                                    d_solution['truck'][iTruck1][iCustomer1]]
                                            + d_instance_data['distance'][
                                                    d_solution['truck'][iTruck1][iCustomer1], \
                                                    d_solution['truck'][iTruck2][iCustomer2 + 1]])


                                mParametrosInsercion.append([iTruck1, iCustomer1, iTruck2, iCustomer2, Ahorro, Ahorro1])

            nMovimiento = 0
            for iCustomer1 in d_solution['truck'][iTruck1]:
                if mov_prov[iCustomer1] == 1:
                    nMovimiento = nMovimiento + 1

            if len(d_solution['truck'][iTruck1]) - nMovimiento > 0:
                StopAlgoritmo = 0
            else:
                StopAlgoritmo = -1
            if len(mParametrosInsercion) == 0:
                StopAlgoritmo = -1
            else:
                mParametrosInsercion = pd.DataFrame(mParametrosInsercion)

            while stop != 0 and StopAlgoritmo != -1:
                # Se ordenan
                mParametrosInsercion = pd.DataFrame(mParametrosInsercion)
                mParametrosInsercion = mParametrosInsercion.sort_values(by=[5], ascending=False)

                if len(mParametrosInsercion)>1:
                    iRow = fun.get_random_number(len(mParametrosInsercion[0]), d_config['beta'])
                else:
                    iRow = 0

                iTruck1 = int(mParametrosInsercion.iloc[iRow][0])
                iPosition1 = int(mParametrosInsercion.iloc[iRow][1])
                iTruck2 = int(mParametrosInsercion.iloc[iRow][2])
                iPosition2 = int(mParametrosInsercion.iloc[iRow][3])
                iCandidate = d_solution['truck'][iTruck1][iPosition1]

                d_solution_temp = cp.deepcopy(d_solution)
                d_solution_temp['truck'][iTruck1][iPosition1] = d_solution['truck'][iTruck2][iPosition2]
                d_solution_temp['truck'][iTruck2][iPosition2] = d_solution['truck'][iTruck1][iPosition1]

                d_solution_temp = arrival.arrival_time(d_instance_data, d_solution_temp)
                stop = check.basic_check(d_instance_data, d_solution_temp)

                if stop == 0:
                    mov_prov[d_solution_temp['truck'][iTruck1][iPosition1]] = 1
                    mov_prov[d_solution_temp['truck'][iTruck2][iPosition2]] = 1
                    
                    d_solution = cp.deepcopy(d_solution_temp)

                    d_solution_temp = arrival.remove_empty_routes(d_solution_temp)
                    d_solution_temp = arrival.arrival_time(d_instance_data, d_solution_temp)
                    d_solution_temp = arrival.solution_metric(d_instance_data, d_solution_temp)

                    Mejora[k] = cp.deepcopy(d_solution_temp)
                    k = k + 1

                else:
                    mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])

                nMovimiento = 0
                for iCustomer1 in d_solution['truck'][iTruck1]:
                    if mov_prov[iCustomer1] == 1:
                        nMovimiento = nMovimiento + 1

                if len(d_solution['truck'][iTruck1]) - nMovimiento > 0:
                    StopAlgoritmo = 0
                else:
                    StopAlgoritmo = -1
                
                if len(d_solution['truck'][iTruck1]) <= 2:
                    StopAlgoritmo = -1
                if len(mParametrosInsercion) == 0:
                    StopAlgoritmo = -1

    mMejoras = []
    for iKey in Mejora.keys():
        mMejoras.append([iKey, Mejora[iKey]['n_truck'], Mejora[iKey]['dist']])

    if len(mMejoras) >= 1:
        mMejoras = pd.DataFrame(mMejoras)
        mMejoras = mMejoras.sort_values(by=[1,2])
        return Mejora[mMejoras.index[0]]
    elif len(mMejoras) == 0:
        return RutaSaved

def compute_dist_diference(d_instance_data, dist, d_solution, iTruck1, iTruck2, iCustomer1, iCustomer2):

    d_solution_temp = cp.deepcopy(d_solution)
    d_solution_temp['truck'][iTruck2][iCustomer2] = d_solution['truck'][iTruck1][iCustomer1] 
    d_solution_temp['truck'][iTruck1][iCustomer1] = d_solution['truck'][iTruck2][iCustomer2] 

    dist_iter = arrival.solution_metric(d_instance_data, d_solution_temp)

    dist_df = dist_iter['dist'] - dist['dist']
    
    return dist_df

def create_insertion_matrix_exchange(d_instance_data, d_solution):

    StopAlgoritmo = 0
    dist = arrival.solution_metric(d_instance_data, d_solution)

    mParametrosInsercion = [\
        [iTruck1, iCustomer1, iTruck2, iCustomer2, \
        compute_dist_diference(d_instance_data, dist, d_solution, iTruck1, iTruck2, iCustomer1, iCustomer2)]\
        for iTruck1 in d_solution['truck'].keys()
        for iCustomer1 in range(1, len(d_solution['truck'][iTruck1]) - 1)\
        for iTruck2 in range(iTruck1 + 1, len(d_solution['truck'].keys()))\
        for iCustomer2 in range(1, len(d_solution['truck'][iTruck2]) - 1)\
        ]

    if len(mParametrosInsercion) == 0:
        StopAlgoritmo = -1
    else:

        mParametrosInsercion = pd.DataFrame(mParametrosInsercion, 
        columns = ['iTruck1', 'customer1', 'iTruck2', 'customer2' ,'SC11'])
        
        mParametrosInsercion = mParametrosInsercion.sort_values(by = ['SC11'])
        # mParametrosInsercion = mParametrosInsercion[mParametrosInsercion['SC11'] < mParametrosInsercion.SC11.quantile([0.25]).item()]
        mParametrosInsercion = mParametrosInsercion[mParametrosInsercion['SC11'] < 0]
        
        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

    return {
        'mParametrosInsercion' : mParametrosInsercion,
        'StopAlgoritmo' : StopAlgoritmo
    }

def exchange_routes2(d_instance_data, d_solution, d_config):
    """
        Inserta cliente de una ruta en otro, con el fin de reducir el numero de rutas

        :param Ruta: Ruta a mejorar
        :param file: archivo a resolver

        :param ParametrosCluster: parametros de insercion y probabilistico

        :param orden: criterio para ordenar las rutas en funcion de su numero de clientes
            0 no se ordena
            1 ascendiente
            2 decreciente

        :param Criterio: seleccion candidado por distancia u horario pronto

        :return
        - Ruta
        """

    d_solution_saved = cp.deepcopy(d_solution)

    d_solution_improve = cp.deepcopy(d_solution)
    Mejora = {}
    Mejora[0] = d_solution_saved
    k = 1
    k_iter = 0
    stop_route = 0

    while stop_route == 0:
            
        StopAlgoritmo = 0

        while StopAlgoritmo != -1:

            stop = 1
            matrix = create_insertion_matrix_exchange(d_instance_data, d_solution_improve)
            mParametrosInsercion = matrix['mParametrosInsercion']
            StopAlgoritmo = matrix['StopAlgoritmo']

            while stop != 0 and StopAlgoritmo != -1:

                if len(mParametrosInsercion)>1:
                    iRow = fun.get_random_number(len(mParametrosInsercion['SC11']), d_config['beta'])
                else:
                    iRow = 0

                iTruck1 = int(mParametrosInsercion.iloc[iRow]['iTruck1'])
                iTruck2 = int(mParametrosInsercion.iloc[iRow]['iTruck2'])
                iPosition1 = int(mParametrosInsercion.iloc[iRow]['customer1'])
                iPosition2 = int(mParametrosInsercion.iloc[iRow]['customer2'])

                d_solution_improve_temp = cp.deepcopy(d_solution_improve)
                d_solution_improve_temp['truck'][iTruck2][iPosition2] \
                    = d_solution_improve['truck'][iTruck1][iPosition1] 
                d_solution_improve_temp['truck'][iTruck1][iPosition1] \
                    = d_solution_improve['truck'][iTruck2][iPosition2] 

                d_solution_improve_temp = arrival.arrival_time(d_instance_data, d_solution_improve_temp)
                stop = check.basic_check(d_instance_data, d_solution_improve_temp)

                if stop == 0:
                    d_solution_improve = cp.deepcopy(d_solution_improve_temp)
                    d_solution_improve_temp = arrival.arrival_time(d_instance_data, d_solution_improve_temp)
                    d_solution_improve_temp = arrival.solution_metric(d_instance_data, d_solution_improve_temp)
                    Mejora[k] = d_solution_improve_temp
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

    mMejoras = [
        [iKey, Mejora[iKey]['n_truck'], Mejora[iKey]['dist']]
        for iKey in Mejora.keys()
    ]

    mMejoras = pd.DataFrame(mMejoras)
    mMejoras = mMejoras.sort_values(by=[1,2])

    d_solution_improve = Mejora[mMejoras.index[0]]
    
    d_solution_improve = arrival.remove_empty_routes(d_solution_improve)
    d_solution_improve = arrival.arrival_time(d_instance_data, d_solution_improve)
    d_solution_improve = arrival.solution_metric(d_instance_data, d_solution_improve)
    d_solution_improve['k'] = k
    
    return d_solution_improve

def compute_dist_diference_insertion(d_instance_data, dist, d_solution, iTruck1, iTruck2, iCustomer1, iCustomer2):

    d_solution_temp = cp.deepcopy(d_solution)
    d_solution_temp['truck'][iTruck1].remove(d_solution['truck'][iTruck1][iCustomer1])
    d_solution_temp['truck'][iTruck2].insert(iCustomer2 + 1, d_solution['truck'][iTruck1][iCustomer1])
    dist_iter = arrival.solution_metric(d_instance_data, d_solution_temp)

    dist_df = dist_iter['dist'] - dist['dist']

    return dist_df

def create_insertion_matrix_insert(d_instance_data, d_solution):

    StopAlgoritmo = 0
    dist = arrival.solution_metric(d_instance_data, d_solution)

    mParametrosInsercion = [\
        [iTruck1, iCustomer1, iTruck2, iCustomer2, \
        compute_dist_diference_insertion(d_instance_data, dist, d_solution, iTruck1, iTruck2, iCustomer1, iCustomer2)]\
        for iTruck1 in d_solution['truck'].keys()
        for iCustomer1 in range(1, len(d_solution['truck'][iTruck1]) - 1)\
        for iTruck2 in range(iTruck1 + 1, len(d_solution['truck'].keys()))\
        for iCustomer2 in range(1, len(d_solution['truck'][iTruck2]) - 1)\
        ]

    if len(mParametrosInsercion) == 0:
        StopAlgoritmo = -1
    else:

        mParametrosInsercion = pd.DataFrame(mParametrosInsercion, 
        columns = ['iTruck1', 'customer1', 'iTruck2', 'customer2' ,'SC11'])
        
        mParametrosInsercion = mParametrosInsercion.sort_values(by = ['SC11'])
        filt = mParametrosInsercion[mParametrosInsercion['SC11'] >= 0]

        # mParametrosInsercion = mParametrosInsercion[mParametrosInsercion['SC11'] < filt.SC11.quantile([0.25]).item()]
        # ParametrosInsercion = mParametrosInsercion[mParametrosInsercion['SC11'] < 0]


        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

    return {
        'mParametrosInsercion' : mParametrosInsercion,
        'StopAlgoritmo' : StopAlgoritmo
    }

def insert_routes(d_instance_data, d_solution, d_config, order):
    """
        Inserta cliente de una ruta en otro, con el fin de reducir el numero de rutas

        :param Ruta: Ruta a mejorar
        :param file: archivo a resolver

        :param ParametrosCluster: parametros de insercion y probabilistico

        :param orden: criterio para ordenar las rutas en funcion de su numero de clientes
            0 no se ordena
            1 ascendiente
            2 decreciente

        :param Criterio: seleccion candidado por distancia u horario pronto

        :return
        - Ruta
        """

    d_solution_improve = cp.deepcopy(d_solution)
    d_solution_improve = solution_data.order_solution(d_instance_data, d_solution_improve, order)

    k_iter = 0
    stop_route = 0
    Mejora = {}
    Mejora[0] = d_solution_improve
    k = 1

    while stop_route == 0:
            
        StopAlgoritmo = 0

        while StopAlgoritmo != -1:

            stop = 1
            matrix = create_insertion_matrix_insert(d_instance_data, d_solution_improve)
            mParametrosInsercion = matrix['mParametrosInsercion']
            StopAlgoritmo = matrix['StopAlgoritmo']

            while stop != 0 and StopAlgoritmo != -1:

                if len(mParametrosInsercion)>1:
                    iRow = fun.get_random_number(len(mParametrosInsercion['SC11']), d_config['beta'])
                else:
                    iRow = 0

                iTruck1 = int(mParametrosInsercion.iloc[iRow]['iTruck1'])
                iTruck2 = int(mParametrosInsercion.iloc[iRow]['iTruck2'])

                iPosition1 = int(mParametrosInsercion.iloc[iRow]['customer1'])
                iPosition2 = int(mParametrosInsercion.iloc[iRow]['customer2'])
                iCandidate = d_solution_improve['truck'][iTruck1][iPosition1]

                d_solution_improve_temp = cp.deepcopy(d_solution_improve)
                d_solution_improve_temp['truck'][iTruck1].remove(iCandidate)
                d_solution_improve_temp['truck'][iTruck2].insert(iPosition2 + 1, iCandidate)

                d_solution_improve_temp = arrival.arrival_time(d_instance_data, d_solution_improve_temp)
                stop = check.basic_check(d_instance_data, d_solution_improve_temp)

                if stop == 0:
                    d_solution_improve_temp = arrival.remove_empty_routes(d_solution_improve_temp)
                    d_solution_improve_temp = arrival.arrival_time(d_instance_data, d_solution_improve_temp)
                    d_solution_improve_temp = arrival.solution_metric(d_instance_data, d_solution_improve_temp)
                    Mejora[k] = d_solution_improve_temp
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

    mMejoras = [
        [iKey, Mejora[iKey]['n_truck'], Mejora[iKey]['dist']]
        for iKey in Mejora.keys()
    ]

    mMejoras = pd.DataFrame(mMejoras)
    mMejoras = mMejoras.sort_values(by=[1,2])

    d_solution_improve = Mejora[mMejoras.index[0]]
    
    d_solution_improve = arrival.remove_empty_routes(d_solution_improve)
    d_solution_improve = arrival.arrival_time(d_instance_data, d_solution_improve)
    d_solution_improve = arrival.solution_metric(d_instance_data, d_solution_improve)
    d_solution_improve['k'] = k
    
    return d_solution_improve

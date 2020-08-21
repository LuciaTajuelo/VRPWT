
import copy as cp
import pandas as pd
import numpy as np

import src.solution_data as arrival
import src.unfeasible as check
import src.common_functions as fun

def kerninghan_lin_one_point(d_instance_data, route, d_config):

    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    mov_prov = {}
    for i in route:
        mov_prov[i] = 0

    Mejora = {}
    Mejora[0] = route_saved
    k = 1

    StopAlgoritmo = 0

    while StopAlgoritmo != -1:
        
        stop = 1
        mParametrosInsercion = []

        dist_ini = arrival.route_metric(d_instance_data, route)
        for iCustomer1 in range(1, (len(route)-1)):
            if mov_prov[route[iCustomer1]] == 0:
                for iCustomer2 in range(1, (len(route)-1)):
                    if mov_prov[route[iCustomer2]] == 0:
                        if iCustomer1 != iCustomer2:

                            route_aux = cp.deepcopy(route)
                            route_aux.remove(route[iCustomer1])
                            route_aux.insert(iCustomer2, route[iCustomer1])

                            dist_iter = arrival.route_metric(d_instance_data, route_aux) - dist_ini

                            mParametrosInsercion.append([iCustomer1, iCustomer2, dist_iter])

        nMovimiento = 0
        for iCustomer1 in route:
            if mov_prov[iCustomer1] == 1:
                nMovimiento = nMovimiento + 1
        if len(route) - nMovimiento > 0:
            StopAlgoritmo = 0
        else:
            StopAlgoritmo = -1
        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

        while stop != 0 and StopAlgoritmo != -1 :
            # Se ordenan
            mParametrosInsercion = pd.DataFrame(mParametrosInsercion)
            mParametrosInsercion = mParametrosInsercion.sort_values(by=[2], ascending= True)

            if (len(mParametrosInsercion)>1):
                iRow = fun.get_random_number(len(mParametrosInsercion[0]), d_config['beta'])
            else:
                iRow = 0
            
            iPosicion = int(mParametrosInsercion.iloc[iRow][0])
            iPosicion2 = int(mParametrosInsercion.iloc[iRow][1])

            route_aux = cp.deepcopy(route)
            route_aux.remove(route[iPosicion])
            route_aux.insert(iPosicion2, route[iPosicion])

            d_arrival = arrival.arrival_time_route(d_instance_data, route_aux)
            d_arrival['truck'] = {}
            d_arrival['truck'][0] = route_aux

            stop = check.basic_check(d_instance_data, d_arrival)

            if stop == 0:
                #route = cp.deepcopy(route_aux)
                mov_prov[route[iPosicion]] = 1

                route_aux = arrival.arrival_time(d_instance_data, d_arrival)
                route_aux = arrival.solution_metric(d_instance_data, route_aux)

                route = cp.deepcopy(route_aux['truck'][0])
                Mejora[k] = cp.deepcopy(route_aux)
                k = k + 1

            else:
                mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])

            nMovimiento = 0
            for iCustomer1 in route:
                if mov_prov[iCustomer1] == 1:
                    nMovimiento = nMovimiento + 1
            if len(route) - nMovimiento > 0:
                StopAlgoritmo = 0
            else:
                StopAlgoritmo = -1
            if len(route)<=2:
                StopAlgoritmo = -1
            if len(mParametrosInsercion)==0:
                StopAlgoritmo = -1

    mMejoras = []
    for iKey in Mejora.keys():
        mMejoras.append([iKey, Mejora[iKey]['dist']])

    if len(mMejoras) > 1:
        mMejoras = pd.DataFrame(mMejoras)
        mMejoras = mMejoras.sort_values(by=[1])
        return Mejora[mMejoras.index[0]]
    else:
        return route_saved

def kerninghan_two_point(d_instance_data, route, d_config):

    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    mov_prov = {}
    for i in route:
        mov_prov[i] = 0

    Mejora = {}
    Mejora[0] = route_saved
    k = 1

    StopAlgoritmo = 0

    while StopAlgoritmo != -1:
        
        stop = 1
        mParametrosInsercion = []

        dist_ini = arrival.route_metric(d_instance_data, route)
        for iCustomer1 in range(1, (len(route)-2)):
            if mov_prov[route[iCustomer1]] == 0:
                for iCustomer2 in range(iCustomer1 + 1, len(route) - 1):
                    if mov_prov[route[iCustomer2]] == 0:

                        route_aux = cp.deepcopy(route)
                        route_aux[iCustomer2] = cp.deepcopy(route[iCustomer1])
                        route_aux[iCustomer1] = cp.deepcopy(route[iCustomer2])

                        dist_iter = arrival.route_metric(d_instance_data, route_aux) - dist_ini

                        mParametrosInsercion.append([iCustomer1, iCustomer2, dist_iter])


        nMovimiento = 0
        for iCustomer1 in route:
            if mov_prov[iCustomer1] == 1:
                nMovimiento = nMovimiento + 1
        if len(route) - nMovimiento > 0:
            StopAlgoritmo = 0
        else:
            StopAlgoritmo = -1
        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

        while stop != 0 and StopAlgoritmo != -1 :
            # Se ordenan
            mParametrosInsercion = pd.DataFrame(mParametrosInsercion)
            mParametrosInsercion = mParametrosInsercion.sort_values(by=[2], ascending= True)

            if (len(mParametrosInsercion)>1):
                iRow = fun.get_random_number(len(mParametrosInsercion[0]), d_config['beta'])
            else:
                iRow = 0
            
            iPosicion = int(mParametrosInsercion.iloc[iRow][0])
            iPosicion2 = int(mParametrosInsercion.iloc[iRow][1])

            route_aux = cp.deepcopy(route)
            route_aux[iPosicion2] = cp.deepcopy(route[iPosicion])
            route_aux[iPosicion] = cp.deepcopy(route[iPosicion2])

            d_arrival = arrival.arrival_time_route(d_instance_data, route_aux)
            d_arrival['truck'] = {}
            d_arrival['truck'][0] = route_aux

            stop = check.basic_check(d_instance_data, d_arrival)

            if stop == 0:
                #route = cp.deepcopy(route_aux)
                mov_prov[route_aux[iPosicion]] = 1
                mov_prov[route_aux[iPosicion2]] = 1

                route_aux = arrival.arrival_time(d_instance_data, d_arrival)
                route_aux = arrival.solution_metric(d_instance_data, route_aux)

                route = cp.deepcopy(route_aux['truck'][0])
                Mejora[k] = cp.deepcopy(route_aux)
                k = k + 1

            else:
                mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])

            nMovimiento = 0
            for iCustomer1 in route:
                if mov_prov[iCustomer1] == 1:
                    nMovimiento = nMovimiento + 1
            if len(route) - nMovimiento > 0:
                StopAlgoritmo = 0
            else:
                StopAlgoritmo = -1
            if len(route)<=2:
                StopAlgoritmo = -1
            if len(mParametrosInsercion)==0:
                StopAlgoritmo = -1

    mMejoras = []
    for iKey in Mejora.keys():
        mMejoras.append([iKey, Mejora[iKey]['dist']])

    if len(mMejoras) > 1:
        mMejoras = pd.DataFrame(mMejoras)
        mMejoras = mMejoras.sort_values(by=[1])
        return Mejora[mMejoras.index[0]]
    else:
        return route_saved

def kerninghan_three_point(d_instance_data, route, d_config):

    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    mov_prov = {}
    for i in route:
        mov_prov[i] = 0

    Mejora = {}
    Mejora[0] = route_saved
    k = 1

    StopAlgoritmo = 0

    while StopAlgoritmo != -1:
        
        stop = 1
        mParametrosInsercion = []

        dist_ini = arrival.route_metric(d_instance_data, route)
        for iCustomer1 in range(1, (len(route)-3)):
            if mov_prov[route[iCustomer1]] == 0:
                for iCustomer2 in [iCustomer \
                    for iCustomer in range(iCustomer1 + 1, len(route) - 2)\
                    if mov_prov[route[iCustomer]] == 0]:
                    for iCustomer3 in [iCustomer \
                        for iCustomer in range(iCustomer2 + 1, len(route) - 1)\
                        if mov_prov[route[iCustomer]] == 0]:

                            for i in itertools.permutations([iCustomer1, iCustomer2, iCustomer3], 3):
                                if i != (iCustomer1, iCustomer2, iCustomer3):

                                    route_aux = cp.deepcopy(route)
                                    route_aux[iCustomer1] = cp.deepcopy(route[i[0]])
                                    route_aux[iCustomer2] = cp.deepcopy(route[i[1]])
                                    route_aux[iCustomer3] = cp.deepcopy(route[i[2]])

                                    dist_iter = arrival.route_metric(d_instance_data, route_aux) - dist_ini
                                    mParametrosInsercion.append([i[0], i[1], i[2], dist_iter, iCustomer1, iCustomer2, iCustomer3])

        nMovimiento = 0
        for iCustomer1 in route:
            if mov_prov[iCustomer1] == 1:
                nMovimiento = nMovimiento + 1
        if len(route) - nMovimiento > 0:
            StopAlgoritmo = 0
        else:
            StopAlgoritmo = -1
        if len(mParametrosInsercion) == 0:
            StopAlgoritmo = -1

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

            iPosicion11 = int(mParametrosInsercion.iloc[iRow][4])
            iPosicion22 = int(mParametrosInsercion.iloc[iRow][5])
            iPosicion33 = int(mParametrosInsercion.iloc[iRow][6])

            route_aux = cp.deepcopy(route)
            route_aux[iPosicion11] = cp.deepcopy(route[iPosicion1])
            route_aux[iPosicion22] = cp.deepcopy(route[iPosicion2])
            route_aux[iPosicion33] = cp.deepcopy(route[iPosicion3])

            d_arrival = arrival.arrival_time_route(d_instance_data, route_aux)
            d_arrival['truck'] = {}
            d_arrival['truck'][0] = route_aux

            stop = check.basic_check(d_instance_data, d_arrival)

            if stop == 0:
                #route = cp.deepcopy(route_aux)
                mov_prov[route_aux[iPosicion11]] = 1
                mov_prov[route_aux[iPosicion22]] = 1
                mov_prov[route_aux[iPosicion33]] = 1

                route_aux = arrival.arrival_time(d_instance_data, d_arrival)
                route_aux = arrival.solution_metric(d_instance_data, route_aux)

                route = cp.deepcopy(route_aux['truck'][0])
                Mejora[k] = cp.deepcopy(route_aux)
                k = k + 1

            else:
                mParametrosInsercion = mParametrosInsercion.drop(mParametrosInsercion.index[iRow])

            nMovimiento = 0
            for iCustomer1 in route:
                if mov_prov[iCustomer1] == 1:
                    nMovimiento = nMovimiento + 1
            if len(route) - nMovimiento > 0:
                StopAlgoritmo = 0
            else:
                StopAlgoritmo = -1
            if len(route)<=2:
                StopAlgoritmo = -1
            if len(mParametrosInsercion)==0:
                StopAlgoritmo = -1

    mMejoras = []
    for iKey in Mejora.keys():
        mMejoras.append([iKey, Mejora[iKey]['dist']])

    if len(mMejoras) > 1:
        mMejoras = pd.DataFrame(mMejoras)
        mMejoras = mMejoras.sort_values(by=[1])
        return Mejora[mMejoras.index[0]]
    else:
        return route_saved

def kerninghan_insert(d_instance_data, route, d_config):

    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    StopAlgoritmo = 0
    stop = 1
    mParametrosInsercion = []

    dist_ini = arrival.route_metric(d_instance_data, route)
    for iCustomer1 in range(1, (len(route)-3)):
        for iCustomer2 in range(iCustomer1 + 1, len(route) - 1):
                for iCustomer3 in range(iCustomer2 + 1, len(route) - 1):

                        route_aux = cp.deepcopy(route)
                        route_aux[iCustomer1] = cp.deepcopy(route[iCustomer2])
                        route_aux[iCustomer2] = cp.deepcopy(route[iCustomer3])
                        route_aux[iCustomer3] = cp.deepcopy(route[iCustomer1])

                        dist_iter = arrival.route_metric(d_instance_data, route_aux) - dist_ini
                        mParametrosInsercion.append([iCustomer1, iCustomer2, iCustomer3, dist_iter])

                        route_aux = cp.deepcopy(route)
                        route_aux[iCustomer1] = cp.deepcopy(route[iCustomer2])
                        route_aux[iCustomer2] = cp.deepcopy(route[iCustomer1])
                        route_aux[iCustomer3] = cp.deepcopy(route[iCustomer2])

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
        route_aux[iPosicion1] = cp.deepcopy(route[iPosicion2])
        route_aux[iPosicion2] = cp.deepcopy(route[iPosicion3])
        route_aux[iPosicion3] = cp.deepcopy(route[iPosicion1])

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

def execute_kerninghan_lin(d_instance_data, route, d_config):
   
    d_arrival = arrival.arrival_time_route(d_instance_data, route)
    d_arrival['truck'] = {}
    d_arrival['truck'][0] = cp.deepcopy(route)
    route_saved = arrival.arrival_time(d_instance_data, d_arrival)
    route_saved = arrival.solution_metric(d_instance_data, route_saved)

    dist1 = cp.deepcopy(route_saved['dist'])
    stop = 0
    k = 0
    
    if len(route) > 3:
        while stop == 0: 
            new_route = kerninghan_lin_one_point(d_instance_data, route, d_config)
            dist2 = new_route['dist']
            if dist1 > dist2:
                route = new_route['truck'][0]
                dist1 = dist2
            else:
                stop = 1
            k = k + 1
        
        stop = 0
        k = 0
        while stop == 0: 
            new_route = kerninghan_two_point(d_instance_data, route, d_config)
            dist2 = new_route['dist']
            if dist1 > dist2:
                route = new_route['truck'][0]
                dist1 = dist2
            else:
                stop = 1
            k = k + 1

    elif len(route) > 4:
        while stop == 0: 
            new_route = kerninghan_three_point(d_instance_data, route, d_config)
            dist2 = new_route['dist']
            if dist1 > dist2:
                route = new_route['truck'][0]
                dist1 = dist2
            else:
                stop = 1
            k = k + 1
    
    return route

def main_kerninghan_lin(d_instance_data, d_solution, d_config):

    d_solution_improve = cp.deepcopy(d_solution)

    for iTruck in d_solution_improve['truck'].keys():
        d_solution_improve['truck'][iTruck] = \
            execute_kerninghan_lin(d_instance_data, d_solution_improve['truck'][iTruck], d_config)

    d_solution_improve = arrival.arrival_time(d_instance_data, d_solution_improve)
    d_solution_improve = arrival.solution_metric(d_instance_data, d_solution_improve)
    d_solution_improve['error'] = check.basic_check(d_instance_data, d_solution_improve)
    
    return d_solution_improve
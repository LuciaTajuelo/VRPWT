import os as os
import pandas as pd
import numpy as np
import copy as cp
import time as tm
from itertools import permutations
import math as math

def read_file(file_name):
    """
    Lectura de set de datos

    :param file_name: nombre del archivo

    :return
    -Diccionarios con la informacion necesaria: Demand, horarios, Distance ..
     """

    with open(file_name) as f:
        data = f.readlines()[4:5]

    data = [x.split() for x in data]
    nCamiones = int(data[0][0])
    cMax = int(data[0][1])

    with open(file_name) as f:
        data = f.readlines()[9:]

    data = [x.split() for x in data]
    data = [iRow for iRow in data if len(iRow) > 0]

    nCustomer = len(data)
    InfoCustomer = {}
    CordX = {}
    CordY = {}
    Demand = {}
    EarlyTime = {}
    LateTime = {}
    ServiceTime = {}
    Distance = {}

    for iCustomer in range(0, nCustomer):
        InfoCustomer[int(data[iCustomer][0])] = {
            'demand': int(data[iCustomer][3]),
            'early_time': int(data[iCustomer][4]),
            'late_time': int(data[iCustomer][5]),
            'service_time': int(data[iCustomer][6])}

        Demand[int(data[iCustomer][0])] = int(data[iCustomer][3])
        EarlyTime[int(data[iCustomer][0])] = int(data[iCustomer][4])
        LateTime[int(data[iCustomer][0])] = int(data[iCustomer][5])
        ServiceTime[int(data[iCustomer][0])] = int(data[iCustomer][6])

        CordX[int(data[iCustomer][0])] = int(data[iCustomer][1])
        CordY[int(data[iCustomer][0])] = int(data[iCustomer][2])

    for iCustomer in range(0, nCustomer):
        for iCustomer2 in range(iCustomer, len(data)):
            Distance[iCustomer, iCustomer2] = ( \
                         (CordX[iCustomer] - CordX[iCustomer2]) ** 2 \
                         + \
                         (CordY[iCustomer] - CordY[iCustomer2]) ** 2 \
                        ) ** (1 / 2)
            Distance[iCustomer2, iCustomer] = Distance[iCustomer, iCustomer2]

    nCustomer = len(data) - 1

    return {
        'n_truck' : nCamiones,
        'cap_max': cMax,
        'n_customer': nCustomer,
        'info_customer': InfoCustomer,
        'demand': Demand,
        'early_time': EarlyTime,
        'late_time': LateTime,
        'service_time': ServiceTime,
        'distance': Distance,
        'cord_x': CordX,
        'cord_y': CordY        
    }

def get_files():
    
    file_name =  os.path.join('src', 'data', 'solomon_100', 'Nombres_archivos.txt')

    with open(file_name) as f:
        data = f.readlines()
    
    return [Name.replace('\n', '') for Name in data]


def read_AIRA(file_name):
    """
    Lectura de set de datos

    :param file_name: nombre del archivo

    :return
    -Diccionarios con la informacion necesaria: Demand, horarios, Distance ..
    """

    d_files = {}
    for iFile in ['Accesos', 'Cargas', 'Distancias', 'Solicitudes', 'Solicitudes_v2', 'Tolvas', 'Velocidades']:

        with open(os.path.join(file_name, iFile + '.txt')) as f:
            d_files[iFile] = f.readlines()

    d_truck_name = {}
    d_name_truck = {}    
    # load
    d_truck_load = {}
    for iTruck in range(len(d_files['Cargas'])):
        l_truck = d_files['Cargas'][iTruck].split()
        d_truck_load[iTruck] = l_truck[1]
        d_truck_name[iTruck] = l_truck[0]
        d_name_truck[l_truck[0]] = iTruck

    # Accesos
    d_feasible_truck_customer = {}
    for iTruck in range(len(d_files['Accesos'])):
        l_truck = d_files['Accesos'][iTruck].split()
        for iCustomer in range(len(l_truck)):
            d_feasible_truck_customer[iTruck, iCustomer] = l_truck[iCustomer]

    # tolva
    d_truck_tolva = {}
    iTolva = -1
    prev_truck = d_name_truck[d_files['Tolvas'][iData].split()[0]]
    for iData in range(len(d_files['Tolvas'])):
        l_truck = d_files['Tolvas'][iData].split()
        if prev_truck == d_name_truck[l_truck[0]]:
            iTolva = iTolva + 1
        else:
            prev_truck = d_name_truck[l_truck[0]]
            iTolva = 0
        d_truck_tolva[d_name_truck[l_truck[0]], iTolva] = l_truck[2]

    # Distancias
    d_km = {}
    d_velocity = {}
    Distance = {}
    for iData1 in range(len(d_files['Distancias'])):
        l_dist = d_files['Distancias'][iData1].split()
        l_velocity = d_files['Velocidades'][iData1].split()
        for iData2 in range(iData1, len(d_files['Distancias'])):
            d_km[iData1, iData2] = float(l_dist[iData2])
            d_km[iData2, iData1] = d_km[iData1, iData2]

            d_velocity[iData1, iData2] = float(l_velocity[iData2])
            d_velocity[iData2, iData1] = d_velocity[iData1, iData2]

            if d_velocity[iData1, iData2] != 0 :
                Distance[iData1, iData2] = \
                    60 * math.floor(d_km[iData1, iData2] / d_velocity[iData1, iData2]) \
                    + d_km[iData1, iData2] / d_velocity[iData1, iData2] % 1
            else: 
                Distance[iData1, iData2] = 0
            Distance[iData2, iData1] = Distance[iData1, iData2]

    # demand
    Demand = {}
    for iData in range(len(d_files['Solicitudes_v2'])):
        Demand[d_files['Solicitudes_v2'][iData].split(";")[0]] = \
            d_files['Solicitudes_v2'][iData].split(";")[1][:-1]

    InfoCustomer = {}
    Demand = {}
    EarlyTime = {}
    LateTime = {}
    ServiceTime = {}
    CordX = {}
    CordY = {}

    for iCustomer in Demand.keys():
        InfoCustomer[iCustomer] = {
            'demand': Demand[iCustomer],
            'early_time': 0,
            'late_time': 24*60,
            'service_time': 0}

        Demand[iCustomer] = Demand[iCustomer]
        EarlyTime[iCustomer] = 0
        LateTime[iCustomer] = 24*60
        ServiceTime[iCustomer] = 0

        CordX[int(data[iCustomer][0])] = 0
        CordY[int(data[iCustomer][0])] = 0

    return {
        'n_truck' : len(d_truck_load.keys()),
        'cap_max': d_truck_load,
        'n_customer': len(Demand.keys()),
        'info_customer': InfoCustomer,
        'demand': Demand,
        'early_time': EarlyTime,
        'late_time': LateTime,
        'service_time': ServiceTime,
        'distance': Distance,
        'cord_x': CordX,
        'cord_y': CordY,
        'd_truck_name': d_truck_name,
        'd_name_truck': d_name_truck,
        'd_truck_load': d_truck_load,
        'd_feasible_truck_customer': d_feasible_truck_customer,
        'd_truck_tolva': d_truck_tolva    
    }

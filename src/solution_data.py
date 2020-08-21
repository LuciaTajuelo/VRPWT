
import copy as cp

def solution_metric(d_instance_data, d_solution):

    d_solution['n_truck'] = len(d_solution['truck'].keys())

    l_dist = [ d_instance_data['distance'][\
                d_solution['truck'][iTruck][i],
                d_solution['truck'][iTruck][i + 1]]\
                for iTruck in d_solution['truck'].keys()\
                for i in range(0, len(d_solution['truck'][iTruck])-1)]
                
    d_solution['dist'] = round(sum(l_dist),2)
    
    return d_solution

def route_metric(d_instance_data, route):

    l_dist = [d_instance_data['distance'][\
            route[i],
            route[i + 1]]\
            for i in range(0, len(route)-1) ]

    return sum(l_dist)

def arrival_time(d_instance_data, d_solution):

    d_solution['arrival'] = {}
    d_solution['arrival']['truck'] = {}
    d_solution['arrival']['customer'] = {}

    for iTruck in d_solution['truck'].keys():
        d_solution['arrival']['truck'][iTruck] = [d_instance_data['early_time'][0]]
        for i in range(1, len(d_solution['truck'][iTruck])):
            t_arrival = max(
                d_solution['arrival']['truck'][iTruck][i - 1] \
                + d_instance_data['distance'][d_solution['truck'][iTruck][i-1],\
                    d_solution['truck'][iTruck][i]]\
                + d_instance_data['service_time'][d_solution['truck'][iTruck][i-1]],
                d_instance_data['early_time'][d_solution['truck'][iTruck][i]]
            )
            d_solution['arrival']['truck'][iTruck].append(t_arrival)
            d_solution['arrival']['customer'][d_solution['truck'][iTruck][i]] = t_arrival

    return d_solution

def arrival_time_route(d_instance_data, d_solution):

    d_arrival = {}
    d_arrival['arrival'] = {}
    d_arrival['arrival']['truck'] = {}
    d_arrival['arrival']['customer'] = {}

    iTruck = 0
    d_arrival['arrival']['truck'][iTruck] = [d_instance_data['early_time'][0]]
    for i in range(1, len(d_solution)):
        t_arrival = max(
            d_arrival['arrival']['truck'][iTruck][i - 1] \
            + d_instance_data['distance'][d_solution[i-1],\
                d_solution[i]]\
            + d_instance_data['service_time'][d_solution[i-1]],
            d_instance_data['early_time'][d_solution[i]]
        )
        d_arrival['arrival']['truck'][iTruck].append(t_arrival)
        d_arrival['arrival']['customer'][d_solution[i]] = t_arrival

    return d_arrival

def remove_empty_routes(d_solution):

    d_solution_aux = {}
    d_solution_aux['truck'] = {}
    k = 0
    for i in d_solution['truck'].keys():
        if len(d_solution['truck'][i]) > 2:
            d_solution_aux['truck'][k] = d_solution['truck'][i]
            k = k + 1
    
    return d_solution_aux

def order_solution(d_instance_data, d_solution, order):

    d_solution_output = cp.deepcopy(d_solution)
    d_solution_output['truck'] = {}
    
    if order == 'descending':
        k = 0
        for i in sorted(d_solution['truck'], key=lambda i: len(d_solution['truck'][i]), reverse=True):
            d_solution_output['truck'][k] = d_solution['truck'][i]
            k = k + 1
    elif order == 'ascending':
        k = 0
        for i in sorted(d_solution['truck'], key=lambda i: len(d_solution['truck'][i]), reverse=False):
            d_solution_output['truck'][k] = d_solution['truck'][i]
            k = k + 1
    else:
        d_solution_output['truck'] = d_solution['truck']

    d_solution_output = arrival_time(d_instance_data, d_solution_output)

    return d_solution_output
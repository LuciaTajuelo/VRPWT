
def truck_arrive_on_time(d_instance_data, d_solution):

    l_error = [iCustomer for iCustomer in d_solution['arrival']['customer'].keys() \
        if d_solution['arrival']['customer'][iCustomer] > d_instance_data['late_time'][iCustomer]]
    
    error = 0
    if len(l_error):
        error = 1

    return error 

def get_customer_late(d_instance_data, d_solution):
    
    l_error = [iCustomer for iCustomer in d_solution['arrival']['customer'].keys() \
        if d_solution['arrival']['customer'][iCustomer] > d_instance_data['late_time'][iCustomer]]
    
    return l_error 

def truck_max_cap(d_instance_data, d_solution):

    error = 0
    
    l_error = [iTruck for iTruck in d_solution['truck'].keys() \
        if sum([d_instance_data['demand'][iCustomer] \
            for iCustomer in d_solution['truck'][iTruck]]) > d_instance_data['cap_max']]
    
    error = 0
    if len(l_error):
        error = 1

    return error

def basic_check(d_instance_data, d_solution):

    error = 0 
    error = error + truck_arrive_on_time(d_instance_data, d_solution)
    error = error + truck_max_cap(d_instance_data, d_solution)
    error = error + depot(d_instance_data, d_solution)

    return error

def customer_visited_once(d_instance_data, d_solution):

    d_error = {
        'visited_more_once' : 0,
        'not_visited' : 0
    }

    for iCustomer in range(1, d_instance_data['n_customer'] + 1):
        l_truck = [iTruck for iTruck in d_solution['truck'].keys() \
            if iCustomer in d_solution['truck'][iTruck]]
        if len(l_truck) > 1:    
            d_error['visited_more_once'] = d_error['visited_more_once'] + 1
        elif len(l_truck) == 0:
            d_error['not_visited'] = d_error['not_visited'] + 1
        else:
            n_visited = d_solution['truck'][l_truck[0]].count(iCustomer)
            if n_visited > 1:
                d_error['visited_more_once'] = d_error['visited_more_once'] + 1

    d_error['error'] = d_error['visited_more_once'] + d_error['not_visited']
    
    return d_error

def depot(d_instance_data, d_solution):

    error = 0

    for iTruck in d_solution['truck'].keys():
        if d_solution['truck'][iTruck].count(0) != 2:
            error = error + 1
        if d_solution['truck'][iTruck][0] != 0:
            error = error + 1
        if d_solution['truck'][iTruck][-1] != 0:
            error = error + 1
    
    if error != 0:
        print('depot error')
        
    return error


def complete_check(d_instance_data, d_solution):

    error = 0 
    error = basic_check(d_instance_data, d_solution)
    customer_error = customer_visited_once(d_instance_data, d_solution)
    error = error + customer_error['error']
    if depot(d_instance_data, d_solution) != 0:
        print('error')
    
    return error




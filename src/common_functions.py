
import numpy as np

def get_random_number(n, beta):
    if  beta < 1:
        nAleatorio = n
        u = np.random.uniform(1, (nAleatorio + 1)) / (nAleatorio + 1)
        iRow = round(np.log(u) / np.log(1 - beta)) % nAleatorio
    else:
        iRow = 0

    return int(iRow)

def get_index(df, column_name, b_reverse):
    
    l_unique_values = list(df[column_name].unique())
    l_unique_values.sort(reverse = b_reverse)
    d_index = {iValue: l_unique_values.index(iValue) for iValue in l_unique_values}
    df[column_name] = [d_index[iKey] for iKey in df[column_name]]

    return df
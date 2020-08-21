
import pandas as pd
import copy as cp
import pickle as pickle
import xlrd as xlrd
import src.read as read
import src.initial_solution as initial_solution
import src.improve_solution as join
import src.Kernighan_Lin as LK
import os as os
import csv
import src.solution_data as arrival
import src.unfeasible as check
import time as time

import plotly.express as px
import plotly.graph_objects as go

import src.join_routes as new_approach
import os as os


def summary(size, folder):

    instance = read.get_files()

    l_df = []
    for iFile in instance:
        print(iFile)
        file_name = iFile.replace("txt", "pickle")
        if os.path.isfile(folder + "\\solomon_" + str(size) + "\\" + file_name):
            with open( folder + "\\solomon_" + str(size) + "\\" + file_name, "rb") as f:
                player = pickle.load(f)
                l_df.append([
                    file_name.replace(".pickle", ""),
                    player['n_truck'],
                    player['dist'],
                    player['time'],
                    player['l_beta'],
                ])
        
        else:
            l_df.append([
            file_name.replace(".pickle", ""),
            '-',
            '-',
            '-',
            '-',
            ])

    l_df = pd.DataFrame(l_df, columns = ['file', 'n_routes', 'distance', 'time','beta'])
    l_df['type'] = folder
    l_df['file'] = [iFile.lower() for iFile in l_df['file']]

    return l_df

def sumary_latex(size, folder):

    df = summary(size, folder)

    file_name = "C:\\Users\\lucia\\Downloads\\BKS.xlsx"
    wb = xlrd.open_workbook(file_name)
    l_tables = wb.sheet_names()

    # To read as dataframe
    df = pd.read_excel(file_name, sheet_name = 'BKS.xlsx')
    df = df[[ 'Instance',  'Vehicles',  'Distance', 'Reference' ]]

    df = df.merge(summary(100, folder), left_on='Instance', right_on='file')

    df['Distance'] = round(df['Distance'],2)
    df['distance'] = round(df['distance'],2)
    df['time'] = round(df['time'],0)

    df['dif_truck'] = df['n_routes'] - df['Vehicles']
    df['dif_dist'] = df['distance'] - df['Distance']
    df['GAP'] = round(((df['distance'] - df['Distance'])/df['Distance'])*100,2)

    df = df.sort_values(by = ['dif_truck', 'dif_dist'])
    df = df.sort_values(by = ['Instance'])

    df = df[['Instance', 'Vehicles','Distance','Reference','n_routes','distance','GAP','time', 'beta']]
    df.columns = ['Instance', 'Vehicles','Distance','Reference','n_routes','distance','GAP','time', 'beta']
    cols = ['Instance', 'Vehicles','Distance','Reference','n_routes','distance','GAP','time', 'beta']
    
    for iCol in cols:
        df.loc[df['Vehicles'] == df['n_routes'],iCol] = \
            '\\textbf{ ' + df.loc[df['Vehicles'] == df['n_routes'],iCol].apply(lambda row:str(row)) + '}'

    df['combined'] = df[cols].apply(lambda row: ' & '.join(row.values.astype(str)), axis=1)
    
    df['combined'] = df['combined'] + "\\\\" 
    df_write = df['combined']
    
    header = pd.DataFrame(data = [
        '\\begin{table}[H]',
        '\\begin{tabular}{c c c c | c c c c}',
        '\\specialrule{.2em}{.2em}{.2em}',
        '\\hline',
        '\\multicolumn{4}{c|}{BKS} & 	\multicolumn{4}{c}{Obtained solution} \\\\',
        '\\hline',
        'Data set  &  N \\textordmasculine routes & Distance & Author &  N \\textordmasculine routes & Distance & GAP by distance (\%) & time (s)\\\\'
    ])
    
    end1 = pd.DataFrame(data = [
        '\\hline',
        '\\specialrule{.2em}{.2em}{.2em}',
        '\\end{tabular} \\',
        '\\caption{BKS compared to obtained solution to data set C1 and C2.}',
        '\\label{TABLE-BKS}',
        '\\end{table}\\'
    ])
    end2 = pd.DataFrame(data = [
        '\\hline',
        '\\specialrule{.2em}{.2em}{.2em}',
        '\\end{tabular} \\',
        '\\caption{BKS compared to obtained solution to data set R1 and R2.}',
        '\\label{TABLE-BKS}',
        '\\end{table}\\'
    ])
    end3 = pd.DataFrame(data = [
        '\\hline',
        '\\specialrule{.2em}{.2em}{.2em}',
        '\\end{tabular} \\',
        '\\caption{BKS compared to obtained solution to data set RC1 and RC2.}',
        '\\label{TABLE-BKS}',
        '\\end{table}\\'
    ])

    df_output = pd.concat([header, df_write.iloc[0:16]])
    df_output = pd.concat([df_output, end1])
    df_output = pd.concat([df_output, header, df_write.iloc[17:38], end2])
    df_output = pd.concat([df_output, header, df_write.iloc[39:], end3])

    df_output.to_csv('pandas.tex', header=False, index=None, sep=' ', mode='w')

def main(size, l_beta):

    instance = read.get_files()
    df_new_sol = []

    folder = 'solomon_solution' + '_'.join([str(i) for i in l_beta])
    try:
        os.mkdir(folder)
    except:
        print('')
    file_name_output = os.path.join(folder, 'solomon_'+ str(size))  

    for iFile in instance:
        file_name = iFile.replace('txt', 'pickle')
        
        file_name =  os.path.join(folder, file_name)
        if not os.path.isfile(file_name.replace(".xlsx", ".pickle")):
            print(iFile)
            print(file_name.replace(".txt", ".pickle") + ".pickle")
            if not os.path.isfile(file_name.replace(".txt", ".pickle") + ".pickle"):
                print(file_name.replace(".txt", ".pickle") + ".pickle")

                df_new_sol = new_approach.create_solution_new(iFile, df_new_sol, size, folder, l_beta)
                df_new_sol
                print('------------------------------------------')

    df_new_sol = pd.DataFrame(df_new_sol, columns = ['file', 'n_routes', 'distance', 'time', 'beta'])
    df_new_sol.to_csv('summary_' + folder + str(size) + '.csv')

def plot_solution(d_instance_data, d_solution):

    df1 = pd.DataFrame.from_dict(d_instance_data['cord_x'], orient='index',columns = ['x'])
    df2 = pd.DataFrame.from_dict(d_instance_data['cord_y'], orient='index',columns = ['y'])

    df1['customer'] = range(0,101)
    df2['customer'] = range(0,101)
    result = pd.merge(df1, df2, on = ['customer'])
    
    result['color'] = 'customer'
    result['color'].iloc[0]= 'depot'
    result['coordinate x']= result['x']
    result['coordinate y']= result['y']

    fig = px.scatter(result, x="coordinate x", y="coordinate y", hover_data=["customer"], text="customer" ,color='color')
    fig.update_traces(textfont_size=15)

    fig = go.Figure()
    for i in d_solution['truck'].keys():
        fig.add_trace(go.Scatter(x=result[result['customer'].isin(d_solution['truck'][i])]['x'], \
            y=result[result['customer'].isin(d_solution['truck'][i])]['y'],
            mode='lines+markers',
            name=i))
    fig.show()
    fig.write_html("file.html")

def print_cluster(cluster):

    hola = list(cluster)
    hola.insert(0,0)


    df1 = pd.DataFrame.from_dict(d_instance_data['cord_x'], orient='index',columns = ['x'])
    df2 = pd.DataFrame.from_dict(d_instance_data['cord_y'], orient='index',columns = ['y'])

    df1['customer'] = range(0,101)
    df2['customer'] = range(0,101)
    result = pd.merge(df1, df2, on = ['customer'])
    result['cluster'] = hola

    fig = go.Figure()
    for iCluster in list(set(cluster)):
        fig.add_trace(go.Scatter(x=result[result['cluster'] == iCluster]['x'], \
            y=result[result['cluster'] == iCluster]['y'],
            mode='lines+markers',
            name='iCluster'))

    fig.show()


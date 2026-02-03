#%%
#Download Hidroweb v1.0
#Autor: Carlos Eduardo Sousa Lima, M. Sc.
#e-mail: carlosesl07@gmail.com

import requests
import xml.etree.ElementTree as ET
import datetime
import calendar
import pandas as pd
import os


cols_pluv = pd.read_csv("cols_pluv.csv")
list_stations = pd.read_excel("list_stations.xlsx", sheet_name = "estacoes")

#%%
for i, j in zip(list_stations["station"], list_stations["type"]):

    params = {'codEstacao':i, 'dataInicio':"", 'dataFim':"",
              'tipoDados':j, 'nivelConsistencia':""}
    server = 'http://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroSerieHistorica'
    response = requests.get(server, params)
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()
    list_content = []

    for content in root.iter("SerieHistorica"):
        row_list = []
        for col in cols_pluv.iloc[:,0]:
            row_data = [content.find(col).text if content.find(col) is not None else '']
            row_list.append(row_data[0])
        list_content.append(row_list)

    df_content = pd.DataFrame(list_content, columns = cols_pluv.iloc[:,0])
    df_content["DataHora"] = pd.to_datetime(df_content["DataHora"])

    df_content.to_csv("Chuvas_C_{}.csv".format(i), index = False, header = True)
#%%
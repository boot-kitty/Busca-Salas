# Imports propios (test)
import test_variables as tv

# Imports externos
import pandas as pd
import requests
import sys
import os
from bs4 import BeautifulSoup

# Imports propios (source)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'source')))

import web_scrapper as ws
import lector_de_archivos as la

# -------------------------------------------------------------------------------------------------

# Url building
empiric_url = 'https://buscacursos.uc.cl/?cxml_semestre=2024-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=PR&cxml_profesor=&cxml_campus=San+Joaqu%C3%ADn&cxml_unidad_academica=4&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS&cxml_modulo_J2=J2&cxml_periodo=TODOS&cxml_escuela=TODOS&cxml_nivel=TODOS#resultados'
url_data = tv.url_data
url = ws.assemble_url(url_data, 'San+Joaqu%C3%ADn', 4, 'J2=J2')
# -------------------------------------------------------------------------------------------------

# Webscrapping test 
df = pd.DataFrame({'Horario': [], 'Sala': []})
response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
df = pd.concat([df, ws.scrape_data(soup)], ignore_index = True)

print("Limpiando DataFrame")
df_limpio = df.dropna()
df_salas_unicas = df_limpio['Sala'].drop_duplicates()

print("Generando objetos 'Sala'")
dict_salas = la.generar_salas(df_salas_unicas)

print("Actualizando horarios de Salas")
la.actualizar_horarios_diccionario_salas(df_limpio, dict_salas)



with pd.option_context(
    'display.max_rows', None,
    'display.max_columns', None,
    'display.precision', 3,
):
    #print(df_limpio)
    pass


A7 = dict_salas["A7"]

print(A7.nombre)
print(A7.horarios)
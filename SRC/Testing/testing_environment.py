# Imports propios
import test_variables as tv
import web_scrapper as ws

# Imports externos
import pandas as pd
import requests
from bs4 import BeautifulSoup
# -------------------------------------------------------------------------------------------------

# Url building
empiric_url = 'https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=San+Joaqu%C3%ADn&cxml_unidad_academica=4&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS&cxml_modulo_M3=M3#resultados'
url_data = tv.url_data
url = ws.assemble_url(url_data, 'San+Joaqu%C3%ADn', 4, 'M3=M3')
# -------------------------------------------------------------------------------------------------

# Webscrapping test 
data_buscacursos = pd.DataFrame({'Horario': [], 'Sala': []})
response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
data_buscacursos = pd.concat([data_buscacursos, ws.scrape_data(soup)], ignore_index = True)

print(data_buscacursos)
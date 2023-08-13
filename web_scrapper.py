# Imports Externos:
import requests
import pandas as pd
from bs4 import BeautifulSoup
# -------------------------------------------------------------------------------------------------

# Funciones:
def extract_row_data(row):
    """
    This function splits the 'Horario' table for each class and returns 
    a list containing both the assigned classroom and the time block 
    """
    columns = row.find_all('td')
    schedule_table = columns[16].find('table')
    course_activities = schedule_table.find_all('tr')

    for activity in course_activities:
        components = activity.find_all('td')
        Horario = components[0].text.strip()
        Sala = components[2].text.strip()

    return [Horario, Sala]


def scrape_course_data(url: str) -> pd.DataFrame:
    """
    This function recives a web url for the page 'https://buscacursos.uc.cl/' in the form of a string 
    and returns a DataFrame with all the 'Horarios' and 'Salas' listed
    """
    data = []
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    page_frame = soup.find('table')
    even_rows = page_frame.find_all('tr', class_ = 'resultadosRowPar')
    uneven_rows = page_frame.find_all('tr', class_ = 'resultadosRowImpar')

    for row in even_rows:
        row_data = extract_row_data(row)
        if (row_data[1] != 'SIN SALA'):
            data.append(row_data)

    for row in uneven_rows:
        row_data = extract_row_data(row)
        if (row_data[1] != 'SIN SALA'):
            data.append(row_data)

    return pd.DataFrame(data, columns = ['Horario', 'Sala'])


def scrape_buscacursos(urls_list):
    data_buscacursos = pd.DataFrame({'Horario': [], 'Salas': []})
    for url in urls_list:
        data_buscacursos.append(scrape_course_data(url))

    
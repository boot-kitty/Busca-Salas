# Imports Externos:
import requests
import pandas as pd
from bs4 import BeautifulSoup
# -------------------------------------------------------------------------------------------------

# Funciones:
def generate_url_list(unidades_academicas:dict, unidades_academicas_extensas:list, url_data):
    pass

def assemble_url(url_data: dict, campus:str, unidad_academica: int, *modulo) -> str:
    """
    This function returns a string, representing a url for a search query that can be used by 'scrape_courses_data'
    """
    url = (url_data['url_components']['domain_request']
            + url_data['url_components']['semester'] + url_data['semestre_actual']
            + url_data['url_components']['constant_data-1']
            + url_data['url_components']['campus'] + campus
            + url_data['url_components']['acamedic_unit'] + str(unidad_academica)
            + url_data['url_components']['constant_data-2']
            )

    if modulo != ():
        url += (url_data['url_components']['module'] + modulo[0])

    url += url_data['url_components']['tail']
    return url


def extract_row_data(row) -> list:
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


def scrape_courses_data(url: str) -> pd.DataFrame:
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
        data_buscacursos.append(scrape_courses_data(url))


# -------------------------------------------------------------------------------------------------

# Código:
if __name__ == "__main__":

    aaaa = {
            "semestre_actual": "2023-2",
            "url_components": {
                                "domain_request":"https://buscacursos.uc.cl/?",
                                "semester": "cxml_semestre=",
                                "constant_data-1": "&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=", 
                                "campus": "&cxml_campus=",
                                "acamedic_unit": "&cxml_unidad_academica=",
                                "constant_data-2": "&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS",
                                "module": "&cxml_modulo_",
                                "tail": "#resultados"
                                }
        }

    test_url = assemble_url(aaaa, 'San+Joaquín', 0, "W5=W5")
    print(test_url)
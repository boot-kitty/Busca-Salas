# Imports Externos:
import requests
import pandas as pd
from bs4 import BeautifulSoup
# -------------------------------------------------------------------------------------------------

# Funciones:
def check_site_warnings(soup:BeautifulSoup, site_warnings):
    try:
        warning_msg = soup.find('div', class_='bordeBonito').text.strip()

        if warning_msg == site_warnings[0]:
            return 0
        
        elif warning_msg == site_warnings[1]:
            return 1
        
        # In case an undefined error pops up
        else:
            print(warning_msg)

    except:
        return None


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


def build_urls_list(unidades_academicas:list, unidades_academicas_extensas:list, unidades_sin_datos:list, 
                    url_data:dict, modulos:list, campus="San+Joaqu%C3%ADn") -> list:
    """
    This function creates a list holding all the urls for search queries that can be used by 'scrape_courses_data', 
    those representing an 'unidad academica' part of 'unidades_academicas_extensas' are split into multiple queries by their 'modulo'
    """
    urls_list = []

    for unidad_academica in unidades_academicas:

        if unidad_academica in unidades_sin_datos:
            continue
        
        elif unidad_academica not in unidades_academicas_extensas:
            urls_list.append(assemble_url(url_data, campus, unidad_academica))

        else:
            for modulo in modulos:
                pass

    return urls_list


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
    i = 0
    data_buscacursos = pd.DataFrame({'Horario': [], 'Salas': []})
    for url in urls_list:
        data_buscacursos.append(scrape_courses_data(url))
        print(f"Dataframe shape: {data_buscacursos.shape[0]}, Iteration: {i}")
        i+=1


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
    
    unidades_academicas_extensas = [
        "agronomia",
        "antropologia",
        "ciencia_politica",
        "astrofisica",
        "ciencias_de_la_salud",
        "construccion_civil",
        "economia",
        "educacion",
        "enfermeria",
        "filosofia",
        "fisica",
        "geografia",
        "historia",
        "ingenieria",
        "letras",
        "matematicas",
        "odontologia",
        "psicologia",
        "quimica",
        "requisito_idioma",
        "sociologia",
        "teologia",
        "trabajo_social"
        ]

    unidades_academicas = {
        "actividades_filosofia": 68,
        "actividades_universitarias": 0,
        "actuacion": 34,
        "agronomia": 11,
        "antropologia": 92,
        "arquitectura": 94,
        "arte": 33,
        "astrofisica": 2,
        "bachillerato": 7,
        "CARA": 52,
        "ciencia_politica": 45,
        "ciencias_biologicas": 12,
        "ciencias_de_la_salud": 16,
        "college": 9,
        "comunicaciones": 28,
        "construccion_civil": 1,
        "deportes": 53,
        "derecho": 17,
        "desarrollo_sustentable": 25,
        "diseno": 59,
        "economia": 5,
        "educacion": 20,
        "enfermeria": 13,
        "escuela_de_gobierno": 19,
        "escuela_de_graduadoos": 40,
        "estudios_urbanos": 95,
        "estetica": 51,
        "filosofia": 67,
        "fisica": 3,
        "geografia": 57,
        "historia": 56,
        "ing_mat": 23,
        "ingenieria": 4,
        "ing_bio_med": 18,
        "eticas_aplicadas": 26,
        "letras": 64,
        "matematicas": 6,
        "medicina": 14,
        "veterniaria": 24,
        "musica": 70,
        "odontologia": 15,
        "psicologia": 29,
        "quimica": 10,
        "farmacia": 8,
        "requisito_idioma": 54,
        "sociologia": 91,
        "teologia": 38,
        "trabajo_social": 30,
        "villarica": 21
        }

    unidades_sin_datos = ["actividades_filosofia", "arquitectura", "bachillerato", "college", "deportes", "farmacia", "villarica"]

    site_warnings = [
        "La búsqueda no produjo resultados.",
        "La búsqueda produjo demasiados resultados. Sólo se muestran los primeros 50 resultados.Por favor introduce más detalles en tus parámetros de búsqueda para ver más resultados."
        ]

    #scrape_courses_data()



"""
test_url = "https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=San+Joaqu%C3%ADn&cxml_unidad_academica=11&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
  
print(check_site_warnings(test_url, site_warnings))
    #test_url_data_indexation(unidades_academicas, unidades_academicas_extensas, unidades_sin_datos, aaaa)

def test_url_data_indexation(unidades_academicas:dict, unidades_academicas_extensas:list, unidades_academicas_sin_datos: list, url_data: dict):

    #This function checks that all extensive and non-extensive academic units are indexed correctly

    todo_correcto = True
    for ua in unidades_academicas:

        if ua not in unidades_academicas_sin_datos:

            if (ua not in unidades_academicas_extensas) == check_site_warnings(assemble_url( url_data, 'San+Joaquín', unidades_academicas[ua])):
                pass
                print(f'{ua} correctamente indexado')

            else:
                todo_correcto = False
                print(f'ERROR en {ua}')

    if todo_correcto:
        print('Dataset Correcto')

    test_url_data_indexation(unidades_academicas, unidades_academicas_extensas, unidades_sin_datos, aaaa)
"""
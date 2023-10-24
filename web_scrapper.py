# Imports Propios:
import errores_y_excepciones as e

# Imports Externos:
import requests
import pandas as pd
from bs4 import BeautifulSoup
# -------------------------------------------------------------------------------------------------

# Funciones:
def find_academic_unit_code(url:str) -> str:
    position_in_url = url.find('unidad_academica=') + 17
    academic_unit_code_string = url[position_in_url: position_in_url+2]

    try:
        academic_unit_code = int(academic_unit_code_string)

    except ValueError:
        academic_unit_code = int(academic_unit_code_string[0])

    return str(academic_unit_code)


def check_site_warnings(soup:BeautifulSoup, site_warnings):
    try:
        warning_msg = soup.find('div', class_='bordeBonito').text.strip()

        if warning_msg == site_warnings[0]:
            return e.ErrorBusquedaVacia
        
        elif warning_msg == site_warnings[1]:
            return e.ErrorBusquedaMuyAmplia
        
        elif warning_msg == site_warnings[2]:
            return e.ErrorBusquedaMuyAmplia
        
        # In case an undefined error pops up
        else:
            print("WARNING INESPERADO!")
            print(warning_msg)

    except:
        return None


def assemble_url(url_data: dict, campus:str, unidad_academica: int, *modulo) -> str:
    """
    This function returns a string, representing a url for a search query that can be used by 'scrape_buscacursos'
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


def build_urls_list(unidades_academicas:list, url_data:dict, campus="San+Joaqu%C3%ADn", restrictions={}) -> list:
    """
    This function creates a list holding all the urls for search queries that can be used by 'scrape_buscacursos'
    """
    urls_list = []

    if restrictions == {}:

        for unidad_academica in unidades_academicas:
            urls_list.append(assemble_url(url_data, campus, unidades_academicas[unidad_academica]))

        return urls_list
    
    try:
        unidades_academicas_extensas = restrictions['unidades_academicas_extensas']
        unidades_academicas_sin_datos = restrictions['unidades_academicas_sin_datos']
        modulos = restrictions['modulos']

        for unidad_academica in unidades_academicas:

            if unidad_academica in unidades_academicas_sin_datos:
                continue

            elif unidad_academica not in unidades_academicas_extensas:
                urls_list.append(assemble_url(url_data, campus, unidad_academica))

            else:
                for modulo in modulos:
                    urls_list.append(assemble_url(url_data, campus, unidad_academica, modulo))

    except KeyError:
        print("ERROR, restricciones incompletas")


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


def scrape_courses_data(soup: BeautifulSoup) -> pd.DataFrame:
    """
    This function recives a BeautifulSoup object with the contents of a query for the page 'https://buscacursos.uc.cl/',
    and returns a DataFrame with all the 'Horarios' and 'Salas' listed
    """
    data = []

    page_frame = soup.find('table')
    even_rows = page_frame.find_all('tr', class_ = 'resultadosRowPar')
    uneven_rows = page_frame.find_all('tr', class_ = 'resultadosRowImpar')

    for row in even_rows:
        try:
            row_data = extract_row_data(row)
            if (row_data[1] != 'SIN SALA'):
                data.append(row_data)

        except UnboundLocalError:
            print('>> Actividad inválida, saltando fila')

    for row in uneven_rows:
        try:
            row_data = extract_row_data(row)
            if (row_data[1] != 'SIN SALA'):
                data.append(row_data)
                
        except UnboundLocalError:
            print('Actividad inválida, saltando fila')

    return pd.DataFrame(data, columns = ['Horario', 'Sala'])


def scrape_buscacursos(urls_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos, recursive=False) -> pd.DataFrame:
    i = 0
    data_buscacursos = pd.DataFrame({'Horario': [], 'Sala': []})

    for url in urls_list:

        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        try:
            query_error = check_site_warnings(soup, site_warnings)
            if query_error != None:
                raise query_error
            
            old_length = data_buscacursos.shape[0]
            data_buscacursos = pd.concat([data_buscacursos, scrape_courses_data(soup)], ignore_index = True)
            outcome = f'added {data_buscacursos.shape[0] - old_length} data entries'

        except e.ErrorBusquedaVacia:
            if not recursive:
                print(f'> Empty response, query ignored | UA: {unidades_academicas_por_codigo[find_academic_unit_code(url)]}')
                continue
            else:
                outcome = 'Empty response,  query ignored'


        except e.ErrorBusquedaMuyAmplia:
            if recursive:
                print(f'>> ERROR, recursive search limit exceeded for {url}')
                raise RecursionError
            
            else:
                print(f'> Too many results | Query modified | UA: {unidades_academicas_por_codigo[find_academic_unit_code(url)]}')

                new_url_list = []
                url_components = url_data['url_components']

                for modulo in modulos:
                    new_url = url[:len(url)-len(url_components['tail'])]
                    new_url += url_components['module'] + modulo + url_components['tail']
                    new_url_list.append(new_url)

                #print(new_url_list)
                result = scrape_buscacursos(new_url_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos, recursive=True)
                data_buscacursos = pd.concat([data_buscacursos, result], ignore_index = True)

        finally:
            if not recursive:
                print(f"Dataframe shape: {data_buscacursos.shape[0]} | Iteration: {i} | UA: {unidades_academicas_por_codigo[find_academic_unit_code(url)]}")

            else:
                print(f">> Recursive search | Iteration: {i+1}/45 | Outcome: {outcome}")

            i += 1

    return data_buscacursos



# -------------------------------------------------------------------------------------------------

# Código:
if __name__ == "__main__":

    url_data = {
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
    
    unidades_academicas_por_codigo = {
        "68": "actividades_filosofia",
        "0": "actividades_universitarias",
        "34": "actuacion",
        "11": "agronomia",
        "92": "antropologia",
        "94": "arquitectura",
        "33": "arte",
        "2": "astrofisica",
        "7": "bachillerato",
        "52": "CARA",
        "45": "ciencia_politica",
        "12": "ciencias_biologicas",
        "16": "ciencias_de_la_salud",
        "9": "college",
        "28": "comunicaciones",
        "1": "construccion_civil",
        "53": "deportes",
        "17": "derecho",
        "25": "desarrollo_sustentable",
        "59": "diseno",
        "5": "economia",
        "20": "educacion",
        "13": "enfermeria",
        "19": "escuela_de_gobierno",
        "40": "escuela_de_graduadoos",
        "95": "estudios_urbanos",
        "51": "estetica",
        "67": "filosofia",
        "3": "fisica",
        "57": "geografia",
        "56": "historia",
        "23": "ing_mat",
        "4": "ingenieria",
        "18": "ing_bio_med",
        "26": "eticas_aplicadas",
        "64": "letras",
        "6": "matematicas",
        "14": "medicina",
        "24": "veterniaria",
        "70": "musica",
        "15": "odontologia",
        "29": "psicologia",
        "10": "quimica",
        "8": "farmacia",
        "54": "requisito_idioma",
        "91": "sociologia",
        "38": "teologia",
        "30": "trabajo_social",
        "21": "villarica"
    }

    unidades_sin_datos = ["actividades_filosofia", "arquitectura", "bachillerato", "college", "deportes", "farmacia", "villarica"]

    site_warnings = [
        "La búsqueda no produjo resultados.",
        "La búsqueda produjo demasiados resultados. Sólo se muestran los primeros 50 resultados.Por favor introduce más detalles en tus parámetros de búsqueda para ver más resultados.",
        "La búsqueda produjo demasiados resultados. Sólo se muestran los primeros 500 resultados.Por favor introduce más detalles en tus parámetros de búsqueda para ver más resultados."
        ]
    
    modulos = [
        'L1=L1', 'L2=L2', 'L3=L3', 'L4=L4', 'L5=L5', 'L6=L6', 'L7=L7', 'L8=L8', 'L9=L9', 
        'M1=M1', 'M2=M2', 'M3=M3', 'M4=M4', 'M5=M5', 'M6=M6', 'M7=M7', 'M8=M8', 'M9=M9', 
        'W1=W1', 'W2=W2', 'W3=W3', 'W4=W4', 'W5=W5', 'W6=W6', 'W7=W7', 'W8=W8', 'W9=W9', 
        'J1=J1', 'J2=J2', 'J3=J3', 'J4=J4', 'J5=J5', 'J6=J6', 'J7=J7', 'J8=J8', 'J9=J9', 
        'V1=V1', 'V2=V2', 'V3=V3', 'V4=V4', 'V5=V5', 'V6=V6', 'V7=V7', 'V8=V8', 'V9=V9'
        ]

    """
    urls_list = build_urls_list(unidades_academicas, url_data)
    scraped_data = scrape_buscacursos(urls_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos)
    print(scraped_data)
    """
    """
    test_url = "https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=San+Joaqu%C3%ADn&cxml_unidad_academica=11&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
  
    print(check_site_warnings(test_url, site_warnings))
    """


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
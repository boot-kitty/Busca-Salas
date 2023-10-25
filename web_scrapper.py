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


def assemble_url(url_data: dict, campus:str, unidad_academica: int, modulo='') -> str:
    """
    This function returns a string, representing a url for a search query that can be used by 'run_webscrapper'
    """
    url = (url_data['url_components']['domain_request']
            + url_data['url_components']['semester'] + url_data['semestre_actual']
            + url_data['url_components']['constant_data-1']
            + url_data['url_components']['campus'] + campus
            + url_data['url_components']['acamedic_unit'] + str(unidad_academica)
            + url_data['url_components']['constant_data-2']
            )

    if modulo != '':
        print('llamando a módulo:', modulo)
        url += (url_data['url_components']['module'] + modulo)

    url += url_data['url_components']['tail']
    return url


def build_urls_list(unidades_academicas:list, url_data:dict, campus="San+Joaqu%C3%ADn", restrictions={}) -> list:
    """
    This function creates a list holding all the urls for search queries that can be used by 'run_webscrapper'
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


def scrape_data(soup: BeautifulSoup) -> pd.DataFrame:
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


def run_webscrapper(urls_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos, recursive=False) -> pd.DataFrame:
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
            data_buscacursos = pd.concat([data_buscacursos, scrape_data(soup)], ignore_index = True)
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
                result = run_webscrapper(new_url_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos, recursive=True)
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

    """
    urls_list = build_urls_list(unidades_academicas, url_data)
    scraped_data = run_webscrapper(urls_list, url_data, unidades_academicas_por_codigo, site_warnings, modulos)
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
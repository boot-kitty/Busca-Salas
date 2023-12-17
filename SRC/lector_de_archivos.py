# Imports Externos:
import pandas as pd
import os
import pickle
import json
import time as t
# Nota: para correr el programa también debe instalarse openpyxl

# Imports Propios:
import salas as s
import web_scrapper as ws
# -------------------------------------------------------------------------------------------------

# Funciones:


def obtener_parametro(key_del_diccionario, *args):
    """
    Esta función se encarga de leer el archivo parametros.json y retornar el valor de uno de los
    diccionarios contenidos en este archivo. 
    
    Por ejemplo si queremos obtener el path del logo de 
    DCCasillas, llamamos a la función: obtener_parametro('paths', 'logo').
    
    De la misma forma, se puede obtener un diccionario completo. 
    Por ejemplo el diccionario con los paths de los archivos de datos:
    llamamos a la función: obtener_parametro('paths', None).
    """

    path = os.path.join("", "parametros.json")
    
    with open(path, "r", encoding = "utf-8") as archivo:
        diccionario_parametros = json.load(archivo)
        diccionario_selecionado = diccionario_parametros[key_del_diccionario]

    try:
        key_del_parametro = args[0]
        return diccionario_selecionado[key_del_parametro]

    # En el caso de que no se haya entregado una llave de parámetro válida, se retorna el
    # diccionario completo
    except IndexError:
        return diccionario_selecionado


def generar_dataframe():
    """
    Esta función se encarga de generar un dataframe de Pandas utilizando el directorio de un 
    archivo .xlsx entregado en parametros.py
    """
    excel_file = os.path.join(*obtener_parametro("paths", "directorio_excel"))
    df = pd.read_excel(excel_file, usecols = ['Horario', 'Sala'])
    return df


def limpiar_dataframe(df: pd.DataFrame):
    """
    Esta función se encarga de eliminar del dataframe las filas sin información y aquellas que contienen sala de tipo 'SIN SALA'
    """
    (_,df_sin_horario_nulo), (_,df_horarios_nulos) = df.groupby(df.Horario.isna())
    df_salas_reales = df_sin_horario_nulo[~df_sin_horario_nulo['Sala'].str.contains("SIN SALA", na=False)]
    return df_salas_reales


def generar_salas(df: pd.DataFrame):
    """
    Esta función se encarga de generar un diccionario cuyas llaves son los nombres de las salas del campus SJ,
    y sus valores corresponden a instancias de la clase Sala
    """
    lista_salas = df.values.tolist()
    diccionario_salas = {}
    for sala in lista_salas:
        diccionario_salas[sala] = s.Sala(sala)
    return diccionario_salas


def separar_datos_horario(datos_horario: list):
    """
    Esta función recibe una lista conteniendo los días y bloques en los que una sala esta resevada, 
    y los transforma en una tupla compatible con el método 'actualizar_horarios' de la clase Sala
    """
    lista_datos_horario = datos_horario.split(':')
    tupla_datos_horario = (lista_datos_horario[0].split("-"), lista_datos_horario[1].split(","))
    return tupla_datos_horario


def actualizar_horarios_diccionario_salas(df: pd.DataFrame, dict_salas: dict):
    """
    Esta función actualiza a 'False' todos los bloques en los que todas las salas del diccionario entregado estén reservadas
    """
    for n in range(0, len(df.index)):
        nombre_sala = df.iloc[n].values[1]
        bloques_ocupados = separar_datos_horario(df.iloc[n].values[0])
        dict_salas[nombre_sala].actualizar_horarios(bloques_ocupados)


def guardar_datos_salas(dict_salas: dict):
    """
    Esta función guarda el diccionario conteniendo las instancias 'Sala' del campus SJ con sus respectivos horarios
    """
    directorio_datos_salas = os.path.join(*obtener_parametro("paths", "directorio_salas"))
    with open(directorio_datos_salas, "wb") as archivo_datos:
        pickle.dump(dict_salas, archivo_datos)


def actualizar_datos_salas_con_datos_locales():
    """
    Esta función se encarga de actualizar la información guardada en el archivo salas_sj.bin,
    para que corresponda a la guardada en la imagen de buscacursos seleccionada
    """
    print("\nGenerando una nueva base de datos")
    df = generar_dataframe()
    df_limpio = limpiar_dataframe(df)
    df_salas_unicas = df_limpio['Sala'].drop_duplicates()

    print("Eliminando duplicados y entradas 'SIN SALA'")
    dict_salas = generar_salas(df_salas_unicas)

    print("Actualizando horarios")
    actualizar_horarios_diccionario_salas(df_limpio, dict_salas)
    directorio_salas = os.path.join(*obtener_parametro("paths", "directorio_salas"))
    
    print(f"Guardando datos en '{directorio_salas}'\n")
    guardar_datos_salas(dict_salas)


def actualizar_datos_salas_con_webscrapper():
    print("\nGenerando una nueva base de datos")
    urls_data = obtener_parametro('urls-data')

    print("Generando urls")
    urls_list = ws.build_urls_list(urls_data['unidades_academicas'], urls_data)

    print("Añadiendo datos de buscacursos")
    df = ws.run_webscrapper(urls_list, urls_data, urls_data['unidades_academicas_por_codigo'], 
                                       urls_data['site_warnings'], urls_data['modulos'])
    
    print("Limpiando DataFrame")
    df_limpio = df.dropna()
    df_salas_unicas = df_limpio['Sala'].drop_duplicates()

    print("Generando objetos 'Sala'")
    dict_salas = generar_salas(df_salas_unicas)

    print("Actualizando horarios de Salas")
    actualizar_horarios_diccionario_salas(df_limpio, dict_salas)
    directorio_salas = os.path.join(*obtener_parametro("paths", "directorio_salas"))
    
    print(f"Guardando datos en '{directorio_salas}'\n")
    guardar_datos_salas(dict_salas)
    print("Guardado exitoso!")


def cargar_datos_salas() -> dict:
    """
    Esta función see encarga de leer el archivo indicado en el parámetro 'directorio_datos_salas',
    y retorna un diccionario con los datos de todas las salas del campus
    """
    directorio_datos_salas = os.path.join(*obtener_parametro("paths", "directorio_salas"))
    with open(directorio_datos_salas, "rb") as archivo_datos:
        dict_salas = pickle.load(archivo_datos)
    return dict_salas


def guardar_datos_salas_en_json():
    pass

# -------------------------------------------------------------------------------------------------

# Código:
if __name__ == "__main__":
    start_time = t.time()
    actualizar_datos_salas_con_webscrapper()

    """
    descomentar si se quiere utilizar un documento de excel de forma local
    actualizar_datos_salas()
    """
    
    print("--- %s seconds ---" % (t.time() - start_time))
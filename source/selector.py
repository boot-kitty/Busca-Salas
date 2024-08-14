# Imports Externos:
import datetime as dt
import time as t

# Imports Propios:
import lector_de_archivos as l
import salas as s

# -------------------------------------------------------------------------------------------------

# Funciones:
def determinar_dia_actual():
    """
    Esta función se encarga de determinar el día de la semana actual,
    y lo retorna como un 'str' de un único caracter
    """
    fecha_actual = dt.date.today()
    dias_semana = ["L", "M", "W", "J", "V", "S", "D"]
    return dias_semana[fecha_actual.weekday()]


def desocupada(sala: s.Sala, tupla_dia_bloque: tuple):
    return sala[1].horarios[tupla_dia_bloque[0]][tupla_dia_bloque[1] - 1]


def encontrar_sala_desocupada(dict_salas: dict, tupla_dia_bloque: tuple):
    salas_desocupadas = dict(filter(lambda sala: desocupada(sala, tupla_dia_bloque), dict_salas.items()))
    return salas_desocupadas


def ordernar_diccionario(dict_desordenado: dict) -> dict:
    lista_llaves = list(dict_desordenado.keys())
    lista_llaves.sort()
    dict_ordenado = {i: dict_desordenado[i] for i in lista_llaves}

    return dict_ordenado
# -------------------------------------------------------------------------------------------------

# Clases:
class Selector:

    def __init__(self):
        self.parametros_busqueda = l.obtener_parametro("preferencias")
        self.dict_salas = dict(filter(self.eliminar_salas_no_deseadas, l.cargar_datos_salas().items()))

    # Métodos
    def actualizar_salas(self):
        """
        Este método carga los datos guardados en el archivo 'directorio_datos_salas' inicado en parámetros.py
        """
        l.actualizar_datos_salas()
        self.dict_salas = dict(filter(self.eliminar_salas_no_deseadas, l.cargar_datos_salas()))


    def eliminar_salas_no_deseadas(self, tupla_sala):
        try:
            sala = tupla_sala[0]
            for edificio in self.parametros_busqueda['edificios_no_deseados']:
                if (edificio in str(sala)) or (str(sala) in self.parametros_busqueda["salas_no_deseadas"]):
                    return False
            return True
        
        except TypeError as E:
            print("Se ha eliminado la sala", tupla_sala, "por una excepción")


    def otorgar_puntaje_edificio(self, nombre_edificio):
        for i in range(0, len(self.parametros_busqueda['edificios_favoritos'])):
            edificio = self.parametros_busqueda['edificios_favoritos'][i]
    

    def encontrar_interseccion_horarios(self, tupla_requests: tuple):
        salas_disponibles = self.dict_salas
        for request in tupla_requests:
            salas_disponibles = encontrar_sala_desocupada(salas_disponibles, (request[0], request[1]))

        if len(salas_disponibles) == 0:
            print("No se han encontrado salas disponibles, se recomienda ajustar los parámetros de búsqueda")
            return {}
        
        else:
            return salas_disponibles
        

    def mostrar_resultados_busqueda(self, lista_de_busqueda: list, interseccion_resultados: dict, union_resultados: list):

        if interseccion_resultados is not None:
            print(f"Resultados de Búsqueda para: {lista_de_busqueda}\n\n"
                + "-"*15 + " Resultados Intersección " + "-"*15,
                "\n", *interseccion_resultados.keys(),
                "\n\n" + "-"*20 + " Resultados Unión " + "-"*17
                )
            
            for resultado in union_resultados:
                resultado = ordernar_diccionario(resultado)
                print(*resultado.keys(),
                      "\n" + "-"*58)

        else:
            resultado = ordernar_diccionario(union_resultados[0])
            print(f"Resultados de Búsqueda para: {lista_de_busqueda}\n\n"
                    + "-"*14 + " Resultados Búsqueda Única " + "-"*14 + "\n",
                    *resultado.keys(),
                    "\n" + "-"*58)


    def buscar_salas(self, lista_de_busqueda: list):
        union_resultados = []

        for request in lista_de_busqueda:
            resultados_request = encontrar_sala_desocupada(self.dict_salas, request)
            union_resultados.append(resultados_request)
        
        if len(lista_de_busqueda) > 1:
            interseccion_resultados = ordernar_diccionario(self.encontrar_interseccion_horarios(lista_de_busqueda))
            self.mostrar_resultados_busqueda(lista_de_busqueda, interseccion_resultados, union_resultados)

        else:
            self.mostrar_resultados_busqueda(lista_de_busqueda, None, union_resultados)
            

# -------------------------------------------------------------------------------------------------

# Código:
if __name__ == "__main__":
    start_time = t.time()
    selector = Selector()

    print("\nuwu")
    tupla_busqueda = [("L", 2)]
    selector.buscar_salas(tupla_busqueda)

    print("\n" + "--- %s seconds ---" % (t.time() - start_time))
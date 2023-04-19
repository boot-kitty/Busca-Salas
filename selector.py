# Imports Externos:
import datetime as dt
import time as t
import salas as s

# Imports Propios:
import lector_de_archivos as l

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


def determinar_numero_bloque():
    """
    Esta función se encarga de determinar el bloque actual de acuerdo a la hora correspondiente
    """
    hora_actual = dt.datetime.now()
    lista_hora_actual = hora_actual.strftime("%H:%M").split(":")
    hora = int(lista_hora_actual[0])
    minuto = int(lista_hora_actual[1])

    # Horarios antes del bloque 1
    if (hora <= 8) and (minuto < 30):
        bloque = -1

    elif (hora == 8 and minuto >= 30) or (hora == 9 and minuto <= 50):
        bloque = 1

    elif (hora == 9 and minuto > 50) or (hora == 10) or (hora == 11 and minuto <= 20):
        bloque = 2

    elif (hora == 11 and minuto > 20) or (hora == 12 and minuto <= 50):
        bloque = 3

    # Horario de almuerzo
    elif (hora == 12 and minuto > 50) or (hora == 13 and minuto <= 50):
        bloque = -2

    elif (hora == 13 and minuto > 50) or (hora == 14) or (hora == 15 and minuto <= 20):
        bloque = 4

    elif (hora == 15 and minuto > 20) or (hora == 16 and minuto <= 50):
        bloque = 5

    elif (hora == 17) or (hora == 18 and minuto <= 20):
        bloque = 6

    elif (hora == 18 and minuto > 20) or (hora == 19 and minuto <= 50):
        bloque = 7

    elif (hora == 19 and minuto > 50) or (hora == 20) or (hora == 21 and minuto <= 20):
        bloque = 8

    # Horarios después del bloque 8
    elif (hora == 21 and minuto > 20) or (hora > 21):
        bloque = -3

    return bloque


def determinar_bloque_actual():
    dia = determinar_dia_actual()
    bloque = determinar_numero_bloque()
    return (dia, bloque)


def desocupada(sala: s.Sala, tupla_dia_bloque: tuple):
    return sala[1].horarios[tupla_dia_bloque[0]][tupla_dia_bloque[1] - 1]


def encontrar_sala_desocupada(dict_salas: dict, tupla_dia_bloque: tuple):
    salas_desocupadas = dict(filter(lambda sala: desocupada(sala, tupla_dia_bloque), dict_salas.items()))
    return salas_desocupadas

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
    

    def encontrar_salas_horarios_multiples(self, dia: str, tupla_bloques: tuple):
        salas_disponibles = self.dict_salas
        for bloque in tupla_bloques:
            salas_disponibles = encontrar_sala_desocupada(salas_disponibles, (dia, bloque))

        if len(salas_disponibles) == 0:
            print("No se han encontrado salas disponibles, se recomienda ajustar los parámetros de búsqueda")
            return {}
        
        else:
            return salas_disponibles


# -------------------------------------------------------------------------------------------------

# Código:
if __name__ == "__main__":
    selector = Selector()
    start_time = t.time()

    """
    print("AP502", selector.dict_salas["AP502"].horarios["W"])
    """

    resultados1 = list(encontrar_sala_desocupada(selector.dict_salas, ("W", 1)).keys())
    resultados2 = list(encontrar_sala_desocupada(selector.dict_salas, ("W", 2)).keys())
    resultados3 = list(encontrar_sala_desocupada(selector.dict_salas, ("W", 3)).keys())
    resultados4 = list(encontrar_sala_desocupada(selector.dict_salas, ("W", 4)).keys())

    
    resultados = list(selector.encontrar_salas_horarios_multiples("W", (3, 4)).keys())
    resultados = sorted(resultados)
    
    resultados1 = sorted(resultados1)
    resultados2 = sorted(resultados2)
    resultados3 = sorted(resultados3)
    resultados4 = sorted(resultados4)

    print("Reultados de la búsqueda:")
    print("-"*60)
    print(resultados)

    print("-"*60)
    print(resultados1)
    print("-"*60)
    print(resultados2)
    print("-"*60)
    print(resultados3)
    print("-"*60)
    print(resultados4)
    input()
    

    print("--- %s seconds ---" % (t.time() - start_time))

    # !!!
    # J módulo 4 AP 504 aparece listada como disponible pero el atributo 'horario' de la sala dice lo contrario
    # M módulo 4 AP está ocupada y listada como disponible
    # !!!

    #J módulo 3 no hay AP
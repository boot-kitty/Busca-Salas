# Mensajes de error:
# Un diccionario que contiene una serie de mensajes de error recurrentes
mensajes_error = {
    -1000: "\nERROR: el número ingresado no se encuentra dentro de las opciones desplegadas",
    -2000: "\nERROR: el input ingresado no corresponde a un número, " 
            + "ni a la opción Salir del programa",
    1000: "\nERROR: la lista de búsqueda ingresada se encuentra vacía",
    2000: "\nERROR: la búsqueda realiza excede el limite de resultados que puede mostrar 'buscacursos'",
    2001: "\nERROR: la búsqueda realizada no entrega ningún resultado"
    }

# -------------------------------------------------------------------------------------------------

# Clases y manejo de excepciones:
class ErrorInputFueraDeRango(Exception):
    pass

class ErrorBusquedaMuyAmplia(Exception):
    # error asociado: 2000
    pass

class ErrorBusquedaVacia(Exception):
    # error asociado: 2001
    pass
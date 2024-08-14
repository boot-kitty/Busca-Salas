# Clases:

class Sala:

    def __init__(self, nombre):
        self.nombre = str(nombre)
        self.horarios = {'L':[True, True, True, True, True, True, True, True, True],
                        'M':[True, True, True, True, True, True, True, True, True],
                        'W':[True, True, True, True, True, True, True, True, True],
                        'J':[True, True, True, True, True, True, True, True, True],
                        'V':[True, True, True, True, True, True, True, True, True],
                        'S':[True, True, True, True, True, True, True, True, True]
                        }

    def actualizar_horarios(self, tp_dia_bloque):
        """
        Modifica las entradas del diccionario 'horarios', 
        cambiando a 'False' aquellos bloques en los que la sala se encuentra reservada
        """
        try:
            for dia in tp_dia_bloque[0]:
                for bloque in tp_dia_bloque[1]:
                    self.horarios[dia][(int(bloque) - 1)] = False
        
        except KeyError:
            print(f"Tupla omitida: {tp_dia_bloque} en {self.nombre}")

        except  ValueError:
            print(f"Tupla omitida: {tp_dia_bloque} en {self.nombre}")
# Imports Externos:
import sys

# Imports Propios:
import errores_y_excepciones as e
import selector as s

# -------------------------------------------------------------------------------------------------

# Código:
selector = s.Selector()
print("-"*4 + " Bienvenid@ a BuscaSalas SJ " + "-"*4 +"\n\n"
    + "Utiliza los números del teclado para interactuar con el programa.\n"
    + "Nota: la opción vacía '[-]' corresponde a una tecla cualquiera.\n")

while True:

    print("\n*** Menú de Principal *** \n"
            + "-"*23
            + "\n[1] Buscar una sala disponible ahora"
            + "\n[2] Busqueda personalizada"
            + "\n[3] Ajustar parámetros de búsqueda"
            + "\n[4] Refrescar lista de salas"
            + "\n[X] Salir del programa\n"
            )
    opcion_elegida_menu_principal = input("Ingrese la opción elegida:\n")
        
    try:
        if int(opcion_elegida_menu_principal) == 1:
            pass

        elif int(opcion_elegida_menu_principal) == 2:
            pass

        elif int(opcion_elegida_menu_principal) == 3:
            pass

        elif int(opcion_elegida_menu_principal) == 4:
            selector.actualizar_salas()
            print("La base de datos de Salas se ha actualizado exitosamente")

        else:
            raise e.ErrorInputFueraDeRango

    except ValueError:
        if (opcion_elegida_menu_principal == "x") or (opcion_elegida_menu_principal == "X"):
            sys.exit()
        else:
            print(e.mensajes_error.get(-2000))

    except e.ErrorInputFueraDeRango:
        print(e.mensajes_error.get(-1000))
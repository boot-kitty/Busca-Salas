# Imports externos
import sys
import os

# Imports propios (source)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'source')))

import web_scrapper as ws
import lector_de_archivos as la
import selector as s
# -------------------------------------------------------------------------------------------------

selector = s.Selector()
s.encontrar_sala_desocupada(selector.dict_salas, ("J", 2))
"""
A7 = selector.dict_salas["A7"]
print(A7.nombre)
print(A7.horarios)
"""
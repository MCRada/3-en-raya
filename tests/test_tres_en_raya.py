import pytest
from tres_en_raya import TresEnRaya

def test_empieza_X():
    assert TresEnRaya().turno == "X"

def test_turnos_alternan():
    j = TresEnRaya(); j.jugar(0, 0)
    assert j.turno == "O"

def test_casilla_ocupada():
    j = TresEnRaya(); j.jugar(0, 0)
    with pytest.raises(ValueError):
        j.jugar(0, 0)

def test_fuera_del_tablero():
    with pytest.raises(ValueError):
        TresEnRaya().jugar(3, 0)

def test_gana_fila():
    j = TresEnRaya()
    for m in [(0,0),(1,0),(0,1),(1,1),(0,2)]: j.jugar(*m)
    assert j.ganador() == "X"

def test_gana_columna():
    j = TresEnRaya()
    for m in [(0,0),(0,1),(1,0),(1,1),(2,0)]: j.jugar(*m)
    assert j.ganador() == "X"

def test_gana_diagonal():
    j = TresEnRaya()
    for m in [(0,0),(0,1),(1,1),(0,2),(2,2)]: j.jugar(*m)
    assert j.ganador() == "X"

def test_empate():
    j = TresEnRaya()
    for m in [(0,0),(0,1),(0,2),(1,1),(1,0),(1,2),(2,1),(2,0),(2,2)]: j.jugar(*m)
    assert j.ganador() is None and j.es_empate()

def test_no_se_juega_tras_ganar():
    j = TresEnRaya()
    for m in [(0,0),(1,0),(0,1),(1,1),(0,2)]: j.jugar(*m)
    with pytest.raises(ValueError):
        j.jugar(2, 2)
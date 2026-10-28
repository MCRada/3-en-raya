"""Pruebas unitarias (pytest) para la kata del Tres en Raya.

Supuestos del contrato (ajustar aquí si tu implementación difiere):
  - Módulo `tres_en_raya` con la clase `TresEnRaya`.
  - Coordenadas base 0: fila y columna en el rango 0..2.
  - ganador() -> "X" | "O" | None
  - es_empate() -> bool
  - Las jugadas inválidas lanzan ERROR_JUGADA.
"""
from itertools import combinations

import pytest

from tres_en_raya import TresEnRaya

ERROR_JUGADA = ValueError
ERROR_TIPO = (ValueError, TypeError)

# --------------------------------------------------------------------------
# Datos y utilidades
# --------------------------------------------------------------------------
CELDAS = [(f, c) for f in range(3) for c in range(3)]

FILAS = [[(f, c) for c in range(3)] for f in range(3)]
COLUMNAS = [[(f, c) for f in range(3)] for c in range(3)]
DIAGONALES = [[(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
LINEAS = FILAS + COLUMNAS + DIAGONALES
LINEAS_SET = [frozenset(linea) for linea in LINEAS]

IDS_LINEAS = (
    [f"fila{i}" for i in range(3)]
    + [f"columna{i}" for i in range(3)]
    + ["diagonal_principal", "diagonal_secundaria"]
)


def jugar_secuencia(juego, movimientos):
    """Aplica una lista de (fila, col) en orden."""
    for fila, col in movimientos:
        juego.jugar(fila, col)


def secuencia_gana_x(linea):
    """X completa `linea` en su 3.er turno; O juega 2 casillas fuera de ella."""
    otras = [c for c in CELDAS if c not in linea][:2]
    return [linea[0], otras[0], linea[1], otras[1], linea[2]]


def secuencia_gana_o(linea):
    """O completa `linea` en su 3.er turno; X juega 3 casillas sin formar línea."""
    otras = [c for c in CELDAS if c not in linea]
    jugadas_x = next(
        combo for combo in combinations(otras, 3) if frozenset(combo) not in LINEAS_SET
    )
    return [
        jugadas_x[0], linea[0],
        jugadas_x[1], linea[1],
        jugadas_x[2], linea[2],
    ]


# Empate: tablero final
#   X O X
#   X O O
#   O X X
SECUENCIA_EMPATE = [
    (0, 0), (0, 1), (0, 2),
    (1, 1), (1, 0), (1, 2),
    (2, 1), (2, 0), (2, 2),
]

# Victoria de X en la 9.ª (última) jugada: tablero final
#   X X X
#   O O X
#   X O O
SECUENCIA_VICTORIA_ULTIMA_JUGADA = [
    (0, 0), (1, 0), (0, 1), (1, 1), (1, 2), (2, 1), (2, 0), (2, 2), (0, 2),
]


@pytest.fixture
def juego():
    return TresEnRaya()


# --------------------------------------------------------------------------
# Estado inicial
# --------------------------------------------------------------------------
class TestEstadoInicial:
    def test_partida_nueva_no_tiene_ganador(self, juego):
        assert juego.ganador() is None

    def test_partida_nueva_no_es_empate(self, juego):
        assert juego.es_empate() is False

    def test_instancias_son_independientes(self):
        a, b = TresEnRaya(), TresEnRaya()
        a.jugar(0, 0)
        # La casilla (0,0) sigue libre en la otra partida.
        b.jugar(0, 0)
        assert b.ganador() is None


# --------------------------------------------------------------------------
# Turnos
# --------------------------------------------------------------------------
class TestTurnos:
    def test_x_empieza(self, juego):
        # Si X empieza, tras X(0,0) O(1,0) X(0,1) O(1,1) X(0,2) gana X.
        jugar_secuencia(juego, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        assert juego.ganador() == "X"

    def test_los_turnos_se_alternan(self, juego):
        # Si no alternaran, el ganador de esta secuencia sería otro.
        jugar_secuencia(juego, secuencia_gana_o(DIAGONALES[0]))
        assert juego.ganador() == "O"

    def test_jugada_valida_no_declara_ganador_ni_empate(self, juego):
        juego.jugar(1, 1)
        assert juego.ganador() is None
        assert juego.es_empate() is False

    def test_jugada_invalida_no_consume_el_turno(self, juego):
        juego.jugar(0, 0)  # X
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(0, 0)  # O intenta casilla ocupada -> error
        # Debe seguir siendo turno de O.
        jugar_secuencia(juego, [(1, 1), (0, 1), (2, 2), (0, 2)])
        assert juego.ganador() == "X"  # X completó la fila 0

    def test_jugada_fuera_de_tablero_no_consume_el_turno(self, juego):
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(3, 3)  # X falla
        # Debe seguir siendo turno de X.
        jugar_secuencia(juego, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
        assert juego.ganador() == "X"


# --------------------------------------------------------------------------
# Victorias
# --------------------------------------------------------------------------
class TestVictoriaX:
    @pytest.mark.parametrize("linea", LINEAS, ids=IDS_LINEAS)
    def test_x_gana_completando_linea(self, juego, linea):
        jugar_secuencia(juego, secuencia_gana_x(linea))
        assert juego.ganador() == "X"
        assert juego.es_empate() is False


class TestVictoriaO:
    @pytest.mark.parametrize("linea", LINEAS, ids=IDS_LINEAS)
    def test_o_gana_completando_linea(self, juego, linea):
        jugar_secuencia(juego, secuencia_gana_o(linea))
        assert juego.ganador() == "O"
        assert juego.es_empate() is False


class TestSinGanadorTodavia:
    def test_dos_en_linea_no_es_victoria(self, juego):
        jugar_secuencia(juego, [(0, 0), (1, 0), (0, 1)])
        assert juego.ganador() is None

    def test_tres_casillas_no_alineadas_no_es_victoria(self, juego):
        # X: (0,0) (0,2) (2,1)  -> no forman línea
        jugar_secuencia(juego, [(0, 0), (1, 0), (0, 2), (1, 1), (2, 1)])
        assert juego.ganador() is None

    def test_tres_en_linea_de_fichas_mixtas_no_es_victoria(self, juego):
        # Fila 0 queda X, O, X: llena pero sin ganador.
        jugar_secuencia(juego, [(0, 0), (0, 1), (0, 2)])
        assert juego.ganador() is None


# --------------------------------------------------------------------------
# Empate
# --------------------------------------------------------------------------
class TestEmpate:
    def test_tablero_lleno_sin_ganador_es_empate(self, juego):
        jugar_secuencia(juego, SECUENCIA_EMPATE)
        assert juego.es_empate() is True
        assert juego.ganador() is None

    def test_no_hay_empate_antes_de_llenar_el_tablero(self, juego):
        jugar_secuencia(juego, SECUENCIA_EMPATE[:-1])  # 8 jugadas
        assert juego.es_empate() is False
        assert juego.ganador() is None

    def test_victoria_en_la_ultima_jugada_no_es_empate(self, juego):
        jugar_secuencia(juego, SECUENCIA_VICTORIA_ULTIMA_JUGADA)
        assert juego.ganador() == "X"
        assert juego.es_empate() is False

    def test_victoria_antes_de_llenar_tablero_no_es_empate(self, juego):
        jugar_secuencia(juego, secuencia_gana_x(FILAS[0]))
        assert juego.es_empate() is False


# --------------------------------------------------------------------------
# Errores: casilla ocupada
# --------------------------------------------------------------------------
class TestCasillaOcupada:
    def test_no_se_puede_jugar_en_casilla_ocupada_por_el_otro(self, juego):
        juego.jugar(1, 1)  # X
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(1, 1)  # O

    def test_no_se_puede_jugar_en_casilla_ocupada_por_si_mismo(self, juego):
        jugar_secuencia(juego, [(0, 0), (1, 1)])  # X, O
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(0, 0)  # X repite casilla

    @pytest.mark.parametrize("casilla", CELDAS)
    def test_cualquier_casilla_ocupada_es_rechazada(self, juego, casilla):
        juego.jugar(*casilla)
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(*casilla)

    def test_intento_en_casilla_ocupada_no_altera_el_ganador(self, juego):
        juego.jugar(0, 0)
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(0, 0)
        assert juego.ganador() is None
        assert juego.es_empate() is False


# --------------------------------------------------------------------------
# Errores: fuera del tablero
# --------------------------------------------------------------------------
class TestFueraDelTablero:
    @pytest.mark.parametrize(
        "fila, col",
        [
            (-1, 0),
            (0, -1),
            (-1, -1),
            (3, 0),
            (0, 3),
            (3, 3),
            (10, 1),
            (1, 10),
            (-100, 100),
        ],
    )
    def test_coordenadas_fuera_de_rango_son_rechazadas(self, juego, fila, col):
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(fila, col)

    def test_indice_negativo_no_se_interpreta_como_desde_el_final(self, juego):
        # En Python tablero[-1] sería la última fila; debe rechazarse igualmente.
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(-1, -1)
        # Y la casilla (2,2) debe seguir libre.
        juego.jugar(2, 2)

    @pytest.mark.parametrize("casilla", [(0, 0), (0, 2), (2, 0), (2, 2), (1, 1)])
    def test_limites_validos_son_aceptados(self, juego, casilla):
        juego.jugar(*casilla)  # no debe lanzar


class TestTiposInvalidos:
    @pytest.mark.parametrize(
        "fila, col",
        [(None, 0), (0, None), ("a", 0), (0, "b"), (1.5, 0), (0, 1.5)],
    )
    def test_argumentos_no_enteros_son_rechazados(self, juego, fila, col):
        with pytest.raises(ERROR_TIPO):
            juego.jugar(fila, col)


# --------------------------------------------------------------------------
# Errores: jugar después de terminar
# --------------------------------------------------------------------------
class TestPartidaTerminada:
    def test_no_se_puede_jugar_tras_victoria_de_x(self, juego):
        jugar_secuencia(juego, secuencia_gana_x(FILAS[0]))
        libre = next(c for c in CELDAS if c not in juego_ocupadas_x(FILAS[0]))
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(*libre)

    def test_no_se_puede_jugar_tras_victoria_de_o(self, juego):
        movs = secuencia_gana_o(COLUMNAS[1])
        jugar_secuencia(juego, movs)
        libre = next(c for c in CELDAS if c not in movs)
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(*libre)

    def test_no_se_puede_jugar_tras_empate(self, juego):
        jugar_secuencia(juego, SECUENCIA_EMPATE)
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(0, 0)

    def test_no_se_puede_jugar_tras_victoria_en_ultima_jugada(self, juego):
        jugar_secuencia(juego, SECUENCIA_VICTORIA_ULTIMA_JUGADA)
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(1, 1)

    def test_jugada_fuera_de_tablero_tras_terminar_tambien_falla(self, juego):
        jugar_secuencia(juego, secuencia_gana_x(FILAS[0]))
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(5, 5)

    def test_intento_tras_terminar_no_cambia_el_resultado(self, juego):
        jugar_secuencia(juego, secuencia_gana_x(DIAGONALES[0]))
        libre = next(c for c in CELDAS if c not in juego_ocupadas_x(DIAGONALES[0]))
        with pytest.raises(ERROR_JUGADA):
            juego.jugar(*libre)
        assert juego.ganador() == "X"
        assert juego.es_empate() is False

    def test_consultas_son_idempotentes(self, juego):
        jugar_secuencia(juego, secuencia_gana_x(FILAS[2]))
        assert juego.ganador() == juego.ganador() == "X"
        assert juego.es_empate() is juego.es_empate() is False


def juego_ocupadas_x(linea):
    """Casillas usadas por secuencia_gana_x(linea) (para elegir una libre)."""
    return set(secuencia_gana_x(linea))
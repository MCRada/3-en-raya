class TresEnRaya:
    LINEAS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

    def __init__(self):
        self.tablero = [None] * 9
        self.turno = "X"

    def jugar(self, fila, col):
        if self.ganador() or self.es_empate():
            raise ValueError("El juego ya terminó")
        if not (0 <= fila < 3 and 0 <= col < 3):
            raise ValueError("Fuera del tablero")
        i = fila * 3 + col
        if self.tablero[i] is not None:
            raise ValueError("Casilla ocupada")
        self.tablero[i] = self.turno
        self.turno = "O" if self.turno == "X" else "X"

    def ganador(self):
        for a, b, c in self.LINEAS:
            if self.tablero[a] and self.tablero[a] == self.tablero[b] == self.tablero[c]:
                return self.tablero[a]
        return None

    def es_empate(self):
        return self.ganador() is None and all(self.tablero)
"""
Tabuleiro do Gomoku 9x9.
Gerencia o estado do jogo (peças) e verifica vitória e empate.
"""

BOARD_SIZE = 9
EMPTY = 0
HUMAN = 1   # peças pretas
AI = 2      # peças brancas

# Direções para detectar 5 em linha: horizontal, vertical e 2 diagonais
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


class Board:
    """Representa o tabuleiro como uma matriz 9x9 e oferece operações básicas."""

    def __init__(self):
        # Cria uma matriz 9x9 preenchida com zeros (células vazias)
        self.grid = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def place(self, row, col, player):
        """Coloca uma peça do jogador na posição (row, col)."""
        self.grid[row][col] = player

    def undo(self, row, col):
        """Remove uma peça da posição (usado pelo minimax para simular jogadas)."""
        self.grid[row][col] = EMPTY

    def is_empty(self, row, col):
        """Retorna True se a célula estiver vazia."""
        return self.grid[row][col] == EMPTY

    def get_candidate_moves(self, radius=1):
        """
        Retorna apenas células vazias próximas a peças já existentes.
        Reduz o espaço de busca do minimax (em vez de testar todas as 81 células).
        Se o tabuleiro estiver vazio, retorna o centro.
        """
        candidates = set()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col] == EMPTY:
                    continue
                # Para cada peça encontrada, adiciona as células vazias vizinhas
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < BOARD_SIZE and
                                0 <= nc < BOARD_SIZE and
                                self.grid[nr][nc] == EMPTY):
                            candidates.add((nr, nc))
        # Se nenhuma peça foi jogada ainda, retorna o centro do tabuleiro
        if not candidates:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        return list(candidates)

    def check_victory(self, player):
        """Verifica se o jogador formou 5 peças consecutivas em alguma direção."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col] != player:
                    continue
                # Para cada direção, conta peças consecutivas a partir desta célula
                for dr, dc in DIRECTIONS:
                    count = 1
                    for i in range(1, 5):
                        nr, nc = row + dr * i, col + dc * i
                        if (0 <= nr < BOARD_SIZE and
                                0 <= nc < BOARD_SIZE and
                                self.grid[nr][nc] == player):
                            count += 1
                        else:
                            break
                    if count >= 5:
                        return True
        return False

    def check_draw(self):
        """Empate: tabuleiro totalmente preenchido sem nenhum vencedor."""
        for row in self.grid:
            if EMPTY in row:
                return False
        return True

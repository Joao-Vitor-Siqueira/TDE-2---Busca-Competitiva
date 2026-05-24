"""
Funções de avaliação heurística (uma para cada nível de dificuldade).

Convenção: score positivo é bom para a IA, score negativo é bom para o humano.
Todas seguem a forma: score_ia - score_humano.
"""

from board import BOARD_SIZE, EMPTY, HUMAN, AI, DIRECTIONS


def _count_sequences(grid, player):
    """
    Conta sequências consecutivas do jogador no tabuleiro.
    Retorna dict {tamanho: quantidade}, considerando sequências de 2 a 5.
    Cada sequência é contada uma única vez (verifica se é o início).
    """
    counts = {2: 0, 3: 0, 4: 0, 5: 0}
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if grid[row][col] != player:
                continue
            for dr, dc in DIRECTIONS:
                # Verifica se a célula anterior na direção NÃO é do mesmo jogador
                # (assim contamos cada sequência uma única vez, pelo seu início)
                pr, pc = row - dr, col - dc
                if (0 <= pr < BOARD_SIZE and
                        0 <= pc < BOARD_SIZE and
                        grid[pr][pc] == player):
                    continue
                # Conta peças consecutivas a partir desta célula
                count = 0
                r, c = row, col
                while (0 <= r < BOARD_SIZE and
                       0 <= c < BOARD_SIZE and
                       grid[r][c] == player):
                    count += 1
                    r += dr
                    c += dc
                if count >= 5:
                    counts[5] += 1
                elif count in counts:
                    counts[count] += 1
    return counts


def _count_open_sequences(grid, player):
    """
    Conta sequências classificando como ABERTA (vivas, com as duas pontas livres)
    ou FECHADA (ao menos uma ponta bloqueada por borda ou peça adversária).
    Retorna: {tamanho: {'open': N, 'closed': N}}
    """
    counts = {n: {'open': 0, 'closed': 0} for n in (2, 3, 4, 5)}

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if grid[row][col] != player:
                continue
            for dr, dc in DIRECTIONS:
                # Pula se não for o início da sequência
                pr, pc = row - dr, col - dc
                if (0 <= pr < BOARD_SIZE and
                        0 <= pc < BOARD_SIZE and
                        grid[pr][pc] == player):
                    continue
                # Conta peças consecutivas
                count = 0
                r, c = row, col
                while (0 <= r < BOARD_SIZE and
                       0 <= c < BOARD_SIZE and
                       grid[r][c] == player):
                    count += 1
                    r += dr
                    c += dc
                # Pontas abertas = células vazias antes e depois da sequência
                open_before = (0 <= pr < BOARD_SIZE and
                               0 <= pc < BOARD_SIZE and
                               grid[pr][pc] == EMPTY)
                open_after = (0 <= r < BOARD_SIZE and
                              0 <= c < BOARD_SIZE and
                              grid[r][c] == EMPTY)
                size = min(count, 5)
                if open_before and open_after:
                    counts[size]['open'] += 1
                else:
                    counts[size]['closed'] += 1
    return counts


# ---------------- NÍVEL INICIANTE ----------------

def evaluate_easy(board):
    """
    Heurística simples: apenas conta pares, trincas, quadras e quintas.
    Score = pontos da IA - pontos do humano.
    """
    weights = {2: 10, 3: 100, 4: 10000, 5: 100000}
    ai_counts = _count_sequences(board.grid, AI)
    human_counts = _count_sequences(board.grid, HUMAN)

    score = 0
    for size, weight in weights.items():
        score += weight * ai_counts[size]
        score -= weight * human_counts[size]
    return score


# ---------------- NÍVEL INTERMEDIÁRIO ----------------

def evaluate_intermediate(board):
    """
    Heurística mais rica:
    - distingue sequências abertas (vivas) e fechadas (vale mais quando aberta)
    - bônus por jogar próximo ao centro
    - penaliza ameaças do humano (multiplicador 1.2)
    """
    weights = {
        2: {'open': 20,    'closed': 5},
        3: {'open': 500,   'closed': 50},
        4: {'open': 20000, 'closed': 1000},
        5: {'open': 100000,'closed': 100000},
    }
    ai_counts = _count_open_sequences(board.grid, AI)
    human_counts = _count_open_sequences(board.grid, HUMAN)

    score = 0
    for size in (2, 3, 4, 5):
        score += weights[size]['open']   * ai_counts[size]['open']
        score += weights[size]['closed'] * ai_counts[size]['closed']
        # Penaliza ameaças do humano com peso 1.2 (defensiva)
        score -= weights[size]['open']   * human_counts[size]['open']   * 1.2
        score -= weights[size]['closed'] * human_counts[size]['closed'] * 1.2

    # Bônus por centralidade: peças mais próximas do centro valem mais
    center = BOARD_SIZE // 2
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board.grid[row][col] == AI:
                dist = abs(row - center) + abs(col - center)
                score += (BOARD_SIZE - dist)

    return int(score)


# ---------------- NÍVEL PROFISSIONAL ----------------

def evaluate_hard(board):
    """
    Heurística avançada:
    - pesos maiores para sequências abertas (vivas)
    - forte penalização para ameaças do humano (multiplicador 1.5)
    - detecção de forks: duas ou mais trincas abertas = ameaça dupla
    - bônus reforçado por centralidade
    """
    weights = {
        2: {'open': 50,     'closed': 10},
        3: {'open': 1000,   'closed': 100},
        4: {'open': 50000,  'closed': 5000},
        5: {'open': 1000000,'closed': 1000000},
    }
    ai_counts = _count_open_sequences(board.grid, AI)
    human_counts = _count_open_sequences(board.grid, HUMAN)

    score = 0
    for size in (2, 3, 4, 5):
        score += weights[size]['open']   * ai_counts[size]['open']
        score += weights[size]['closed'] * ai_counts[size]['closed']
        # Penalização defensiva forte (1.5) para ameaças do humano
        score -= weights[size]['open']   * human_counts[size]['open']   * 1.5
        score -= weights[size]['closed'] * human_counts[size]['closed'] * 1.5

    # Detecção de fork (ameaça dupla): duas trincas abertas simultâneas
    if ai_counts[3]['open'] >= 2:
        score += 10000   # IA criou um fork ofensivo
    if human_counts[3]['open'] >= 2:
        score -= 15000   # Humano criou fork - precisamos defender com urgência

    # Bônus por centralidade reforçado
    center = BOARD_SIZE // 2
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board.grid[row][col] == AI:
                dist = abs(row - center) + abs(col - center)
                score += (BOARD_SIZE - dist) * 2

    return int(score)


def get_evaluator(difficulty):
    """Retorna a função de avaliação apropriada para a dificuldade escolhida."""
    return {
        "Easy": evaluate_easy,
        "Intermediate": evaluate_intermediate,
        "Hard": evaluate_hard,
    }[difficulty]

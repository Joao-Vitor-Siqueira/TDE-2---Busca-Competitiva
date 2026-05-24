"""
Agente de IA do Gomoku com 3 níveis de dificuldade.

- Iniciante:     Minimax puro (sem poda alfa-beta)         - profundidade 2
- Intermediario: Minimax com poda alfa-beta                - profundidade 4
- Profissional:  Alfa-beta + ordenacao + limite de tempo   - aprofundamento iterativo
"""

import time
from board import HUMAN, AI
from heuristics import evaluate_easy, evaluate_intermediate, evaluate_hard

# Configurações de cada nível
EASY_DEPTH = 2
INTERMEDIATE_DEPTH = 4
HARD_MAX_DEPTH = 10        # profundidade máxima tentada (>6 conforme requisito)
HARD_TIME_LIMIT = 3.0      # limite obrigatório de 3 segundos por jogada

# Constantes de vitória/derrota usadas como retorno terminal
WIN_SCORE = 10_000_000
LOSE_SCORE = -10_000_000


class TimeoutException(Exception):
    """Lançada pela busca hard quando o limite de tempo é excedido."""
    pass


# =================== NÍVEL INICIANTE: Minimax puro ===================

def minimax_easy(board, depth, maxing):
    """Minimax clássico, sem poda. Explora todos os ramos até a profundidade."""
    # Caso terminal: alguém venceu
    if board.check_victory(AI):
        return WIN_SCORE
    if board.check_victory(HUMAN):
        return LOSE_SCORE
    # Profundidade esgotada: avalia o estado atual com a heurística
    if depth == 0:
        return evaluate_easy(board)

    candidates = board.get_candidate_moves(radius=1)

    if maxing:
        best = float('-inf')
        for row, col in candidates:
            board.place(row, col, AI)
            score = minimax_easy(board, depth - 1, False)
            board.undo(row, col)
            best = max(best, score)
        return best
    else:
        best = float('inf')
        for row, col in candidates:
            board.place(row, col, HUMAN)
            score = minimax_easy(board, depth - 1, True)
            board.undo(row, col)
            best = min(best, score)
        return best


# =================== NÍVEL INTERMEDIÁRIO: Minimax + alfa-beta ===================

def minimax_intermediate(board, depth, alpha, beta, maxing):
    """Minimax com poda alfa-beta: corta ramos que não podem melhorar o resultado."""
    if board.check_victory(AI):
        return WIN_SCORE
    if board.check_victory(HUMAN):
        return LOSE_SCORE
    if depth == 0:
        return evaluate_intermediate(board)

    candidates = board.get_candidate_moves(radius=1)

    if maxing:
        best = float('-inf')
        for row, col in candidates:
            board.place(row, col, AI)
            score = minimax_intermediate(board, depth - 1, alpha, beta, False)
            board.undo(row, col)
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break   # poda beta: o adversario nao escolheria este ramo
        return best
    else:
        best = float('inf')
        for row, col in candidates:
            board.place(row, col, HUMAN)
            score = minimax_intermediate(board, depth - 1, alpha, beta, True)
            board.undo(row, col)
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break   # poda alfa: a IA nao escolheria este ramo
        return best


# =================== NÍVEL PROFISSIONAL: alfa-beta + ordenação + tempo ===================

def _order_moves(board, candidates, maxing):
    """
    Ordena os candidatos pela avaliação heurística para acelerar a poda.
    Movimentos promissores primeiro = mais cortes alfa-beta.
    """
    player = AI if maxing else HUMAN
    scored = []
    for row, col in candidates:
        board.place(row, col, player)
        score = evaluate_hard(board)
        board.undo(row, col)
        scored.append((score, row, col))
    # max quer maior score primeiro; min quer menor primeiro
    scored.sort(reverse=maxing)
    return [(r, c) for _, r, c in scored]


def minimax_hard(board, depth, alpha, beta, maxing, start_time):
    """Minimax com poda alfa-beta, ordenação de movimentos e checagem de timeout."""
    # Verifica timeout antes de qualquer trabalho
    if time.time() - start_time > HARD_TIME_LIMIT:
        raise TimeoutException()

    if board.check_victory(AI):
        return WIN_SCORE
    if board.check_victory(HUMAN):
        return LOSE_SCORE
    if depth == 0:
        return evaluate_hard(board)

    candidates = board.get_candidate_moves(radius=1)
    candidates = _order_moves(board, candidates, maxing)

    if maxing:
        best = float('-inf')
        for row, col in candidates:
            board.place(row, col, AI)
            score = minimax_hard(board, depth - 1, alpha, beta, False, start_time)
            board.undo(row, col)
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float('inf')
        for row, col in candidates:
            board.place(row, col, HUMAN)
            score = minimax_hard(board, depth - 1, alpha, beta, True, start_time)
            board.undo(row, col)
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


# =================== Função principal: escolhe a jogada da IA ===================

def get_ai_move(board, difficulty):
    """
    Decide o melhor movimento para a IA na dificuldade escolhida.
    Retorna: (linha, coluna, score)
    """
    candidates = board.get_candidate_moves(radius=1)
    best_move = candidates[0]
    best_score = float('-inf')

    if difficulty == "Easy":
        for row, col in candidates:
            board.place(row, col, AI)
            score = minimax_easy(board, EASY_DEPTH - 1, False)
            board.undo(row, col)
            if score > best_score:
                best_score = score
                best_move = (row, col)

    elif difficulty == "Intermediate":
        alpha, beta = float('-inf'), float('inf')
        for row, col in candidates:
            board.place(row, col, AI)
            score = minimax_intermediate(board, INTERMEDIATE_DEPTH - 1,
                                         alpha, beta, False)
            board.undo(row, col)
            if score > best_score:
                best_score = score
                best_move = (row, col)
                alpha = max(alpha, score)

    else:  # Hard: aprofundamento iterativo (depth 2, 3, 4, ...) com limite de tempo
        start_time = time.time()
        for depth in range(2, HARD_MAX_DEPTH + 1):
            try:
                # Tenta completar a busca nesta profundidade
                depth_best_move = best_move
                depth_best_score = float('-inf')
                alpha, beta = float('-inf'), float('inf')
                ordered = _order_moves(board, candidates, True)
                for row, col in ordered:
                    board.place(row, col, AI)
                    score = minimax_hard(board, depth - 1,
                                         alpha, beta, False, start_time)
                    board.undo(row, col)
                    if score > depth_best_score:
                        depth_best_score = score
                        depth_best_move = (row, col)
                        alpha = max(alpha, score)
                # Profundidade completa: atualiza o melhor resultado
                best_move = depth_best_move
                best_score = depth_best_score
            except TimeoutException:
                # Tempo esgotado: usa o melhor da profundidade anterior
                break

    return best_move[0], best_move[1], best_score

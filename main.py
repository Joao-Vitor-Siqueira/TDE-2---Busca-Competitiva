"""
Gomoku 9x9 - TDE 2: Busca Competitiva (Inteligência Artificial)

Autores: [adicionar nomes dos integrantes do grupo]

Como jogar:
  - Selecione a dificuldade no menu inicial (Iniciante / Intermediario / Profissional).
  - Voce (peças PRETAS) joga primeiro clicando em uma celula vazia.
  - A IA (peças BRANCAS) responde automaticamente apos cada jogada sua.
  - Vence quem alinhar 5 peças em linha (horizontal, vertical ou diagonal).
"""

import sys
import time
import pygame

from board import Board, HUMAN, AI
from ai import get_ai_move
from heuristics import get_evaluator
from ui import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    draw_board, draw_hud, draw_menu, get_cell_from_mouse,
)


def print_board_terminal(board):
    """Imprime o tabuleiro como matriz no terminal (X = humano, O = IA)."""
    symbols = {0: '.', HUMAN: 'X', AI: 'O'}
    print("    " + "  ".join(chr(65 + i) for i in range(9)))
    for i, row in enumerate(board.grid):
        print(f"{i+1:2}  " + "  ".join(symbols[v] for v in row))
    print()


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gomoku 9x9 - TDE 2")
    clock = pygame.time.Clock()

    # Fontes
    font_coords = pygame.font.SysFont("Arial", 18, bold=True)
    font_hud = pygame.font.SysFont("Arial", 18)
    font_title = pygame.font.SysFont("Arial", 56, bold=True)
    font_button = pygame.font.SysFont("Arial", 22, bold=True)

    # Estado da aplicação
    state = "menu"          # "menu" ou "game"
    difficulty = None
    board = None
    evaluator = None
    current_player = HUMAN
    turn_count = 1
    game_over = False
    winner = None
    last_ai_time = 0.0
    last_score = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # ==================== TELA DE MENU ====================
        if state == "menu":
            button_rects = draw_menu(screen, font_title, font_button, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    # Verifica se algum botao foi clicado
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            difficulty = ["Easy", "Intermediate", "Hard"][i]
                            # Inicializa um novo jogo
                            board = Board()
                            evaluator = get_evaluator(difficulty)
                            current_player = HUMAN
                            turn_count = 1
                            game_over = False
                            winner = None
                            last_ai_time = 0.0
                            last_score = 0
                            state = "game"
                            print(f"\n=== JOGO INICIADO - Dificuldade: {difficulty} ===\n")
                            break

            pygame.display.flip()
            clock.tick(60)
            continue

        # ==================== TURNO DO HUMANO ====================
        # Lemos eventos do pygame e tratamos cliques na tabela
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (current_player == HUMAN
                  and not game_over
                  and event.type == pygame.MOUSEBUTTONDOWN
                  and event.button == 1):
                cell = get_cell_from_mouse(event.pos)
                if cell is None:
                    continue
                row, col = cell
                if not board.is_empty(row, col):
                    continue
                # Jogada valida
                board.place(row, col, HUMAN)
                last_score = evaluator(board)
                print(f"Turno {turn_count} - Humano jogou em {chr(65+col)}{row+1}")
                print_board_terminal(board)
                print(f"Avaliacao do estado: {last_score}\n")

                if board.check_victory(HUMAN):
                    game_over = True
                    winner = HUMAN
                    print(">>> HUMANO VENCEU! <<<\n")
                elif board.check_draw():
                    game_over = True
                    winner = 0
                    print(">>> EMPATE! <<<\n")
                else:
                    current_player = AI
                    turn_count += 1

        # ==================== TURNO DA IA ====================
        # IMPORTANTE: fora do loop de eventos para executar apenas UMA vez por turno
        if current_player == AI and not game_over:
            # Mostra a tela atualizada antes de pensar (peça do humano visível)
            draw_board(screen, board, font_coords)
            draw_hud(screen, font_hud, current_player, turn_count,
                     last_ai_time, last_score, difficulty, game_over, winner)
            pygame.display.flip()

            start = time.time()
            row, col, score = get_ai_move(board, difficulty)
            last_ai_time = time.time() - start
            board.place(row, col, AI)
            last_score = score

            print(f"Turno {turn_count} - IA jogou em {chr(65+col)}{row+1}")
            print_board_terminal(board)
            print(f"Tempo da jogada: {last_ai_time:.2f}s")
            print(f"Avaliacao do estado: {last_score}\n")

            if board.check_victory(AI):
                game_over = True
                winner = AI
                print(">>> IA VENCEU! <<<\n")
            elif board.check_draw():
                game_over = True
                winner = 0
                print(">>> EMPATE! <<<\n")
            else:
                current_player = HUMAN
                turn_count += 1

        # ==================== RENDERIZAÇÃO ====================
        draw_board(screen, board, font_coords)
        draw_hud(screen, font_hud, current_player, turn_count,
                 last_ai_time, last_score, difficulty, game_over, winner)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


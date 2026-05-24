"""
Funções de renderização da interface gráfica do Gomoku (Pygame).
Inclui: menu inicial, tabuleiro, peças e HUD inferior.
"""

import pygame
from board import BOARD_SIZE, HUMAN, AI

# Tamanhos da janela
CELL_SIZE = 60
BORDER_MARGIN = 40
HUD_HEIGHT = 100
WINDOW_WIDTH = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2)
WINDOW_HEIGHT = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2) + HUD_HEIGHT

# Paleta de cores
COLOR_BG = (240, 230, 210)
COLOR_BOARD = (220, 180, 130)
COLOR_GRID = (40, 40, 40)
COLOR_TEXT = (30, 30, 30)
COLOR_HUD_BG = (50, 50, 50)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_BLACK_PIECE = (10, 10, 10)
COLOR_WHITE_PIECE = (245, 245, 245)
COLOR_BUTTON = (80, 130, 200)
COLOR_BUTTON_HOVER = (100, 160, 240)


def get_cell_from_mouse(pos):
    """Converte a posição do mouse (pixels) em coordenadas (linha, coluna)."""
    x, y = pos
    bx = x - BORDER_MARGIN
    by = y - BORDER_MARGIN
    if 0 <= bx < CELL_SIZE * BOARD_SIZE and 0 <= by < CELL_SIZE * BOARD_SIZE:
        return by // CELL_SIZE, bx // CELL_SIZE
    return None


def draw_board(screen, board, font_coords):
    """Desenha o fundo do tabuleiro, as linhas da grade, as coordenadas e as peças."""
    screen.fill(COLOR_BG)

    # Fundo do tabuleiro (área cor de madeira)
    board_rect = pygame.Rect(BORDER_MARGIN, BORDER_MARGIN,
                             CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE)
    pygame.draw.rect(screen, COLOR_BOARD, board_rect)

    # Linhas da grade + rótulos (A-I no topo, 1-9 à esquerda)
    for i in range(BOARD_SIZE + 1):
        line_pos = BORDER_MARGIN + (i * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID,
                         (line_pos, BORDER_MARGIN),
                         (line_pos, BORDER_MARGIN + CELL_SIZE * BOARD_SIZE), 1)
        pygame.draw.line(screen, COLOR_GRID,
                         (BORDER_MARGIN, line_pos),
                         (BORDER_MARGIN + CELL_SIZE * BOARD_SIZE, line_pos), 1)
        if i < BOARD_SIZE:
            center = BORDER_MARGIN + (i * CELL_SIZE) + (CELL_SIZE // 2)
            txt_col = font_coords.render(chr(65 + i), True, COLOR_TEXT)
            screen.blit(txt_col,
                        (center - txt_col.get_width() // 2, BORDER_MARGIN // 4))
            txt_row = font_coords.render(str(i + 1), True, COLOR_TEXT)
            screen.blit(txt_row,
                        (BORDER_MARGIN // 3, center - txt_row.get_height() // 2))

    # Peças (círculos pretos e brancos)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board.grid[row][col]
            if piece == 0:
                continue
            cx = BORDER_MARGIN + (col * CELL_SIZE) + (CELL_SIZE // 2)
            cy = BORDER_MARGIN + (row * CELL_SIZE) + (CELL_SIZE // 2)
            radius = int(CELL_SIZE * 0.4)
            if piece == HUMAN:
                pygame.draw.circle(screen, COLOR_BLACK_PIECE, (cx, cy), radius)
            else:
                pygame.draw.circle(screen, COLOR_WHITE_PIECE, (cx, cy), radius)
                pygame.draw.circle(screen, COLOR_GRID, (cx, cy), radius, 1)


def draw_hud(screen, font, current_player, turn, last_ai_time, last_score,
             difficulty, game_over, winner):
    """Desenha a barra inferior com tempo, score, turno e estado do jogo."""
    hud_rect = pygame.Rect(0, WINDOW_HEIGHT - HUD_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)

    # Linha de cima: vez atual, turno, tempo da IA
    player_str = f"Vez: {'PRETO (Humano)' if current_player == HUMAN else 'BRANCO (IA)'}"
    turn_str = f"Turno: {turn}"
    timer_str = f"Tempo IA: {last_ai_time:.2f}s"

    # Linha de baixo: dificuldade, avaliação heurística e status
    diff_str = f"Nivel: {difficulty}"
    score_str = f"Avaliacao: {last_score}"
    if game_over:
        if winner == 0:
            status_str = "EMPATE!"
        elif winner == HUMAN:
            status_str = "VENCEDOR: PRETO"
        else:
            status_str = "VENCEDOR: BRANCO (IA)"
    else:
        status_str = "Jogo em andamento"

    y_top = WINDOW_HEIGHT - HUD_HEIGHT + 12
    y_bot = WINDOW_HEIGHT - 35

    screen.blit(font.render(player_str, True, COLOR_HUD_TEXT), (20, y_top))
    screen.blit(font.render(turn_str, True, COLOR_HUD_TEXT),
                (WINDOW_WIDTH // 2 - 50, y_top))
    screen.blit(font.render(timer_str, True, COLOR_HUD_TEXT),
                (WINDOW_WIDTH - 180, y_top))

    screen.blit(font.render(diff_str, True, COLOR_HUD_TEXT), (20, y_bot))
    screen.blit(font.render(score_str, True, COLOR_HUD_TEXT),
                (WINDOW_WIDTH // 2 - 80, y_bot))
    screen.blit(font.render(status_str, True, COLOR_HUD_TEXT),
                (WINDOW_WIDTH - 240, y_bot))


def draw_menu(screen, font_title, font_button, mouse_pos):
    """
    Desenha o menu inicial de seleção de dificuldade.
    Retorna a lista de retângulos dos botões [easy, intermediate, hard].
    """
    screen.fill(COLOR_BG)

    # Título e subtítulo
    title = font_title.render("GOMOKU 9x9", True, COLOR_TEXT)
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))
    subtitle = font_button.render("Selecione a dificuldade da IA:",
                                  True, COLOR_TEXT)
    screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 170))

    # Botões (3 níveis)
    button_w, button_h = 320, 60
    button_x = WINDOW_WIDTH // 2 - button_w // 2
    labels = ["INICIANTE", "INTERMEDIARIO", "PROFISSIONAL"]
    rects = []
    for i, label in enumerate(labels):
        y = 240 + i * 80
        rect = pygame.Rect(button_x, y, button_w, button_h)
        color = COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(screen, color, rect, border_radius=8)
        txt = font_button.render(label, True, COLOR_HUD_TEXT)
        screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                          rect.centery - txt.get_height() // 2))
        rects.append(rect)
    return rects

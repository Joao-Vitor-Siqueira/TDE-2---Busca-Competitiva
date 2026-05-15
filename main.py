import pygame
import sys
import time

# Constantes
BOARD_SIZE = 9
CELL_SIZE = 60
BORDER_MARGIN = 40
HUD_HEIGHT = 80
WINDOW_WIDTH = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2)
WINDOW_HEIGHT = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2) + HUD_HEIGHT

# Cores
COLOR_BG = (240, 230, 210)       
COLOR_BOARD = (220, 180, 130)    
COLOR_GRID = (40, 40, 40)
COLOR_TEXT = (30, 30, 30)
COLOR_HUD_BG = (50, 50, 50)
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_BLACK_PIECE = (10, 10, 10)
COLOR_WHITE_PIECE = (245, 245, 245)

# Configurações do Pygame
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Gomoku")
clock = pygame.time.Clock()
font_coords = pygame.font.SysFont("Arial", 18, bold=True)
font_hud = pygame.font.SysFont("Arial", 20)

# Tempo gasto
turn_start_time = time.time()
elapsed_turn_time = 0.0

# Funções
def get_cell_from_mouse(pos):
    x, y = pos
    board_x = x - BORDER_MARGIN
    board_y = y - BORDER_MARGIN
    
    if 0 <= board_x < CELL_SIZE * BOARD_SIZE and 0 <= board_y < CELL_SIZE * BOARD_SIZE:
        col = board_x // CELL_SIZE
        row = board_y // CELL_SIZE
        return row, col
    return None

def create_gomoku_graph(size=9):
    graph = {}

    # Gerar coordenadas
    letters = [chr(ord('A') + i) for i in range(size)]

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for row in range(size):
        for col in range(size):
            node = f"{letters[col]}{row + 1}"
            neighbors = []

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                # Verificar limites do tabuleiro
                if 0 <= new_row < size and 0 <= new_col < size:
                    neighbor = f"{letters[new_col]}{new_row + 1}"

                    # Criação do nó (vizinho, peça)
                    neighbors.append([neighbor, 0])

            graph[node] = neighbors

    return graph

# Variáveis do jogo
board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
board_graph = create_gomoku_graph()
current_player = 1  # 1 = Preto, 2 = Branco
turn_count = 1

# ----------------------------------------- Lógica do jogo -----------------------------------------


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            cell = get_cell_from_mouse(event.pos)
            if cell:
                row, col = cell
                # Posicionar peça
                if board[row][col] == 0:
                    board[row][col] = current_player
                    
                    # Avançar o turno
                    current_player = 2 if current_player == 1 else 1
                    turn_count += 1
                    turn_start_time = time.time() 

    # Atualizar timer
    elapsed_turn_time = time.time() - turn_start_time
    
    
    # ----------------------------------------- RENDERIZAÇÃO -----------------------------------------

    screen.fill(COLOR_BG)
    
    # Tabuleiro
    board_rect = pygame.Rect(BORDER_MARGIN, BORDER_MARGIN, CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE)
    pygame.draw.rect(screen, COLOR_BOARD, board_rect)

    # Coordenadas
    for i in range(BOARD_SIZE + 1):
        line_pos = BORDER_MARGIN + (i * CELL_SIZE)
        
        if i <= BOARD_SIZE:
            # Vertical 
            pygame.draw.line(screen, COLOR_GRID, (line_pos, BORDER_MARGIN), (line_pos, BORDER_MARGIN + CELL_SIZE * BOARD_SIZE), 1)
            # Horizontal 
            pygame.draw.line(screen, COLOR_GRID, (BORDER_MARGIN, line_pos), (BORDER_MARGIN + CELL_SIZE * BOARD_SIZE, line_pos), 1)

        if i < BOARD_SIZE:
            cell_center_offset = BORDER_MARGIN + (i * CELL_SIZE) + (CELL_SIZE // 2)
            
            # Colunas
            col_letter = chr(65 + i)
            txt_col = font_coords.render(col_letter, True, COLOR_TEXT)
            screen.blit(txt_col, (cell_center_offset - txt_col.get_width() // 2, BORDER_MARGIN // 4))

            # Linhas
            row_number = str(i + 1)
            txt_row = font_coords.render(row_number, True, COLOR_TEXT)
            screen.blit(txt_row, (BORDER_MARGIN // 3, cell_center_offset - txt_row.get_height() // 2))

    # Peças
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece != 0:
                center_x = BORDER_MARGIN + (col * CELL_SIZE) + (CELL_SIZE // 2)
                center_y = BORDER_MARGIN + (row * CELL_SIZE) + (CELL_SIZE // 2)
                radius = int(CELL_SIZE * 0.4)
                
                if piece == 1: # Preto
                    pygame.draw.circle(screen, COLOR_BLACK_PIECE, (center_x, center_y), radius)
                    pygame.draw.circle(screen, (60, 60, 60), (center_x, center_y), radius, 1) 
                elif piece == 2: # Branco
                    pygame.draw.circle(screen, COLOR_WHITE_PIECE, (center_x, center_y), radius)
                    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), radius, 1) 

    # HUD
    hud_rect = pygame.Rect(0, WINDOW_HEIGHT - HUD_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)
    
    player_str = f"Player: {'Black' if current_player == 1 else 'White'}"
    turn_str = f"Turn: {turn_count}"
    timer_str = f"Turn Time: {elapsed_turn_time:.1f}s"
    
    txt_player = font_hud.render(player_str, True, COLOR_HUD_TEXT)
    txt_turn = font_hud.render(turn_str, True, COLOR_HUD_TEXT)
    txt_timer = font_hud.render(timer_str, True, COLOR_HUD_TEXT)
    
    hud_y_pos = WINDOW_HEIGHT - (HUD_HEIGHT // 2) - (txt_player.get_height() // 2)
    screen.blit(txt_player, (30, hud_y_pos))
    screen.blit(txt_turn, (WINDOW_WIDTH // 2 - txt_turn.get_width() // 2, hud_y_pos))
    screen.blit(txt_timer, (WINDOW_WIDTH - txt_timer.get_width() - 30, hud_y_pos))

    # Atualizar tela
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
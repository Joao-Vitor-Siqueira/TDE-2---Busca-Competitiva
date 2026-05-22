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
game_over = False
winner = None

# ----------------------------------------- Lógica do jogo -----------------------------------------

#Verifica quem ganhou
def check_victory(board, player):
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal principal
        (1, -1)   # Diagonal secundária
    ]

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            # Verifica se a peça atual pertence ao jogador
            if board[row][col] != player:
                continue

            # para cada direção, conta quantas peças seguidas existem
            for dr, dc in directions:
                count = 1

                for i in range(1, 5): #passa por 4 peças adicionais para verificar 5 seguidas
                    new_row = row + dr * i
                    new_col = col + dc * i

                    # Verifica limites
                    if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE: # se a linha e coluna estão dentro do tabuleiro
                        if board[new_row][new_col] == player: # se a peça da nova posição pertencer ao mesmo jogador, incrementa a contagem
                            count += 1
                        else:
                            break
                    else:
                        break

                # Encontrou 5 seguidas
                if count >= 5:
                    return True

    return False

def check_draw(board):
    for row in board:
        if 0 in row: #se encontrar um espaço vazio, o jogo não é empate
            return False

    return True

def simulate_move(board, row, col, player):
    # Cria uma cópia do tabuleiro
    simulated_board = [linha[:] for linha in board]

    # Faz a jogada simulada
    simulated_board[row][col] = player

    return simulated_board

# ----------------------------------------- IA INICIANTE -----------------------------------------

AI_PLAYER = 2
HUMAN_PLAYER = 1
MAX_DEPTH = 2


# Retorna todas as jogadas possíveis
def get_possible_moves(board):
    moves = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                moves.append((row, col))

    return moves


# Heurística simples
# Conta sequências de 2 e 3 peças
def evaluate_board(board):

    # Vitória
    if check_victory(board, AI_PLAYER):
        return 1000

    if check_victory(board, HUMAN_PLAYER):
        return -1000

    score = 0

    directions = [
        (0, 1),
        (1, 0),
        (1, 1),
        (1, -1)
    ]

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            for dr, dc in directions:

                ai_count = 0
                human_count = 0

                for i in range(3):

                    new_row = row + dr * i
                    new_col = col + dc * i

                    if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:

                        if board[new_row][new_col] == AI_PLAYER:
                            ai_count += 1

                        elif board[new_row][new_col] == HUMAN_PLAYER:
                            human_count += 1

                # Pontuação simples
                if ai_count == 2:
                    score += 10

                elif ai_count == 3:
                    score += 50

                if human_count == 2:
                    score -= 10

                elif human_count == 3:
                    score -= 50

    return score


# Algoritmo Minimax clássico
def minimax(board, depth, maximizing):

    # Casos terminais
    if depth == 0:
        return evaluate_board(board)

    if check_victory(board, AI_PLAYER):
        return 1000

    if check_victory(board, HUMAN_PLAYER):
        return -1000

    if check_draw(board):
        return 0

    possible_moves = get_possible_moves(board)

    # Jogador MAX (IA)
    if maximizing:

        best_score = -float('inf')

        for row, col in possible_moves:

            simulated = simulate_move(board, row, col, AI_PLAYER)

            score = minimax(simulated, depth - 1, False)

            best_score = max(best_score, score)

        return best_score

    # Jogador MIN (Humano)
    else:

        best_score = float('inf')

        for row, col in possible_moves:

            simulated = simulate_move(board, row, col, HUMAN_PLAYER)

            score = minimax(simulated, depth - 1, True)

            best_score = min(best_score, score)

        return best_score


# Escolhe a melhor jogada da IA
def get_best_move(board):

    best_score = -float('inf')
    best_move = None

    possible_moves = get_possible_moves(board)

    for row, col in possible_moves:

        simulated = simulate_move(board, row, col, AI_PLAYER)

        score = minimax(simulated, MAX_DEPTH, False)

        if score > best_score:
            best_score = score
            best_move = (row, col)

    return best_move

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
                if board[row][col] == 0 and not game_over: # se a célula estiver vazia e o jogo não tiver acabado

                    board[row][col] = current_player # coloca a peça do jogador atual na célula selecionada

                    # Verifica vitória
                    if check_victory(board, current_player):
                        game_over = True
                        winner = current_player

                    # Verifica empate
                    elif check_draw(board):
                        game_over = True
                        winner = 0

                    else:
                        # Próximo jogador
                        current_player = 2 if current_player == 1 else 1
                        turn_count += 1
                        turn_start_time = time.time()

                        # Jogada da IA
                        if current_player == AI_PLAYER and not game_over:
                            ai_move = get_best_move(board)
                            
                            if ai_move:
                                
                                ai_row, ai_col = ai_move
                            
                                board[ai_row][ai_col] = AI_PLAYER

                                # Verifica vitória
                                if check_victory(board, AI_PLAYER):
                                    game_over = True
                                    winner = AI_PLAYER

                                # Verifica empate
                                elif check_draw(board):
                                    game_over = True
                                    winner = 0

                                else:
                                    current_player = HUMAN_PLAYER
                                    turn_count += 1
                                    turn_start_time = time.time()
                                    
    # Atualizar timer apenas se o jogo não acabou
    if not game_over:
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
    
    if game_over:
        if winner == 0:
            status_str = "Draw!"
        else:
            status_str = f"Winner: {'Black' if winner == 1 else 'White'}"
    else:
        status_str = "Game Running"

    txt_player = font_hud.render(player_str, True, COLOR_HUD_TEXT)
    txt_turn = font_hud.render(turn_str, True, COLOR_HUD_TEXT)
    txt_timer = font_hud.render(timer_str, True, COLOR_HUD_TEXT)
    txt_status = font_hud.render(status_str, True, COLOR_HUD_TEXT)

    hud_y_pos = WINDOW_HEIGHT - (HUD_HEIGHT // 2) - (txt_player.get_height() // 2)
    screen.blit(txt_player, (30, hud_y_pos))
    screen.blit(txt_turn, (WINDOW_WIDTH // 2 - txt_turn.get_width() // 2, hud_y_pos))
    screen.blit(txt_timer, (WINDOW_WIDTH - txt_timer.get_width() - 30, hud_y_pos))
    screen.blit(txt_status, (30, WINDOW_HEIGHT - 30))

    # Atualizar tela
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

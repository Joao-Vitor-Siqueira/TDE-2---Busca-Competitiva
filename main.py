import pygame
import sys
import time

# Constantes
MAX_TIME = 3.0
DIFFICULTY = "Easy"
BOARD_SIZE = 9
CELL_SIZE = 60
BORDER_MARGIN = 40
HUD_HEIGHT = 80
WINDOW_WIDTH = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2)
WINDOW_HEIGHT = (CELL_SIZE * BOARD_SIZE) + (BORDER_MARGIN * 2) + HUD_HEIGHT
DIRECTIONS = [(1,0),(0,1),(1,1),(1,-1)]

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

# ----------------------------------------- Funções Auxiliares -----------------------------------------
def get_cell_from_mouse(pos):
    x, y = pos
    board_x = x - BORDER_MARGIN
    board_y = y - BORDER_MARGIN
    
    if 0 <= board_x < CELL_SIZE * BOARD_SIZE and 0 <= board_y < CELL_SIZE * BOARD_SIZE:
        col = board_x // CELL_SIZE
        row = board_y // CELL_SIZE
        return row, col
    return None

def get_nearby_moves(pos, radius=1):
    row, col = pos
    moves = []

    for d_row in range(-radius, radius + 1):
        for d_col in range(-radius, radius + 1):

            # Pular posição atual
            if d_row == 0 and d_col == 0:
                continue

            new_row = row + d_row
            new_col = col + d_col

            # Checar se está dentro do tabuleiro
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:

                # Checar se está vazia
                if board[new_row][new_col] == 0:
                    moves.append((new_row, new_col))

    return moves

#Verifica quem ganhou
def check_victory(board, player):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            # Verifica se a peça atual pertence ao jogador
            if board[row][col] != player:
                continue

            # para cada direção, conta quantas peças seguidas existem
            for dr, dc in DIRECTIONS:
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

# ----------------------------------------- Minimax e Heurísticas -----------------------------------------

def evaluate_easy(player=2):
    score = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            if board[row][col] != player:
                continue

            for d_row, d_col in DIRECTIONS:

                prev_r = row - d_row
                prev_c = col - d_col

                # Para não contar a mesma linha mais de uma vez
                if (0 <= prev_r < BOARD_SIZE and
                    0 <= prev_c < BOARD_SIZE and
                    board[prev_r][prev_c] == player):
                    continue

                # Se for o começo de uma sequência, começar a contagem    
                count = 0
                r, c = row, col

                while (0 <= r < BOARD_SIZE and
                       0 <= c < BOARD_SIZE and
                       board[r][c] == player):

                    count += 1
                    r += d_row
                    c += d_col

                if count >= 5:
                    score += 100000
                elif count == 4:
                    score += 10000
                elif count == 3:
                    score += 100
                elif count == 2:
                    score += 10

    return score

def minimax_easy(pos, maxing, depth=3):
    if check_victory(board,2):
        return float('inf')  # IA vence
    if check_victory(board,1):
        return float('-inf')  # Humano vence
    if depth == 0:
        return evaluate_easy()

    child = get_nearby_moves(pos)
    if maxing:
        maxEval = float('-inf')
        for row,col in child:            
            if board[row][col] == 0:
                board[row][col] = 2 #Simular jogada da IA
                eval = minimax_easy( (row, col),False,depth - 1)
                board[row][col] = 0 # Desfazer jogada
                maxEval = max(eval, maxEval)
                
        return maxEval
    
    else:
        minEval = float('inf')
        for row,col in child:            
            if board[row][col] == 0:
                board[row][col] = 1 # Simular jogada do humano
                eval = minimax_easy((row, col),True,depth - 1)
                board[row][col] = 0 # Desfazer jogada
                minEval = min(eval, minEval)
                
        return minEval
    
def evaluate_intermediate(player):
    #implementar heurísticas intermediárias
    return  
    
def minimax_intermediate(pos, maxing, alpha, beta , depth=5):
    if check_victory(board,2):
        return float('inf')  # IA vence
    if check_victory(board,1):
        return float('-inf')  # Humano vence
    if depth == 0:
        player = 2 if maxing else 1
        return evaluate_intermediate(player)

    child = get_nearby_moves(pos)
    
    if maxing:
        maxEval = float('-inf')
        for row,col in child:            
            if board[row][col] == 0:
                board[row][col] = 2 #Simular jogada da IA
                eval = minimax_easy( (row, col),False,depth - 1)
                board[row][col] = 0 # Desfazer jogada
                
                maxEval = max(eval, maxEval)
                alpha = max(eval,alpha)
                if(beta <= alpha):
                    break
                
        return maxEval
    
    else:
        minEval = float('inf')
        for row,col in child:            
            if board[row][col] == 0:
                board[row][col] = 1 # Simular jogada do humano
                eval = minimax_easy((row, col),True,depth - 1)
                board[row][col] = 0 # Desfazer jogada
                
                minEval = min(eval, minEval)
                beta = min(eval,beta)
                if(beta <= alpha):
                    break
                 
        return minEval

def ai_move():
    best_move = (-1,-1)
    score = -1
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                pos = (row,col)                
                
                move_score = minimax_easy(pos,False) if DIFFICULTY == "Easy" else minimax_intermediate() if DIFFICULTY == "Intermediate" else "minimax_hard()"
                
                if(move_score > score):
                    board[row][col] = 2
                    best_move = (row,col)
                    board[row][col] = 0
                    score = move_score
                    
    nextRow, nextCol = best_move
    board[nextRow][nextCol] = 2
    return score
        
    


# ----------------------------------------- Lógica do jogo -----------------------------------------

# Variáveis do jogo
board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = 1  # 1 = Preto (Humano), 2 = Branco (IA)
turn_count = 1
game_over = False
winner = None

# Main loop
running = True
print(f"\nDificuldade selecionada: {DIFFICULTY}")
print("------------------------------------------------")


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        #Turno do jogador humano    
        elif current_player == 1 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            cell = get_cell_from_mouse(event.pos)
            if cell:
                row, col = cell
                # Posicionar peça
                if board[row][col] == 0 and not game_over: # se a célula estiver vazia e o jogo não tiver acabado

                    board[row][col] = current_player # coloca a peça do jogador atual na célula selecionada

                    if check_victory(board, current_player):
                        game_over = True
                        winner = current_player

                    elif check_draw(board):
                        game_over = True
                        winner = 0

                    else:
                        # Próximo jogador
                        current_player = 2 
                        turn_count += 1
                        turn_start_time = time.time()
        
        #Turno da IA
        elif current_player == 2:
            score = ai_move()
            if check_victory(board, current_player):
                game_over = True
                winner = current_player

            elif check_draw(board):
                game_over = True
                winner = 0
            
            current_player = 1 
            turn_count += 1
            print(f"Tempo da jogada: {elapsed_turn_time:.2f}s")
            print(f"Pontuação: {score}")
            print("------------------------------------------------")
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

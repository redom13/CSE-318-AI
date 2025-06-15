import pygame
import threading
import time
import engine

# Constants
ROWS, COLS = 9, 6
CELL_SIZE = 60
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 40
RED = (255, 0, 0)
BLUE = (0, 100, 255)
BG_COLOR = (30, 30, 30)
LINE_COLOR = (200, 200, 200)
FONT_COLOR = (255, 255, 255)
AI_HEURISTIC = 0 # 0 for Random

# Button styling
BUTTON_BG_COLOR = (50, 100, 150)  # Default blue button background
BUTTON_HOVER_COLOR = (70, 120, 170)  # Lighter blue when hovering
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 10  # Radius for rounded corners

# Game State
board = [[None for _ in range(COLS)] for _ in range(ROWS)]
waiting_for_ai = False
first_move = True
game_over = False
mode_selected = False
aiPlayer = False
winner_msg = ''
winner_font_color = (255,255,255)
total_moves = 0

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chain Reaction - Human vs AI")
font = pygame.font.SysFont(None, 24)
selecter_font = pygame.font.SysFont(None, 32)
winner_font = pygame.font.SysFont(None, 40)

# Drawing Utility
def draw_orbs(cell, cell_rect):
    count, color = cell
    orb_color = RED if color == 'R' else BLUE
    cx, cy = cell_rect.centerx, cell_rect.centery
    r = 10
    offset = 16

    positions = []
    if count == 1:
        positions = [(cx, cy)]
    elif count == 2:
        positions = [(cx - offset, cy), (cx + offset, cy)]
    elif count == 3:
        positions = [
            (cx, cy - offset),
            (cx - offset, cy + offset // 2),
            (cx + offset, cy + offset // 2)
        ]
    elif count >= 4:
        positions = [
            (cx - offset, cy - offset),
            (cx + offset, cy - offset),
            (cx - offset, cy + offset),
            (cx + offset, cy + offset)
        ]
    for pos in positions:
        pygame.draw.circle(screen, orb_color, pos, r)

def draw_button(text, rect, is_hovered=False):
    color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_BG_COLOR
    
    # Draw rounded rectangle (using multiple draw calls since pygame doesn't have built-in rounded rect)
    pygame.draw.rect(screen, color, rect, border_radius=BUTTON_RADIUS)
    
    # Render and center the text
    text_surface = selecter_font.render(text, True, FONT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_board():
    global mode_selected, game_over, winner_msg, waiting_for_ai,total_moves,aiPlayer,winner_font_color
    screen.fill(BG_COLOR)
    if not mode_selected:
        # Create button rectangles
        button1_rect = pygame.Rect(
            WIDTH//2 - BUTTON_WIDTH//2,
            HEIGHT//2 - BUTTON_HEIGHT - 20,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        button2_rect = pygame.Rect(
            WIDTH//2 - BUTTON_WIDTH//2,
            HEIGHT//2 + 20,
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )
        
        # Check if mouse is hovering over buttons
        mouse_pos = pygame.mouse.get_pos()
        button1_hover = button1_rect.collidepoint(mouse_pos)
        button2_hover = button2_rect.collidepoint(mouse_pos)
        
        # Draw the buttons
        draw_button("Human vs AI", button1_rect, button1_hover)
        draw_button("AI vs AI", button2_rect, button2_hover)
    elif game_over and winner_msg:
        label = winner_font.render(winner_msg, True, winner_font_color)
        label_moves = winner_font.render(f"Total Moves: {total_moves}", True, winner_font_color)
        # Center the text
        text_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # Position at bottom center
        text_rect_moves = label_moves.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        # screen.fill(BG_COLOR)
        screen.blit(label, text_rect)
        screen.blit(label_moves, text_rect_moves)
        # print("Total Moves: ", total_moves)
    else:
        # screen.fill(BG_COLOR)
        for i in range(ROWS):
            for j in range(COLS):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, LINE_COLOR, rect, 1)
                cell = board[i][j]
                if cell:
                    draw_orbs(cell, rect)
        
        label_moves = font.render(f"Total Moves: {total_moves}", True, FONT_COLOR)
        screen.blit(label_moves, (200, HEIGHT - 30))

        if waiting_for_ai:
            if not aiPlayer:
                label = font.render("AI is thinking...", True, FONT_COLOR)
                screen.blit(label, (10, HEIGHT - 30))


    pygame.display.flip()

def reset_game_state():
    global board, waiting_for_ai, first_move, game_over, winner_msg,total_moves
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    waiting_for_ai = False
    first_move = True
    game_over = False
    winner_msg = ''
    total_moves = 0
    engine.moves = 0
    # write_gamestate_file()

# Writing to the txt file
def write_gamestate_file():
    with open("gamestate.txt", "w") as f:
        f.write("Human Move:\n")
        for row in board:
            line = []
            for cell in row:
                if cell:
                    line.append(f"{cell[0]}{cell[1]}")
                else:
                    line.append("0")
            f.write(" ".join(line) + "\n")

# Waiting for AI move (Polling)
def wait_for_ai_move():
    while True:
        try:
            with open("gamestate.txt", "r") as f:
                header = f.readline().strip()
            if header == "AI Move:":
                return
        except FileNotFoundError:
            pass
        time.sleep(0.5) # Check every 0.5 sec

# Reading AI move from txt file
def read_ai_move():
    global board
    with open("gamestate.txt", "r") as f:
        f.readline()  # skip header
        new_board = []
        for _ in range(ROWS):
            row = []
            for cell in f.readline().strip().split():
                if cell == "0":
                    row.append(None)
                else:
                    row.append((int(cell[0]), cell[1]))
            new_board.append(row)
        board = new_board

# Utility for incorporating waiting 
def wait_for_ai_response():
    global waiting_for_ai,first_move,total_moves
    wait_for_ai_move()
    read_ai_move()
    if not game_over:
        total_moves += 1
    
    if aiPlayer:
        pygame.time.wait(1000)

    waiting_for_ai = False

    if first_move:
        first_move = False

# Utility to calculate critical mass
def calculate_critical_mass(row,col):
    if row > 0 and row < ROWS - 1 and col > 0 and col < COLS - 1:
        return 4
    elif row == 0 or row == ROWS - 1:
        if col == 0 or col == COLS - 1:
            return 2
        else:
            return 3
    elif col == 0 or col == COLS - 1:
        return 3

def explode(row, col):
    # Start with the initial cell to check
    cells_to_check = [(row, col)]
    
    while cells_to_check:
        r, c = cells_to_check.pop(0)  # Get the next cell to process
        cell = board[r][c]
        
        if cell is None:
            continue
            
        count, color = cell
        critical_mass = calculate_critical_mass(r, c)
        
        if count >= critical_mass:
            # This cell explodes
            board[r][c] = None
            
            # Add orbs to neighbors and queue them for checking
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = r + dr, c + dc
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    if board[new_row][new_col] is None:
                        board[new_row][new_col] = (1, color)
                    else:
                        current_count, _ = board[new_row][new_col]
                        board[new_row][new_col] = (current_count + 1, color)
                    
                    # Queue this cell for potential explosion
                    cells_to_check.append((new_row, new_col))
            
            detect_winner()  
            if game_over:
                return

# Utility for detecting winner
def detect_winner():
    # print("First move is: ",first_move)
    global game_over,winner_msg,first_move,board,winner_font_color
    if first_move:
        return
    else:
        winner_msg = ''
        color_count = {'R':0,'B':0}
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] == None:
                    continue
                count,color = board[i][j]
                color_count[color] += count
        # print(color_count)
        if color_count['R'] == 0 and color_count['B'] > 0:
            winner_msg = 'Blue has won the game'
            winner_font_color = (0,100,255)
            game_over = True
        elif color_count['B'] == 0 and color_count['R'] > 0:
            winner_msg = 'Red has won the game'
            winner_font_color = (255,0,0)
            game_over = True
        else:
            return
        
def handle_player_ai_move():
    global waiting_for_ai,board, total_moves, aiPlayer
    if waiting_for_ai:
        return
    # label = font.render("Red is thinking...", True, FONT_COLOR)
    # screen.blit(label, (10, HEIGHT - 30))
    # pygame.display.flip()
    # pygame.time.wait(50) 
    new_board = engine.ai_move(board,isBlue=False, heuristic=AI_HEURISTIC)
    if new_board is not None:
        board = new_board
        write_gamestate_file()
        draw_board() 
        if not game_over:
            total_moves += 1

        waiting_for_ai = True

        if aiPlayer:
            pygame.time.wait(1000) 

        threading.Thread(target=wait_for_ai_response, daemon=True).start()

# Utility for handling mode selection
def handle_mode_selection_click(x, y):
    global mode_selected, aiPlayer
    
    button1_rect = pygame.Rect(
        WIDTH//2 - BUTTON_WIDTH//2,
        HEIGHT//2 - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    button2_rect = pygame.Rect(
        WIDTH//2 - BUTTON_WIDTH//2,
        HEIGHT//2 + 20,
        BUTTON_WIDTH, 
        BUTTON_HEIGHT
    )

    if button1_rect.collidepoint(x, y):
        mode_selected = True
        aiPlayer = False
        pygame.display.set_caption("Chain Reaction - Human vs AI")
        reset_game_state()
    elif button2_rect.collidepoint(x, y):
        mode_selected = True
        aiPlayer = True
        pygame.display.set_caption("Chain Reaction - AI vs AI")
        reset_game_state()

# Utitlity for handling user clicks
def handle_click(x, y):
    global waiting_for_ai, first_move,total_moves, board, aiPlayer, game_over
    row, col = y // CELL_SIZE, x // CELL_SIZE

    if waiting_for_ai or row >= ROWS or col >= COLS or row < 0 or col < 0:
        return
    
    # if first_move:
    #     first_move = False

    cell = board[row][col]
    if cell is None:
        board[row][col] = (1, 'R')
    elif cell[1] == 'R':
        board[row][col] = (cell[0] + 1, 'R')
        explode(row,col)
    else:
        print("Invalid move.")
        return

    write_gamestate_file()
    waiting_for_ai = True
    draw_board()
    total_moves += 1
    threading.Thread(target=wait_for_ai_response, daemon=True).start()


def main():
    global board
    draw_board()
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # board = [[None for _ in range(COLS)] for _ in range(ROWS)]
                # write_gamestate_file()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if not mode_selected:
                    handle_mode_selection_click(*event.pos)
                elif not aiPlayer and not waiting_for_ai:
                    handle_click(*event.pos)
        
        if mode_selected and aiPlayer and not waiting_for_ai and not game_over:
            handle_player_ai_move()
        if game_over == False:
            detect_winner()

        draw_board()

        clock.tick(30) 
    

    pygame.quit()

if __name__ == "__main__":
    main()

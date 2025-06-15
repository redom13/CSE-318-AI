import pygame
import os

# Constants
ROWS, COLS = 9, 6
CELL_SIZE = 60
WIDTH, HEIGHT = COLS * CELL_SIZE + 200, ROWS * CELL_SIZE + 200
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BG_COLOR = (30, 30, 30)
LINE_COLOR = (200, 200, 200)
FONT_COLOR = (255, 255, 255)

# Board Representation (2D array of tuples): (count, color) or None
board = [[None for _ in range(COLS)] for _ in range(ROWS)]

# Init Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chain Reaction - Human vs AI")
font = pygame.font.SysFont(None, 24)

# def draw_board():
#     screen.fill(BG_COLOR)
#     for i in range(ROWS):
#         for j in range(COLS):
#             rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
#             pygame.draw.rect(screen, LINE_COLOR, rect, 1)
#             cell = board[i][j]
#             if cell:
#                 count, color = cell
#                 orb_color = RED if color == 'R' else BLUE
#                 for k in range(count):
#                     offset_x = 10 + (k * 10)
#                     pygame.draw.circle(screen, orb_color,
#                                        (j * CELL_SIZE + offset_x + 10, i * CELL_SIZE + CELL_SIZE // 2),
#                                        8)
#     pygame.display.flip()

def draw_orbs(cell, cell_rect):
    count, color = cell
    orb_color = RED if color == 'R' else BLUE
    cx, cy = cell_rect.centerx, cell_rect.centery
    r = 10  # orb radius
    offset = 16  # distance from center for multi-orb

    positions = []
    if count == 1:
        positions = [(cx, cy)]
    elif count == 2:
        positions = [(cx - offset, cy), (cx + offset, cy)]
    elif count == 3:
        positions = [
            (cx, cy - offset),
            (cx - offset, cy + offset//2),
            (cx + offset, cy + offset//2)
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

def draw_board():
    screen.fill(BG_COLOR)
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)
            cell = board[i][j]
            if cell:
                draw_orbs(cell, rect)
    pygame.display.flip()

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
    cell = board[row][col]
    if cell is None:
        return
    count, color = cell
    critical_mass = calculate_critical_mass(row, col)
    
    if count >= critical_mass:
        board[row][col] = None  # Remove the orb
        # Spread to adjacent cells
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if abs(dr) + abs(dc) == 1:  # Only orthogonal neighbors
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                        if board[new_row][new_col] is None:
                            board[new_row][new_col] = (1, color)  # Add one orb of the same color
                        else:
                            current_count, current_color = board[new_row][new_col]
                            if current_color == color:
                                board[new_row][new_col] = (current_count + 1, current_color)
                                explode(new_row, new_col)  # Check if it can explode again
                            else:
                                board[new_row][new_col] = (current_count + 1, color) # Add one orb of new color and convert others to this color
                                explode(new_row, new_col)  # Check if it can explode again
    return

def handle_click(x, y):
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    if board[row][col] is None:
        board[row][col] = (1, 'R')
    elif board[row][col][1] == 'R':
        board[row][col] = (board[row][col][0] + 1, 'R')
        explode(row, col)
    else:
        print("Invalid move (opponent cell)")
        return
    write_gamestate_file()

def main():
    running = True
    draw_board()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(*event.pos)
                draw_board()

    pygame.quit()

if __name__ == "__main__":
    main()

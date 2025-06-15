import time
import random

ROWS, COLS = 9, 6
moves = 0
AI_TIME_LIMIT = 7 # seconds

def parse_board_from_file(filepath):
    global ROWS, COLS
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None, None # File doesn't exist

    if not lines: # Check if lines is empty
        return None, None # File is empty

    header = lines[0].strip()
    board = []
    for line in lines[1:]:
        row = []
        for cell in line.strip().split():
            if cell == "0":
                row.append(None)
            else:
                row.append((int(cell[0]), cell[1]))  # (count, 'R' or 'B')
        board.append(row)
    return header, board

def write_ai_move(filepath, board):
    with open(filepath, "w") as f:
        f.write("AI Move:\n")
        for row in board:
            line = []
            for cell in row:
                if cell:
                    line.append(f"{cell[0]}{cell[1]}")
                else:
                    line.append("0")
            f.write(" ".join(line) + "\n")

def wait_for_human_move(filepath):
    while True:
        header, board = parse_board_from_file(filepath)
        red_count , _ = ball_count(board)
        if header == "Human Move:" and red_count > 0:
            print("Detected Human Move. Processing...")
            return board
        time.sleep(0.5)

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

def explode(board, row, col):
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

            if moves > 0 and game_over(board)[0]:
                return

def ball_count(board):
    red_count, blue_count = 0, 0
    for row in board:
        for cell in row:
            if cell is not None:
                count, color = cell
                if color == 'R':
                    red_count += count
                elif color == 'B':
                    blue_count += count
    return red_count, blue_count

def game_over(board):
    if moves: # Only if there has been at least one move
        red_count, blue_count = ball_count(board)
        if blue_count == 0 and red_count > 0:
            return True, 'R'
        if red_count == 0 and blue_count > 0:
            return True, 'B'
    
    return False, None

def evaluate(board, heuristic=1):
    # Difference in orb counts ---> H1
    red_count, blue_count = ball_count(board)
    if heuristic == 1:
        return blue_count - red_count
    # Corner control ---> H2
    elif heuristic == 2:
        score = 0
        for i in range(ROWS):
            for j in range(COLS):
                if (i == 0 or i == ROWS - 1) and (j == 0 or j == COLS - 1):
                    if board[i][j]:
                        count, color = board[i][j]
                        if color == 'B':
                            score += count
                        elif color == 'R':
                            score -= count
        return score
    # Threat/Opportunity (Almost Critical Cells) ---> H3
    elif heuristic == 3:
        score = 0
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j]:
                    count, color = board[i][j]
                    critical_mass = calculate_critical_mass(i, j)
                    if count == critical_mass - 1:
                        if color == 'B':
                            score += 1
                        elif color == 'R':
                            score -= 1
        return score
    # Mobility (Number of Possible Moves) ---> H4
    elif heuristic == 4:
        blue_moves, red_moves = 0, 0
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] is None or board[i][j][1] == 'B':
                    blue_moves += 1
                if board[i][j] is None or board[i][j][1] == 'R':
                    red_moves += 1
        return blue_moves - red_moves
    # Combined Heuristic ---> H5
    elif heuristic == 5:
        weights = [0.5, 1, 1.5, 1.2]
        h1 = blue_count - red_count
        h2 = 0
        for i in range(ROWS):
            for j in range(COLS):
                if (i == 0 or i == ROWS - 1) and (j == 0 or j == COLS - 1):
                    if board[i][j]:
                        count, color = board[i][j]
                        if color == 'B':
                            h2 += count
                        elif color == 'R':
                            h2 -= count
        h3 = 0
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j]:
                    count, color = board[i][j]
                    critical_mass = calculate_critical_mass(i, j)
                    if count == critical_mass - 1:
                        if color == 'B':
                            h3 += 1
                        elif color == 'R':
                            h3 -= 1
        h4 = 0
        blue_moves, red_moves = 0, 0
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] is None or board[i][j][1] == 'B':
                    blue_moves += 1
                if board[i][j] is None or board[i][j][1] == 'R':
                    red_moves += 1
        h4 = blue_moves - red_moves

        weighted_score = (weights[0] * h1 + 
                        weights[1] * h2 + 
                        weights[2] * h3 + 
                        weights[3] * h4)
        return weighted_score

def get_valid_random_move(board, color):
    valid_moves = []
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] is None or board[i][j][1] == color:
                valid_moves.append((i, j))
    if valid_moves:
        return random.choice(valid_moves)
    return None

def minimax(board, depth, alpha, beta, maximizing_player,heuristic=1,start_time=None,time_limit=None):
    if start_time and time_limit and (time.time() - start_time > time_limit):
        return (float('-inf') if maximizing_player else float('inf')), None # Timeout 
    
    if depth == 0:
        return evaluate(board,heuristic), None
    over, winner = game_over(board)
    if over:
        if winner == 'B':
            return float('inf'), None
        elif winner == 'R':
            return float('-inf'), None
        else:
            return 0, None
        
    if maximizing_player: 
        max_eval = float('-inf')
        best_move_found = None
        
        possible_moves = []
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] is None or board[i][j][1] == 'B':
                    possible_moves.append((i, j))
        
        random.shuffle(possible_moves)

        for i, j in possible_moves:
            if start_time and time_limit and (time.time() - start_time > time_limit):
                return max_eval, best_move_found # Return current best if timeout

            current_cell_val = board[i][j]
            count, _ = current_cell_val if current_cell_val else (0, 'B')
            
            new_board = [row[:] for row in board] 
            new_board[i][j] = (count + 1, 'B')
            explode(new_board, i, j) 
            
            eval_val, _ = minimax(new_board, depth - 1, alpha, beta, False, heuristic, start_time, time_limit)
            
            if eval_val > max_eval:
                max_eval = eval_val
                best_move_found = (i, j)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break 
        return max_eval, best_move_found
    else: 
        min_eval = float('inf')
        best_move_found = None 
        
        possible_moves = []
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] is None or board[i][j][1] == 'R':
                    possible_moves.append((i, j))

        random.shuffle(possible_moves)

        for i, j in possible_moves:
            if start_time and time_limit and (time.time() - start_time > time_limit):
                return min_eval, best_move_found

            current_cell_val = board[i][j]
            count, _ = current_cell_val if current_cell_val else (0, 'R')

            new_board = [row[:] for row in board]
            new_board[i][j] = (count + 1, 'R')
            explode(new_board, i, j)
            
            eval_val, _ = minimax(new_board, depth - 1, alpha, beta, True, heuristic, start_time, time_limit)

            if eval_val < min_eval:
                min_eval = eval_val
                best_move_found = (i, j)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move_found
    
def make_random_ai_move(board, color):
    global moves 
    
    print(f"AI ({color}) making a random move.")
    chosen_move = get_valid_random_move(board, color) 

    if chosen_move is None:
        print(f"No valid random moves available for {color}. Game might be stuck or over.")
        return board

    i, j = chosen_move
    
    current_cell_val = board[i][j]
    count, _ = current_cell_val if current_cell_val else (0, color)
    board[i][j] = (count + 1, color)
    
    explode(board, i, j)
    moves += 1

    return board
    
def ai_move(board,isBlue=True, heuristic=1):
    global moves

    if heuristic == 0:
        return make_random_ai_move(board, 'B' if isBlue else 'R')
    start_time = time.time()

    color = 'B' if isBlue else 'R'
    depth = 3

    eval_score, best_move = minimax(board, depth, float('-inf'), float('inf'), isBlue ,heuristic,start_time, AI_TIME_LIMIT)
    
    time_taken = time.time() - start_time
    print(f"AI ({color}) evaluated move with score: {eval_score} in {time_taken:.2f} seconds.")

    if best_move is None:
        print(f"No valid move found for AI. Choosing a random move.")
        best_move = get_valid_random_move(board, color)
        if best_move is None:
            print(f"No valid random moves available. Game might be stuck or over.")
            return board # No move can be made

    if best_move:
        i, j = best_move
        if isBlue:
            count, _ = board[i][j] if board[i][j] else (0, 'B')
            board[i][j] = (count + 1, 'B')
        else:
            count, _ = board[i][j] if board[i][j] else (0, 'R')
            board[i][j] = (count + 1, 'R')
        explode(board, i, j)
        moves += 1
    return board

def main(filepath="gamestate.txt"):
    while True:
        board = wait_for_human_move(filepath)
        new_board = ai_move(board,isBlue=True,heuristic=3)  
        write_ai_move(filepath, new_board)
        print("AI Move written. Waiting for next human move...")

if __name__ == "__main__":
    main()

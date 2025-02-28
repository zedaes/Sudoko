import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.live import Live
from tqdm import tqdm

console = Console()

def load_sudokus(file_name):
    """Loads Sudoku puzzles from a CSV file."""
    df = pd.read_csv(file_name)
    return df.to_dict(orient='list')

def render_board(board, original_board, color_map):
    """Creates a rich.Table object for displaying the Sudoku board with colors."""
    table = Table(show_header=False, show_lines=True)
    for _ in range(9):
        table.add_column(justify="center")

    for r in range(9):
        row = []
        for c in range(9):
            num = board[r][c]
            color = color_map[(r, c)]
            if num == 0:
                row.append(".")
            else:
                row.append(f"[{color}]{num}[/]")
        table.add_row(*row)
    return table

def is_valid(board, row, col, num):
    """Checks if a number can be placed in the given cell."""
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    box_row_start, box_col_start = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row_start + i][box_col_start + j] == num:
                return False
    return True

def solve_sudoku(board, original_board, color_map, progress, live):
    """Backtracking Sudoku solver with real-time visualization."""
    empty = find_empty_location(board)
    if not empty:
        return True  # Solved
    row, col = empty

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            color_map[(row, col)] = "green"
            progress.update(1)  # Update progress bar
            live.update(render_board(board, original_board, color_map))

            if solve_sudoku(board, original_board, color_map, progress, live):
                return True

            # Backtracking: Turn numbers red
            board[row][col] = 0
            color_map[(row, col)] = "red"
            progress.update(-1)  # Reduce progress
            live.update(render_board(board, original_board, color_map))

    return False

def find_empty_location(board):
    """Finds an empty cell in the Sudoku board."""
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def string_to_board(sudoku_string):
    """Converts a Sudoku string into a 2D board."""
    return [[int(num) for num in sudoku_string[i:i+9]] for i in range(0, 81, 9)]

def board_to_string(board):
    """Converts a board back into a string."""
    return "".join(str(num) for row in board for num in row)

def sudoku_solver(sudoku_string):
    """Solves a Sudoku puzzle and returns the solved board as a string."""
    board = string_to_board(sudoku_string)
    original_board = [row[:] for row in board]  # Copy original for color reference
    total_cells = sum(row.count(0) for row in board)

    # Color map for tracking number updates
    color_map = {(r, c): "blue" if original_board[r][c] != 0 else "white" for r in range(9) for c in range(9)}

    with tqdm(total=total_cells, desc="Solving Sudoku", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} cells filled") as progress:
        with Live(render_board(board, original_board, color_map), refresh_per_second=60) as live:
            if solve_sudoku(board, original_board, color_map, progress, live):
                return board_to_string(board)
    return None

# Load Sudoku data
sudoku_data = load_sudokus('sudoku.csv')
num_puzzles = len(sudoku_data['puzzle'])

# Overall progress bar for all Sudokus
with tqdm(total=num_puzzles, desc="Solving all Sudokus", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} puzzles solved") as overall_progress:
    for i in range(num_puzzles):
        puzzle = sudoku_data['puzzle'][i]
        solution = sudoku_data['solution'][i]

        console.print(f"[bold magenta]Solving puzzle {i + 1}/{num_puzzles}[/bold magenta]")

        solved = sudoku_solver(puzzle)

        console.print("[bold green]✅ Solved board:[/bold green]")
        console.print(render_board(string_to_board(solved), string_to_board(puzzle), {(r, c): "blue" for r in range(9) for c in range(9)}))

        if solved == solution:
            console.print("[green]✅ Correct![/green]")
        else:
            console.print("[red]❌ Incorrect solution[/red]")

        overall_progress.update(1)

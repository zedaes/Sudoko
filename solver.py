import pandas as pd
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from tqdm import tqdm

console = Console()

def load_sudokus(file_name):
    df = pd.read_csv(file_name)
    return df.to_dict(orient='list')

def render_board(board, original_board, color_map):
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
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    box_row_start, box_col_start = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row_start + i][box_col_start + j] == num:
                return False
    return True

def solve_sudoku(board, original_board, color_map, progress, live, stats):
    empty = find_empty_location(board)
    if not empty:
        return True  
    row, col = empty

    for num in range(1, 10):
        stats['attempts'] += 1  
        if is_valid(board, row, col, num):
            board[row][col] = num
            color_map[(row, col)] = "green"
            stats['correct_placements'] += 1  
            progress.update(1)
            live.update(render_board(board, original_board, color_map))

            if solve_sudoku(board, original_board, color_map, progress, live, stats):
                return True

            board[row][col] = 0
            color_map[(row, col)] = "red"
            stats['backtracks'] += 1  
            progress.update(-1)
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
    return [[int(num) for num in sudoku_string[i:i+9]] for i in range(0, 81, 9)]

def board_to_string(board):
    return "".join(str(num) for row in board for num in row)

def sudoku_solver(sudoku_string):
    board = string_to_board(sudoku_string)
    original_board = [row[:] for row in board]  
    total_cells = sum(row.count(0) for row in board)

    color_map = {(r, c): "blue" if original_board[r][c] != 0 else "white" for r in range(9) for c in range(9)}

    stats = {"attempts": 0, "correct_placements": 0, "backtracks": 0}
    start_time = time.time()

    with tqdm(total=total_cells, desc="Solving Sudoku", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} cells filled") as progress:
        with Live(render_board(board, original_board, color_map), refresh_per_second=60) as live:
            if solve_sudoku(board, original_board, color_map, progress, live, stats):
                stats["solve_time"] = time.time() - start_time
                return board_to_string(board), stats
    return None, stats

sudoku_data = load_sudokus('sudoku.csv')
num_puzzles = len(sudoku_data['puzzle'])

overall_stats = {"total_attempts": 0, "total_correct": 0, "total_backtracks": 0, "total_time": 0}

with tqdm(total=num_puzzles, desc="Solving all Sudokus", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} puzzles solved") as overall_progress:
    for i in range(num_puzzles):
        puzzle = sudoku_data['puzzle'][i]
        solution = sudoku_data['solution'][i]

        console.print(f"[bold magenta]Solving puzzle {i + 1}/{num_puzzles}[/bold magenta]")

        solved, stats = sudoku_solver(puzzle)

        overall_stats["total_attempts"] += stats["attempts"]
        overall_stats["total_correct"] += stats["correct_placements"]
        overall_stats["total_backtracks"] += stats["backtracks"]
        overall_stats["total_time"] += stats["solve_time"]

        console.print("\n[bold green]✅ Final Solved Board:[/bold green]")
        console.print(render_board(string_to_board(solved), string_to_board(puzzle), {(r, c): "blue" for r in range(9) for c in range(9)}))

        console.print(f"\n[bold cyan]📊 Stats for Puzzle {i + 1}:[/bold cyan]")
        console.print(f" - ⏳ Time Taken: {stats['solve_time']:.2f} sec")
        console.print(f" - 🔢 Attempts: {stats['attempts']}")
        console.print(f" - ✅ Correct Moves: {stats['correct_placements']}")
        console.print(f" - ❌ Backtracks: {stats['backtracks']}")

        if solved == solution:
            console.print("[green]✅ Correct![/green]")
        else:
            console.print("[red]❌ Incorrect solution[/red]")

        overall_progress.update(1)

console.print("\n[bold yellow]🏆 Final Summary of All Sudoku Solves:[/bold yellow]")
summary_table = Table(show_header=True, header_style="bold magenta")
summary_table.add_column("Metric", justify="left")
summary_table.add_column("Value", justify="center")

summary_table.add_row("Total Attempts", str(overall_stats["total_attempts"]))
summary_table.add_row("Total Correct Moves", str(overall_stats["total_correct"]))
summary_table.add_row("Total Backtracks", str(overall_stats["total_backtracks"]))
summary_table.add_row("Total Time (sec)", f"{overall_stats['total_time']:.2f}")

console.print(summary_table)

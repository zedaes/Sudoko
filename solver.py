import csv
import pygame
import sys
from constants import * 

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")

def read_sudoku_csv(filename):
    puzzles = []
    solutions = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            puzzles.append(row[0])
            solutions.append(row[1])
    return puzzles, solutions

def string_to_board(sudoku_string):
    board = []
    for i in range(0, 81, 9):
        row = [int(num) for num in sudoku_string[i:i + 9]]
        board.append(row)
    return board

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row_start + i][box_col_start + j] == num:
                return False
    return True
    

def main():
    while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
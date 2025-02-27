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

def main():
    while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
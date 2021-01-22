import pygame
import time

def backtrack_solve(draw, grid, fast):
    find = find_empty(grid)
    if not find:
        return True
    else:
        i, j = find

    for n in range(1, 10):
        if is_possible(i, j, n, grid):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            grid[i][j] = n
            draw()
            if not fast:
                time.sleep(0.02)

            if backtrack_solve(draw, grid, fast):
                return True

            grid[i][j] = 0
            draw()
            if not fast:
                time.sleep(0.02)

def is_possible(y, x, num, grid):
    # Row
    if num in grid[y]:
        return False

    # Column
    for i in range(len(grid)):
        if grid[i][x] == num:
            return False

    # 3x3 square
    gx = x//3 * 3
    gy = y//3 * 3
    for i in range(3):
        for j in range(3):
            if grid[gy+i][gx+j] == num:
                return False
    return True


def find_empty(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 0:
                return (i, j)

    return None

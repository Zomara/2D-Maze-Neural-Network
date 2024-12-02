import pygame
import random
import time
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 900
GRID_SIZE = 3
MAP_SIZE = 30
TILE_SIZE_W = int(SCREEN_WIDTH / MAP_SIZE / GRID_SIZE)
TILE_SIZE_H = int(SCREEN_HEIGHT / MAP_SIZE / GRID_SIZE)
window = pygame.display.set_mode((SCREEN_WIDTH-(TILE_SIZE_W*2), SCREEN_HEIGHT-(TILE_SIZE_H*2)))

player_x = MAP_SIZE/2 *TILE_SIZE_W
player_y = MAP_SIZE/2 * TILE_SIZE_H

def blank_map():
    map = []
    for i in range(MAP_SIZE):
        row = []
        for j in range(MAP_SIZE):
            if j == 0 or j == MAP_SIZE-1 or i == 0 or i == MAP_SIZE-1:
                row.append(-1)
            else:    
                row.append(0)
        map.append(row)
    return map

def limit(input):
    output = input%(MAP_SIZE-1)

    if output == 0:
        output = 1

    return output

def generate_map():
    map = blank_map()
    for j in range(1):
        row = random.randint(1, MAP_SIZE-2)
        column = random.randint(1, MAP_SIZE-2)
        while map[row][column] > 0:
            row = random.randint(1, MAP_SIZE-2)
            column = random.randint(1, MAP_SIZE-2)
        color_pos = random.randint(0, 2)
        base_color = [random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)]
        base_color[color_pos] = 50
        length = 0
        end_column = -1
        end_row = -1
        stop = False
        while not stop:
            direction = random.choice([-1, 1])
            displacement = random.randint(5, 12)
            for i in range(1, displacement+5):
                if map[limit(row+i*direction)][column] > 0:
                    end_column = column
                    end_row = limit(row+i*direction)
                    displacement = i-5
                    if displacement < 1:
                        displacement = 1
                    stop = True
                    break
            for i in range(displacement):
                row = limit(row+direction)
                length += 1
                map[row][column] = length
                draw_super_map(map, column, row, end_column, end_row, base_color, color_pos)
            
            if stop:
                break
            
            direction = random.choice([-1, 1])
            displacement = random.randint(5, 12)
            for i in range(1, displacement+5):
                if map[row][limit(column+i*direction)] > 0:
                    end_column = limit(column+i*direction)
                    end_row = row
                    displacement = i-5
                    if displacement < 1:
                        displacement = 1
                    stop = True
                    break
            for i in range(displacement):
                column = limit(column+direction)
                length += 1
                map[row][column] = length
                draw_super_map(map, column, row, end_column, end_row, base_color, color_pos)

    draw_super_map(map, column, row, end_column, end_row, base_color, color_pos)

def gradient(value, rgb, color_pos):
    rgb[color_pos] = rgb[color_pos]+1 #+value
    if rgb[color_pos] > 255:
        rgb[color_pos] = 0

    return tuple(rgb)

def grid_color(value, rgb, color_pos):
    if value == 0:
        colour = (200, 200, 200)
    elif value > 0:
        colour = gradient(value, rgb, color_pos)
    elif value == -1:
        colour = (50, 50, 50)
    return colour

def draw_map(map, green_column, green_row, end_column, end_row, base_color, color_pos):
    surface = pygame.Surface((SCREEN_WIDTH/GRID_SIZE, SCREEN_HEIGHT/GRID_SIZE))
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            pygame.draw.rect(surface, grid_color(map[row][column], base_color, color_pos), (column * TILE_SIZE_W, row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))
    pygame.draw.rect(surface, (0, 255, 0), (green_column * TILE_SIZE_W, green_row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))
    pygame.draw.rect(surface, (255, 0, 0), (end_column * TILE_SIZE_W, end_row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))
    return surface

def draw_super_map(map, green_column, green_row, end_column, end_row, base_color, color_pos):
    for j in range(GRID_SIZE):
        for i in range(GRID_SIZE):
            window.blit(draw_map(map, green_column, green_row, end_column, end_row, base_color, color_pos), (j*(SCREEN_WIDTH/GRID_SIZE-TILE_SIZE_W), i*(SCREEN_HEIGHT/GRID_SIZE-TILE_SIZE_H)))
    time.sleep(0.01)                                                    
    pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    generate_map()
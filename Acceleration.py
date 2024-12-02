import pygame
import math
import csv
import os
pygame.init()

#screen size MUST be a square
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
MAP_SIZE = 100
TILE_SIZE = int(SCREEN_WIDTH / MAP_SIZE)
TILE_SPACING = 1
MAX_DEPTH = int(math.sqrt(math.pow(SCREEN_WIDTH, 2)+math.pow(SCREEN_HEIGHT, 2)))
FOV = math.pi
CASTED_RAYS = 12
STEP_ANGLE = FOV/CASTED_RAYS
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player_x = SCREEN_WIDTH-TILE_SIZE*3
player_y = SCREEN_HEIGHT-TILE_SIZE*3
player_angle = math.pi
player_rect = pygame.Rect(player_x-TILE_SIZE/2, player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
player_speed_limit = TILE_SIZE/4
player_velocity_x = 0
player_velocity_y = 0

map = []
tiles=[]
with open(os.path.join('map_csv', 'Drift.csv')) as data:
    data = csv.reader(data, delimiter=',')
    for row in data:
        map.append(list(row))

def load_tiles():
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            if map[row][column] == '2':
                tiles.append(pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, 
                                TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
    return tiles

def draw_map():
    pygame.draw.rect(window, (0, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            pygame.draw.rect(window,
                             (200, 200, 200) if map[row][column] == '-1' else (100, 100, 100), 
                             (column * TILE_SIZE, row * TILE_SIZE, 
                              TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
    player_rect = pygame.Rect(player_x-TILE_SIZE/2, player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(window, (255, 0, 0), player_rect)
    pygame.draw.circle(window, (0, 0, 255), (int(player_x), int(player_y)), TILE_SIZE/2)
    pygame.draw.line(window, (0, 255, 0), (player_x, player_y), 
                         (player_x+math.sin(player_angle)*TILE_SIZE, 
                          player_y+math.cos(player_angle)*TILE_SIZE), 1)

def cast_rays():
    start_angle = player_angle-(FOV/2)
    for ray_num in range(CASTED_RAYS):
        angle = STEP_ANGLE*ray_num + start_angle
        for depth in range(MAX_DEPTH):
            target_x = player_x+math.sin(angle)*depth
            target_y = player_y+math.cos(angle)*depth
            column = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)
            if map[row][column] == "2":
                pygame.draw.rect(window, (0, 255, 0),
                             (column * TILE_SIZE, row * TILE_SIZE, 
                              TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
                pygame.draw.line(window, (255, 255, 0), (player_x, player_y), (target_x, target_y), 1)
                break

def get_hits():
    player_rect = pygame.Rect(player_x-TILE_SIZE/2, player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
    for tile in tiles:
        if player_rect.colliderect(tile):
            return True
    return False

def limit(velocity):
    if velocity > player_speed_limit:
        velocity = player_speed_limit
    elif velocity < -player_speed_limit:
        velocity = -player_speed_limit
    return velocity

def update_player():
    global player_velocity_y, player_velocity_x, player_x, player_y, player_angle

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: 
        player_angle += 0.03
    if keys[pygame.K_d]: 
        player_angle -= 0.03
    if keys[pygame.K_w]:
        player_velocity_x = limit(player_velocity_x + math.sin(player_angle)/7)
        player_velocity_y = limit(player_velocity_y + math.cos(player_angle)/7)

    player_velocity_x = player_velocity_x*0.97
    player_velocity_y = player_velocity_y*0.97

    player_x += player_velocity_x
    if get_hits():
        player_x -= player_velocity_x
        player_velocity_x = player_velocity_x/2
    
    player_y += player_velocity_y
    if get_hits():
        player_y -= player_velocity_y 
        player_velocity_y = player_velocity_y/2

tiles = load_tiles()
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_player()
    draw_map()
    cast_rays()
    pygame.display.update()
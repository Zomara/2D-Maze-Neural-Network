import pygame
import math
import csv
import os
import neat
import random
import pickle
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
FONT = pygame.font.SysFont("ComicSansBold", 40)

record_location = None
best = 0
map = []
with open(os.path.join('map_csv', 'Massive.csv')) as data:
    data = csv.reader(data, delimiter=',')
    for row in data:
        map.append(list(row))

def load_tiles():
    tiles=[]
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            if map[row][column] == '2':
                tiles.append(pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, 
                                TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
    return tiles

def draw_map(gravestones, record, bots, fitness, best):
    pygame.draw.rect(window, (0, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            pygame.draw.rect(window,
                             (200, 200, 200) if map[row][column] == '-1' else (100, 100, 100), 
                             (column * TILE_SIZE, row * TILE_SIZE, 
                              TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
    for gravestone in gravestones:
        pygame.draw.rect(window, (255, 0, 0), gravestone)
    if record != None:
        pygame.draw.rect(window, (0, 255, 0), record)
    text = FONT.render("Population: " + str(len(bots)) + " Fitness: " + str(fitness) + " Best: " + str(best), 1, (0, 200, 200))
    window.blit(text, (TILE_SIZE, TILE_SIZE))

class player:
    def __init__(self):
        self.player_x = SCREEN_WIDTH-TILE_SIZE*3
        self.player_y = SCREEN_HEIGHT-TILE_SIZE*3
        self.player_angle = math.pi
        self.player_rect = pygame.Rect(self.player_x-TILE_SIZE/2, self.player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
        self.player_speed = TILE_SIZE/10
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.set_colorkey((0, 0, 0))
        self.surface.set_alpha(128)

    def draw_player(self):
        pygame.draw.circle(self.surface, (self.r, self.g, self.b), (int(self.player_x), int(self.player_y)), TILE_SIZE/2)
        pygame.draw.line(self.surface, (0, 255, 0), (self.player_x, self.player_y), 
                         (self.player_x+math.sin(self.player_angle)*TILE_SIZE, 
                          self.player_y+math.cos(self.player_angle)*TILE_SIZE), 1)
        window.blit(self.surface, (0, 0))

    def cast_rays(self):
        wall_d = []
        start_angle = self.player_angle-(FOV/2)
        for ray_num in range(CASTED_RAYS):
            angle = STEP_ANGLE*ray_num + start_angle
            for depth in range(MAX_DEPTH):
                target_x = self.player_x+math.sin(angle)*depth
                target_y = self.player_y+math.cos(angle)*depth
                column = int(target_x / TILE_SIZE)
                row = int(target_y / TILE_SIZE)
                if map[row][column] == "2":
                    wall_d.append(depth)
                    break
        return wall_d

    def get_hits(self, tiles):
        self.player_rect = pygame.Rect(self.player_x-TILE_SIZE/2, self.player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
        for tile in tiles:
            if self.player_rect.colliderect(tile):
                return tile
        return None

def eval_genomes(genomes, config):
    global record_location, best
    bots = []
    ge = [] #genome list --> index's match constantly changing bot list (cuz bots die)
    nets = []
    gravestones = []

    for irrelevant_variable_lol, g in genomes: 
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        bots.append(player())
        g.fitness = 0
        ge.append(g)

    tiles = load_tiles()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        for x, bot in enumerate(bots):
            output = nets[x].activate(bot.cast_rays())
            desicion = max(output[0], output[1], output[2])
            if desicion == output[0]:
                pass
            elif desicion == output[1]:
                bot.player_angle += 0.02
            elif desicion == output[2]:
                bot.player_angle -= 0.02

            bot.player_x += math.sin(bot.player_angle)*bot.player_speed
            bot.player_y += math.cos(bot.player_angle)*bot.player_speed
            bot.player_rect = pygame.Rect(bot.player_x-TILE_SIZE/2, bot.player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
            collision = bot.get_hits(tiles)
            if collision:
                if len(bots) == 1 and ge[x].fitness >= best:
                    record_location = collision
                    best = ge[x].fitness
                else:
                    gravestones.append(collision)
                bots.pop(x)
                nets.pop(x)
                ge.pop(x)
            else:
                ge[x].fitness += 1
                current_fitness = ge[x].fitness

        if len(bots) == 0:
            running = False

        draw_map(gravestones, record_location, bots, current_fitness, best)
        for x, bot in enumerate(bots):
            bot.draw_player()
        pygame.display.update()

def run(config):
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-281')
    #p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 300)
    with open("best_pathfinder.pickle", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEAT_Config.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    run(config)
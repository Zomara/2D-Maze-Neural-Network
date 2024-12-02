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

best = 0
map = []
with open(os.path.join('map_csv', 'Drift.csv')) as data:
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

def draw_map(gravestones, death_path, bots, fitness, best):
    pygame.draw.rect(window, (100, 100, 100), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            pygame.draw.rect(window,
                             (0, 0, 0) if map[row][column] == '-1' else (80, 80, 80), 
                             (column * TILE_SIZE, row * TILE_SIZE, 
                              TILE_SIZE-TILE_SPACING, TILE_SIZE-TILE_SPACING))
    for gravestone in gravestones:
        pygame.draw.rect(window, (255, 0, 0), gravestone)
    window.blit(death_path, (0, 0))
    text = FONT.render(str(len(bots)) + " | " + str(fitness) + " | " + str(best), 1, (0, 200, 200))
    window.blit(text, ((SCREEN_WIDTH-text.get_width())/2, (SCREEN_HEIGHT-text.get_height())/2))

class player:
    def __init__(self):
        self.player_x = random.choice([(SCREEN_WIDTH-TILE_SIZE*3), (TILE_SIZE*3)])
        self.player_y, self.player_angle = random.choice([(SCREEN_WIDTH-TILE_SIZE*3, math.pi), (TILE_SIZE*3, 0)])
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        self.player_rect = pygame.Rect(self.player_x-TILE_SIZE/2, self.player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
        self.player_speed_limit = TILE_SIZE/4
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.set_colorkey((0, 0, 0))
        self.surface.set_alpha(200)

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
    
    def limit(self, velocity):
        if velocity > self.player_speed_limit:
            velocity = self.player_speed_limit
        elif velocity < -self.player_speed_limit:
            velocity = -self.player_speed_limit
        return velocity


def eval_genomes(genomes, config):
    global best
    bots = []
    ge = [] #genome list --> index's match constantly changing bot list (cuz bots die)
    nets = []
    gravestones = []
    death_path = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    death_path.set_colorkey((0, 0, 0))
    death_path.set_alpha(128)

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
            input = bot.cast_rays() + [bot.player_velocity_x, bot.player_velocity_y, bot.player_angle]
            output = nets[x].activate(input)
            desicion = max(output[0], output[1], output[2])
            if desicion == output[0]:
                pass
            elif desicion == output[1]:
                bot.player_angle += 0.03
            elif desicion == output[2]:
                bot.player_angle -= 0.03

            bot.player_velocity_x = bot.limit(bot.player_velocity_x + math.sin(bot.player_angle)/7)
            bot.player_velocity_y = bot.limit(bot.player_velocity_y + math.cos(bot.player_angle)/7)

            bot.player_velocity_x = bot.player_velocity_x*0.97
            bot.player_velocity_y = bot.player_velocity_y*0.97

            bot.player_x += bot.player_velocity_x
            bot.player_y += bot.player_velocity_y

            bot.player_rect = pygame.Rect(bot.player_x-TILE_SIZE/2, bot.player_y-TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
            collision = bot.get_hits(tiles)
            if collision:
                if len(bots) == 1 and ge[x].fitness >= best:
                    best = ge[x].fitness
                else:
                    gravestones.append(collision)
                    death_path.blit(bots[x].surface, (0, 0))
                bots.pop(x)
                nets.pop(x)
                ge.pop(x)
            else:
                ge[x].fitness += 1
                current_fitness = ge[x].fitness
                if current_fitness > 10000:
                    running = False


        if len(bots) == 0:
            running = False

        draw_map(gravestones, death_path, bots, current_fitness, best)
        for x, bot in enumerate(bots):
            bot.draw_player()
        pygame.display.update()

def run(config):
    p = neat.Checkpointer.restore_checkpoint('neat-driftv2-19')
    #p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1, filename_prefix='neat-driftv2-'))

    winner = p.run(eval_genomes, 300)
    with open("best_drifter.pickle", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "DRIFT_Config.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    run(config)
import time
from choice import Choice
from player import Player
from sprite_objects import *
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
sc_map = pygame.Surface(MINIMAP_RES)

sprites = Sprites()
clock = pygame.time.Clock()
player = Player(sprites)
drawing = Drawing(sc, sc_map, player, clock)
interaction = Interaction(player, sprites, drawing)
choice = Choice(sc, sc_map)

pygame.mouse.set_visible(False)

choice.intro()

init = 0

while True:

    player.movement()
    drawing.background(player.angle)
    walls, wall_shot = ray_casting_walls(player, drawing.textures)
    drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
    drawing.fps(clock)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LCTRL] :
        drawing.mini_map(player)
        
    interaction.clear_world()

    pygame.display.flip()
    clock.tick(FPS)

    if init != 1 :
        player.re_init()
        init = 1

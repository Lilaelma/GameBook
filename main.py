import time
from choice import Choice
from player import Player
from sprite_objects import *
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction


def intro(sc) :
    t1 = 0
    delta_t = 0
    font_text = pygame.font.SysFont("Arial", 20, bold=True)
    with open("intro.txt", "r") as fc :
        for l in fc :

            ligne = ""
            for c in l :
                if c != "\n" :
                    ligne += c

            render = font_text.render(ligne, 0, DARKBROWN)
            text_pos = ((WIDTH - (len(ligne) * 10)) // 2, HEIGHT - 50)
            sc.fill(BLACK)
            t1 = time.time()
            while delta_t <= 3 :
                sc.blit(render, text_pos)
                delta_t = time.time() - t1
                pygame.display.flip()
            print(ligne)
            delta_t = 0

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

import pygame
import time
from player import Player
from ray_casting import ray_casting_walls
from drawing import Drawing
from sprite_objects import *
from settings import *


class Choice :
	def __init__(self, sc, sc_map) :
		self.sc = sc
		self.sc_map = sc_map
		self.font_text = pygame.font.SysFont("Arial", 20, bold=True)
		self.t1 = 0
		self.delta_t = 0
		self.sprites = Sprites()
		self.clock = pygame.time.Clock()
		self.player = Player(self.sprites)
		self.drawing = Drawing(sc, sc_map, self.player, self.clock)

	def intro(self) :
		with open("intro.txt", "r") as fc :
		    for l in fc :

		        ligne = ""
		        for c in l :
		            if c != "\n" :
		                ligne += c

		        render = self.font_text.render(ligne, 0, DARKBROWN)
		        text_pos = ((WIDTH - (len(ligne) * 10)) // 2, HEIGHT - 50)
		        self.t1 = time.time()
		        while self.delta_t <= 1 :
		            
		            self.delta_t = time.time() - self.t1
		            self.player.angle_control()
		            self.drawing.background(self.player.angle)
		            walls, wall_shot = ray_casting_walls(self.player, self.drawing.textures)
		            self.drawing.world(walls + [obj.object_locate(self.player) for obj in self.sprites.list_of_objects])
		            self.drawing.fps(self.clock)
		        
		            keys = pygame.key.get_pressed()
		            if keys[pygame.K_LCTRL] :
		                self.drawing.mini_map(self.player)
		                
		            self.sc.blit(render, text_pos)
		            pygame.display.flip()
		        self.delta_t = 0

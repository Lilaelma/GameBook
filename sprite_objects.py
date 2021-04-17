import pygame
from settings import *
from collections import deque
from ray_casting import mapping
from numba.core import types
from numba.typed import Dict
from numba import int32


class Sprites:
    def __init__(self):
        self.sprite_parameters = {
            "sprite_door_v": {
                "sprite": [pygame.image.load(f"sprites/doors/door_v/{i}.png").convert_alpha() for i in range(16)],
                "viewing_angles": True,
                "shift": 0.1,
                "scale": (2.6, 1.2),
                "side": 100,
                "animation": [],
                "death_animation": [],
                "is_dead": "immortal",
                "dead_shift": 0,
                "animation_dist": 0,
                "animation_speed": 0,
                "blocked": True,
                "flag": "door_h",
                "obj_action": []
            },
            "sprite_door_h": {
                "sprite": [pygame.image.load(f"sprites/doors/door_h/{i}.png").convert_alpha() for i in range(16)],
                "viewing_angles": True,
                "shift": 0.1,
                "scale": (2.6, 1.2),
                "side": 100,
                "animation": [],
                "death_animation": [],
                "is_dead": "immortal",
                "dead_shift": 0,
                "animation_dist": 0,
                "animation_speed": 0,
                "blocked": True,
                "flag": "door_v",
                "obj_action": []
            },
            "npc_soldier0": {
                "sprite": [pygame.image.load(f"sprites/npc/soldier0/base/{i}.png").convert_alpha() for i in range(8)],
                "viewing_angles": True,
                "shift": 0.8,
                "scale": (0.4, 0.6),
                "side": 30,
                "animation": [],
                "death_animation": deque([pygame.image.load(f"sprites/npc/soldier0/death/{i}.png")
                                         .convert_alpha() for i in range(10)]),
                "is_dead": None,
                "dead_shift": 1.7,
                "animation_dist": None,
                "animation_speed": 6,
                "blocked": True,
                "flag": "npc",
                "obj_action": deque([pygame.image.load(f"sprites/npc/soldier0/action/{i}.png")
                                    .convert_alpha() for i in range(4)])
            },
        }

        self.list_of_objects = [
            SpriteObject(self.sprite_parameters["sprite_door_v"], (5, 4.5)),
        ]

    @property
    def sprite_shot(self):
        return min([obj.is_on_fire for obj in self.list_of_objects], default=(float("inf"), 0))

    @property
    def blocked_doors(self):
        blocked_doors = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
        for obj in self.list_of_objects:
            if obj.flag in {"door_h", "door_v"} and obj.blocked:
                i, j = mapping(obj.x, obj.y)
                blocked_doors[(i, j)] = 0
        return blocked_doors


class SpriteObject:
    def __init__(self, parameters, pos):
        self.object = parameters["sprite"].copy()
        self.viewing_angles = parameters["viewing_angles"]
        self.shift = parameters["shift"]
        self.scale = parameters["scale"]
        self.animation = parameters["animation"].copy()
        self.animation_dist = parameters["animation_dist"]
        self.animation_speed = parameters["animation_speed"]
        self.blocked = parameters["blocked"]
        self.flag = parameters["flag"]
        self.obj_action = parameters["obj_action"].copy()
        self.x, self.y = pos[0] * TILE, pos[1] * TILE
        self.side = parameters["side"]
        self.npc_action_trigger = False
        self.door_open_trigger = False
        self.door_prev_pos = self.y if self.flag == "door_h" else self.x
        self.delete = False
        if self.viewing_angles:
            if len(self.object) == 8:
                self.sprite_angles = [frozenset(range(338, 361)) | frozenset(range(0, 23))] + \
                                     [frozenset(range(i, i + 45)) for i in range(23, 338, 45)]
            else:
                self.sprite_angles = [frozenset(range(348, 361)) | frozenset(range(0, 11))] + \
                                     [frozenset(range(i, i + 23)) for i in range(11, 348, 23)]
            self.sprite_positions = {angle: pos for angle, pos in zip(self.sprite_angles, self.object)}

    @property
    def pos(self):
        return self.x - self.side // 2, self.y - self.side // 2

    def object_locate(self, player):

        dx, dy = self.x - player.x, self.y - player.y
        self.distance_to_sprite = math.sqrt(dx ** 2 + dy ** 2)

        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += DOUBLE_PI
        self.theta -= 1.4 * gamma

        delta_rays = int(gamma / DELTA_ANGLE)
        self.current_ray = CENTER_RAY + delta_rays
        if self.flag not in {"door_h", "door_v"}:
            self.distance_to_sprite *= math.cos(HALF_FOV - self.current_ray * DELTA_ANGLE)

        fake_ray = self.current_ray + FAKE_RAYS
        if 0 <= fake_ray <= FAKE_RAYS_RANGE and self.distance_to_sprite > 30:
            self.proj_height = min(int(PROJ_COEFF / self.distance_to_sprite),
                                   DOUBLE_HEIGHT if self.flag not in {"door_h", "door_v"} else HEIGHT)
            sprite_width = int(self.proj_height * self.scale[0])
            sprite_height = int(self.proj_height * self.scale[1])
            half_sprite_width = sprite_width // 2
            half_sprite_height = sprite_height // 2
            shift = half_sprite_height * self.shift

            # logic for doors, npc, decor
            if self.flag in {"door_h", "door_v"}:
                if self.door_open_trigger:
                    self.open_door()
                self.object = self.visible_sprite()
                sprite_object = self.sprite_animation()
            else:
                if self.npc_action_trigger:
                    sprite_object = self.npc_in_action()
                else:
                    self.object = self.visible_sprite()
                    sprite_object = self.sprite_animation()


            # sprite scale and pos
            sprite_pos = (self.current_ray * SCALE - half_sprite_width, HALF_HEIGHT - half_sprite_height + shift)
            sprite = pygame.transform.scale(sprite_object, (sprite_width, sprite_height))
            return (self.distance_to_sprite, sprite, sprite_pos)
        else:
            return (False,)

    def sprite_animation(self):
        if self.animation and self.distance_to_sprite < self.animation_dist:
            sprite_object = self.animation[0]
            if self.animation_count < self.animation_speed:
                self.animation_count += 1
            else:
                self.animation.rotate()
                self.animation_count = 0
            return sprite_object
        return self.object

    def visible_sprite(self):
        if self.viewing_angles:
            if self.theta < 0:
                self.theta += DOUBLE_PI
            self.theta = 360 - int(math.degrees(self.theta))

            for angles in self.sprite_angles:
                if self.theta in angles:
                    return self.sprite_positions[angles]
        return self.object

    def open_door(self):
        if self.flag == "door_h":
            self.y -= 3
            if abs(self.y - self.door_prev_pos) > TILE:
                self.delete = True
        elif self.flag == "door_v":
            self.x -= 3
            if abs(self.x - self.door_prev_pos) > TILE:
                self.delete = True

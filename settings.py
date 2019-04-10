import pygame as pg

pg.mixer.init()

WIDTH = 720
HEIGHT = 480

FPS = 100

BG = (51, 204, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
FONT_NAME = "arial"
YELLOW = (255, 255, 0)

P_SPEED = 5
START_POS_X = 300
START_POS_Y = 200
JUMP = 10

SMALL_HP = 30
BIG_HP = 60
SMALL_SPEED = 2.5
BIG_SPEED = 1.5
SPAWN_POS = (WIDTH / 2, 10)

GRAVITY = 0.4

#Events
PLAYER_DEATH = pg.USEREVENT + 1
CRATE_PICKUP = pg.USEREVENT + 2
SPAWN_ENEMY = pg.USEREVENT + 3
RELOAD = pg.USEREVENT + 4
ENEMY_DEATH = pg.USEREVENT + 5
BULLET_HIT = pg.USEREVENT + 6
SHOT_FIRED = pg.USEREVENT + 7

#Sounds
jump_sound = pg.mixer.Sound(file = "sound\\jump.wav")
shot_sound = pg.mixer.Sound(file = "sound\\hit2.wav")
pickup_sound = pg.mixer.Sound(file= "sound\\pickup.wav")

import pygame as pg
from settings import *
import random

class Block(pg.sprite.Sprite):
    def __init__(self, canvas, img_path, x, y, type):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type

class Player(pg.sprite.Sprite):
    def __init__(self, canvas, img_path, x, y):
        pg.sprite.Sprite.__init__(self)
        #self.image = pg.image.load(img_path)
        self.image = pg.Surface((20,20))
        self.rect = self.image.get_rect()
        pg.draw.rect(self.image, RED, self.rect)
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.vel_x = 0
        self.in_air = True
        self.can_jump = False
        self.speed = P_SPEED
        self.direction = 0
        self.weapon = None
        self.can_shoot = True
        self.facing = 1
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.direction = -1
            self.facing = -1
        if keys[pg.K_RIGHT]:
            self.direction = 1
            self.facing = 1
        self.vel_x = self.direction * self.speed
        if keys[pg.K_UP] and self.can_jump:
            jump_sound.play()
            self.vel_y -= JUMP
            self.in_air = True
            self.can_jump = False
        if keys[pg.K_x] and self.can_shoot:
            shot_sound.stop()
            shot_sound.play()
            event = pg.event.Event(SHOT_FIRED)
            pg.event.post(event);
            self.vel_x -= self.weapon.recoil * self.facing
            self.can_shoot = False
        if self.in_air:
            self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.direction = 0
        if self.rect.top >= HEIGHT:
            event = pg.event.Event(PLAYER_DEATH)
            pg.event.post(event)
    def draw(self, canvas):
        canvas.blit(self.image, self.rect)


class Enemy(pg.sprite.Sprite):
    def __init__(self, canvas, blocks, projectiles):
        pg.sprite.Sprite.__init__(self)
        self.type = random.choice((True, False))
        if self.type:
            self.image = pg.image.load("img\\enemysmall.png")
            self.hp = SMALL_HP
            self.speed = SMALL_SPEED
        elif not self.type:
            self.image = pg.image.load("img\\enemybig.png")
            self.hp = BIG_HP
            self.speed = BIG_SPEED
        self.blocks = blocks
        self.projectiles = projectiles
        self.flaming = False
        self.in_air = True
        self.rect = self.image.get_rect()
        self.rect.center = SPAWN_POS
        self.direction = random.choice((-1, 1))
        self.vel_y = 0
        pg.time.set_timer(SPAWN_ENEMY, random.choice([2000, 3000, 4000]))
    def update(self):
        if self.in_air:
            self.vel_y += GRAVITY
        self.rect.x += self.direction * self.speed
        self.rect.y += self.vel_y
        if self.rect.top > HEIGHT:
            self.rect.center = SPAWN_POS
            if not self.flaming:
                self.flaming = True
                self.speed *= 2

class Crate(pg.sprite.Sprite):
    def __init__(self, crate_spawn):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("img\\crate.png")
        self.rect = self.image.get_rect()
        self.rect.center = crate_spawn

class Weapon(pg.sprite.Sprite):
    def __init__(self, bullet_size, reload_time, bullet_speed, bullets_per_shot, spread, damage, bullet_lifetime, knockback, recoil):
        self.reload_time = reload_time
        self.bullet_speed = bullet_speed
        self.bullets_per_shot = bullets_per_shot
        self.spread = spread
        self.damage = damage
        self.knockback = knockback
        self.recoil = recoil
        self.bullet_size = bullet_size
        self.bullet_lifetime = bullet_lifetime

class Projectile(pg.sprite.Sprite):
    def __init__(self, player, weapon, dir_x, dir_y):
        pg.sprite.Sprite.__init__(self)
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = weapon.bullet_speed
        self.lifetime = weapon.bullet_lifetime
        self.damage = weapon.damage
        self.image = pg.Surface((weapon.bullet_size, weapon.bullet_size), pg.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        pg.draw.ellipse(self.image, YELLOW, self.rect)
        self.rect.center = player.rect.center
        self.knockback = weapon.knockback
    def update(self):
        self.rect.x += self.dir_x * self.speed
        self.rect.y += self.dir_y * self.speed

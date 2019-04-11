import pygame as pg
from settings import *
from objects import *

class Game:
    def __init__(self):
        pg.init()
        self.canvas = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Super Crate Box")
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.bg_image = pg.image.load("img\\citybg2.png")
        self.bg_image = pg.transform.scale(self.bg_image, (720, 480))

    def new(self):
        self.score = 0
        self.crate_spawn_poss = []
        self.blocks = pg.sprite.Group()
        self.weapons = {}
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.beams = pg.sprite.Group()
        self.explosives = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.enemies.add(Enemy(self.canvas, self.blocks, self.projectiles))
        self.crates = pg.sprite.Group()
        self.init_level()
        self.init_weapons()
        self.crates.add(Crate(random.choice(self.crate_spawn_poss)))
        self.player = Player(self.canvas, "img\\player.png", START_POS_X, START_POS_Y)
        self.player.weapon = self.weapons["laser"]
        self.playing = True
        pg.display.flip()
        while self.playing:
            self.run()

    def run(self):
        self.clock.tick(FPS)
        self.events()
        self.update()
        self.fill()
        self.draw()

    def update(self):
        self.player.update()
        self.blocks.update()
        self.enemies.update()
        self.projectiles.update()
        self.beams.update()
        self.explosions.update()
        self.explosives.update()
        self.crates.update()
        self.check_collision()
        #print(self.clock.get_fps())

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            if event.type == SPAWN_ENEMY:
                self.enemies.add(Enemy(self.canvas, self.blocks, self.projectiles))
            if event.type == PLAYER_DEATH:
                self.playing = False
            if event.type == ENEMY_DEATH:
                self.enemies.remove(event.caller[0])
                self.projectiles.remove(event.caller[1])
            if event.type == RELOAD:
                self.player.can_shoot = True
            if event.type == SHOT_FIRED:
                self.on_shot_fired()

    def fill(self):
        #self.canvas.fill(BG)
        self.canvas.blit(self.bg_image, (0,0))

    def draw(self):
        self.blocks.draw(self.canvas)
        self.enemies.draw(self.canvas)
        self.projectiles.draw(self.canvas)
        self.crates.draw(self.canvas)
        self.beams.draw(self.canvas)
        self.explosives.draw(self.canvas)
        self.explosions.draw(self.canvas)
        #self.player_g.draw(self.canvas)
        self.player.draw(self.canvas)
        self.draw_text(str(self.score), 30, BLACK, WIDTH / 2, 30)
        pg.display.flip()

    def check_collision(self):
        for crate in self.crates:
            if pg.sprite.collide_rect(self.player, crate):
                crate.kill()
                self.on_crate_pickup()
        for block in self.blocks:
            if pg.sprite.collide_rect(self.player, block):
                if self.player.rect.top <= block.rect.bottom and\
                block.rect.top < self.player.rect.top and\
                block.type == "platform":
                    self.player.rect.top = block.rect.bottom
                    self.player.vel_y = - self.player.vel_y
                if self.player.rect.bottom >= block.rect.top and\
                block.rect.bottom > self.player.rect.bottom and\
                block.type == "platform":
                    self.player.rect.bottom = block.rect.top
                    self.player.vel_y = 0
                    self.player.can_jump = True
                if self.player.rect.left <= block.rect.right and\
                block.rect.left < self.player.rect.left and\
                block.type == "wall":
                    self.player.rect.left = block.rect.right
                if self.player.rect.right >= block.rect.left and\
                block.rect.right > self.player.rect.right and\
                block.type == "wall":
                    self.player.rect.right = block.rect.left
            for enemy in self.enemies:
                if pg.sprite.collide_rect(enemy, self.player):
                    self.playing = False;
                if pg.sprite.collide_rect(enemy, block):
                    if enemy.rect.top <= block.rect.bottom and\
                    block.rect.top < enemy.rect.top and\
                    block.type == "platform":
                        enemy.rect.top = block.rect.bottom
                        enemy.vel_y = - enemy.vel_y
                    if enemy.rect.bottom >= block.rect.top and\
                    block.rect.bottom > enemy.rect.bottom and\
                    block.type == "platform":
                        enemy.rect.bottom = block.rect.top
                        enemy.vel_y = 0
                    if enemy.rect.left <= block.rect.right and\
                    block.rect.left < enemy.rect.left and\
                    block.type == "wall":
                        enemy.rect.left = block.rect.right
                        enemy.direction = - enemy.direction
                    if enemy.rect.right >= block.rect.left and\
                    block.rect.right > enemy.rect.right and\
                    block.type == "wall":
                        enemy.rect.right = block.rect.left
                        enemy.direction = - enemy.direction
                elif not pg.sprite.collide_rect(enemy, block):
                    enemy.in_air = True
                for explosive in self.explosives:
                    if pg.sprite.collide_rect(explosive, enemy) or pg.sprite.collide_rect(explosive, block):
                        self.explosions.add(Explosion(100, explosive.rect.center[0], explosive.rect.center[1], explosive))
                        explosive.kill()
                for explosion in self.explosions:
                    if pg.sprite.collide_rect(explosion, enemy):
                        enemy.hp -= explosion.damage_per_tick
                        if enemy.hp <= 0:
                            enemy.kill()
                for beam in self.beams:
                    if pg.sprite.collide_rect(beam, enemy):
                        print("hit!")
                        enemy.hp -= beam.damage_per_tick
                        if enemy.hp <= 0:
                            enemy.kill()
                for projectile in self.projectiles:
                    if pg.sprite.collide_rect(block, projectile):
                        projectile.kill()
                    if pg.sprite.collide_rect(enemy, projectile):
                        enemy.hp -= projectile.damage;
                        if (enemy.rect.center[0] - projectile.rect.center[0]) > 0:
                            enemy.rect.x += projectile.knockback
                        else:
                            enemy.rect.x -= projectile.knockback
                        projectile.kill()
                        if enemy.hp <= 0:
                            enemy.kill()

    def on_shot_fired(self):
        if self.player.weapon.type == "proj":
            """
            for bullet in range(self.player.weapon.bullets_per_shot):
                dir_x = self.player.facing
                dir_y = random.uniform(-self.player.weapon.spread, self.player.weapon.spread)
                length = (dir_x ** 2 + dir_y ** 2) ** 0.5
                dir_x /= length
                dir_y /= length
                self.projectiles.add(Projectile(self.player, self.player.weapon, dir_x, dir_y))
            """
            self.init_projectile(self.projectiles)
        elif self.player.weapon.type == "expl":
            self.init_projectile(self.explosives)
        elif self.player.weapon.type == "beam":
            self.beams.add(Laser(self.player))
        pg.time.set_timer(RELOAD, self.player.weapon.reload_time)

    def init_projectile(self, group):
        for bullet in range(self.player.weapon.bullets_per_shot):
            dir_x = self.player.facing
            dir_y = random.uniform(self.player.weapon.spread, 0)
            length = (dir_x ** 2 + dir_y ** 2) ** 0.5
            dir_x /= length
            dir_y /= length
            group.add(Projectile(self.player, self.player.weapon, dir_x, dir_y))

    def on_crate_pickup(self):
        pickup_sound.play()
        self.crates.add(Crate(random.choice(self.crate_spawn_poss)))
        self.player.weapon = self.weapons[random.choice(list(self.weapons.keys()))]
        self.score +=1

    def init_level(self):
        self.blocks.add(Block(self.canvas, "img\\leftwall.png", 0, 20, "wall"))
        self.blocks.add(Block(self.canvas, "img\\leftwall.png", 700, 20, "wall"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 0, 0, "platform"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 400, 0, "platform"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 0, 460, "platform"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 400, 460, "platform"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 200, 130, "platform"))
        self.blocks.add(Block(self.canvas, "img\\bigplatform.png", 200, 350, "platform"))
        self.blocks.add(Block(self.canvas, "img\\smallplatform.png", 20, 240, "platform"))
        self.blocks.add(Block(self.canvas, "img\\smallplatform.png", 540, 240, "platform"))
        self.crate_spawn_poss = [(255, 115), (465, 115), (100, 225), (620, 225), (255, 335), (465, 335), (100, 445), (620, 445)]

    def init_weapons(self):
        #bullet size, reload time(ms), bullet speed, bullets per shot, spread, damage, lifetime(not implemented yet), knockback, recoil
        self.weapons["pistol"] = Weapon(10, 200, 7, 1, 0, 10, 10000, 5, 0, "proj")
        self.weapons["shotgun"] = Weapon(10, 1000, 7, 8, 1, 5, 10000, 5, 10, "proj")
        self.weapons["machinegun"] = Weapon(10, 50, 7, 1, 0.1, 3, 10000, 5, 10, "proj")
        self.weapons["slowgun"] = Weapon(20, 2000, 3, 1, 0, 40, 10000, 50, 30, "proj")
        self.weapons["laser"] = Weapon(20, 1000, 5, 1, 0, 0.3, 1000, 1, 1, "beam")
        self.weapons["explosive"] = Weapon(20, 1000, 5, 1, 0, 0.3, 1000, 1, 1, "expl")

    def draw_text(self, text, size, text_color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.canvas.blit(text_surface, text_rect)

    def wait_any_key(self):
            wait = True
            while wait:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        wait = False
                        self.running = False
                    if event.type == pg.KEYDOWN:
                        wait = False;

    def show_game_over(self):
        if not self.running:
            return
        #self.canvas.fill(BG)
        self.draw_text("Game over! Your score is {score}".format(score = self.score), 42, BLACK, WIDTH/2, 100)
        pg.display.flip()
        self.wait_any_key()

    def show_highscore(self):
        if not self.running:
            return
        self.canvas.fill(BG)
        highscores = open("highscores.txt", "r")
        #scores = highscores.readlines()[1:]
        self.draw_text(highscores.read(), 42, BLACK, WIDTH/2, 100)
        pg.display.flip()
        self.wait_any_key()

game = Game()
while game.running:
    game.new()
    #game.show_game_over()
    #game.show_highscore()

pg.quit()

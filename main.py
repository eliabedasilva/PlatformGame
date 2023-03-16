import pygame, sys, random, time
from pygame.locals import *
from engine import *


# class ---------------------------------|

class Enemy(RigidyBory):

    def update(self, colliders_list):
        self.update_gravity(colliders_list)

    def movement(self):
        pass


class ColliderAttack(Entity):

    def update(self, group: pygame.sprite.Group):
        for enemy in group:
            if self.rect.colliderect(enemy.rect):
                enemy.kill()
        self.kill()


class Player(SimplePlayer):

    def attack(self):
        collider_attack = ColliderAttack([0, 0], [self.rect.w, self.rect.h], '', True)
        collider_attack.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
        if not self.flip:
            collider_attack.rect.x += 35
        else:
            collider_attack.rect.x -= 35
        return collider_attack


# init  ---------------------------------|
pygame.init()
size_display = [1280, 720]
display = pygame.display.set_mode(size_display)
pygame.display.set_caption('Platform game')
clock = pygame.time.Clock()
last_time = time.time()
scroll = [0, 0]
click = False
first_time = True
positions_enemy = [[460, 213], [148, 204], [961, 209], [1877, 325], [1399, 995], [1988, 996], [2754, 214], [652, -1239]]
fps = 30

# player ----------------------------------|
player = Player([size_display[0] / 2 - 10, size_display[1] / 2 - 20], [28, 60], '', 1, 12, 2, 22, 2, True)
player.has_animations = True

# images  ---------------------------------| 
enemy_image = load_image('data/enemy.png', 4)
bricks_top_left = load_image('data/tiles/default/tile_0275.png', 1)
bricks_top_center = load_image('data/tiles/default/tile_0276.png', 1)
bricks_top_right = load_image('data/tiles/default/tile_0277.png', 1)
bricks_left = load_image('data/tiles/default/tile_0295.png', 1)
bricks_center = load_image('data/tiles/default/tile_0296.png', 1)
bricks_right = load_image('data/tiles/default/tile_0297.png', 1)
simple_grass = load_image('data/tiles/default/tile_0018.png', 1)
map_image_1 = load_image('data/maps/map_1.png', 1)

# groups  ---------------------------------|
timerGroup = pygame.sprite.Group()
attackGroup = pygame.sprite.Group()
enemyGroup = pygame.sprite.Group()

for position in positions_enemy:
    enemy = Enemy(position, [player.rect.w, player.rect.h], enemy_image, 2, False)
    if random.random() >= 0.5:
        enemy.image = pygame.transform.flip(enemy.image, True, False)
    else:
        enemy.image = pygame.transform.flip(enemy.image, False, False)
    enemyGroup.add(enemy)

# Animationa  -----------------------------|
animation_database = {}
animation_database['player_run'] = load_animation('run', 'data/anim/run', [3, 3, 3], 4)
animation_database['player_idle'] = load_animation('idle', 'data/anim/idle', [6, 6, 6], 4)
player.set_animations('player_idle', False, animation_database)

# Levels  ---------------------------------|
colliders_list = []
tiles = [[195, bricks_top_left, True],
         [0, bricks_top_center, True],
         [127, bricks_top_right, True],
         [73, bricks_left, True],
         [44, bricks_center, False],
         [133, bricks_right, True],
         [181, simple_grass, False]]

map_1 = TileMap(map_image_1, tiles, [0, 0])
for rect in map_1.get_tile_map():
    colliders_list.append(rect)

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_w or event.key == K_UP:
                player.jumping = True
            if event.key == K_l:
                collider_attack = player.attack()
                attackGroup.add(collider_attack)

        elif event.type == MOUSEBUTTONDOWN:
            click = True

    # logic update  ---------------------------------|
    timerGroup.update()
    if player.speed == 0:
        player.new_value = 'player_idle'
        player.change_action()
    else:
        player.new_value = 'player_run'
        player.change_action()

    player.update(colliders_list)
    enemyGroup.update(colliders_list)
    attackGroup.update(enemyGroup)

    scroll, first_time = scroll_player(player, size_display, scroll, 15, first_time, [True, True])
    # scroll_wasd(scroll, 15)

    # draw  -----------------------------------------|
    display.fill([0, 0, 0])
    map_1.draw(display, scroll)
    # click = set_entities_positions(Entity([player.rect.x, player.rect.y], [player.rect.w, player.rect.h], enemy_image, True), click, display, scroll, enemyGroup, positions_enemy)
    draw_group(display, scroll, enemyGroup)
    draw_group(display, scroll, attackGroup)
    player.draw(display, scroll=scroll)

    # update  ---------------------------------------|
    pygame.display.update()
    clock.tick(fps)

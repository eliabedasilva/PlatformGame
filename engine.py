import pygame, copy
from pygame.locals import *


class Timer(pygame.sprite.Sprite):
    def __init__(self, timer_limit, count_limit, *groups):
        super().__init__(*groups)
        self.timer_limit = timer_limit
        self.time = 0
        self.count_limit = count_limit
        self.count = 0

    def update(self):
        self.time += 1

    def check_time(self):
        if self.count == self.count_limit:
            self.kill()
            return False

        if self.time == self.timer_limit:
            if self.count_limit < 0:
                pass
            else:
                self.count += 1
            self.time = 0
            return True


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, size, image, debug):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        if image != '':
            self.rect2 = image.get_rect()
        self.image = image
        self.debug = debug
        self.has_animationss = False

    def update(self):
        if self.has_animations:
            self.uptade_animation()

    def draw(self, display, scroll=[0, 0], color=(79, 79, 79)):

        if self.image == '':
            pygame.draw.rect(display, color,
                             (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h))
        else:
            self.rect2.center = self.rect.center
            display.blit(self.image, (self.rect2.x - scroll[0], self.rect2.y - scroll[1]))

        if self.debug:
            pygame.draw.rect(display, (0, 250, 83),
                             (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h), 1)

    def set_animations(self, action, flip, animation_database):
        self.frame = 0
        self.action = action
        self.flip = flip
        self.animation_database = animation_database
        self.has_animations = True

    def update_animation(self):
        self.frame += 1
        if self.frame >= len(self.animation_database[self.action]):
            self.frame = 0
        self.frame_id = self.animation_database[self.action][self.frame]
        self.image = pygame.transform.flip(animation_frames[self.frame_id], self.flip, False)
        self.rect2 = self.image.get_rect()

    def change_action(self):
        if self.action != self.new_value:
            self.action = self.new_value
            self.frame = 0


class RigidyBory(Entity):
    def __init__(self, pos, size, image, gravity_acceleration, debug):
        super().__init__(pos, size, image, debug)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        if image != '':
            self.rect2 = image.get_rect()
        self.image = image
        self.debug = debug
        self.has_animations = False
        self.gravity_acceleration = gravity_acceleration
        self.gravity = 0

    def update(self, colliders_list):
        self.update_gravity(colliders_list)
        if self.has_animations:
            self.uptade_animation()

    def update_gravity(self, colliders_list):
        self.rect.y += self.gravity
        if self.gravity < self.rect.h:
            self.gravity += self.gravity_acceleration
        if self.gravity < 0:
            colliders = test_collision_list(colliders_list, self)
            collision_2d(colliders, self, 'top')
        elif self.gravity > 0:
            colliders = test_collision_list(colliders_list, self)
            collision_2d(colliders, self, 'bottom')


class SimplePlayer(RigidyBory):
    def __init__(self, pos, size, image, speed_acceleration, max_speed, gravity_acceleration, jump_force, count_jump,
                 debug):
        super().__init__(pos, size, image, debug, gravity_acceleration)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.image = image
        if self.image != '':
            self.rect2 = image.get_rect()
            self.image_copy = self.image.copy()
        self.debug = debug
        self.has_animations = False
        self.gravity_acceleration = gravity_acceleration
        self.speed_acceleration = speed_acceleration
        self.speed = 0
        self.max_speed = max_speed
        self.count_jump = count_jump
        self.air_time = self.count_jump
        self.jump_force = jump_force
        self.jumping = False
        self.test = 0

    def update(self, colliders_list):
        self.jump()
        self.update_gravity(colliders_list)
        self.movement(colliders_list)
        if self.has_animations:
            self.update_animation()

    def movement(self, colliders_list):
        keys = pygame.key.get_pressed()
        if (keys[K_a] or keys[K_LEFT]) and self.speed >= -self.max_speed:
            if self.speed > 0:
                self.speed = 0
            self.speed -= self.speed_acceleration
            self.rect.x += self.speed
            colliders = test_collision_list(colliders_list, self)
            collision_2d(colliders, self, 'left')
            self.flip = True
        elif (keys[K_d] or keys[K_RIGHT]) and self.speed <= self.max_speed:
            if self.speed < 0:
                self.speed = 0
            self.speed += self.speed_acceleration
            self.rect.x += self.speed
            colliders = test_collision_list(colliders_list, self)
            collision_2d(colliders, self, 'right')
            self.flip = False
        else:
            if self.speed > 0:
                self.speed -= self.speed_acceleration
                self.rect.x += self.speed
                colliders = test_collision_list(colliders_list, self)
                collision_2d(colliders, self, 'right')
                self.flip = False
            elif self.speed < 0:
                self.speed += self.speed_acceleration
                self.rect.x += self.speed
                colliders = test_collision_list(colliders_list, self)
                collision_2d(colliders, self, 'left')
                self.flip = True

    def jump(self):
        if self.jumping:
            self.jumping = False
            if self.air_time < self.count_jump:
                self.air_time += 1
                self.gravity = -self.jump_force


class TileMap():
    def __init__(self, image, tiles, pos):

        self.tile_map = []
        self.colliders_list = []
        self.pos = pos
        tile_size = tiles[1][1].get_height()
        pos_x = self.pos[0]
        for x in range(image.get_width()):
            pos_y = self.pos[1]
            for y in range(image.get_height()):
                for tile in tiles:
                    if image.get_at((x, y))[0] == tile[0]:
                        if tile[1] != '':
                            Tile = Entity((pos_x, pos_y), (tile_size, tile_size), tile[1], False)
                            if tile[2]:
                                self.colliders_list.append(Tile.rect)
                            self.tile_map.append(Tile)
                pos_y += tile_size
            pos_x += tile_size

    def get_tile_map(self):
        return self.colliders_list

    def draw(self, display, scroll):
        for Tile in self.tile_map:
            Tile.draw(display, scroll)


class ButtonSystem():
    def __init__(self, buttons, input_method, selector=''):
        self.input_method = input_method
        self.buttons = []
        for button in buttons:
            self.buttons.append([Entity(button[0], button[1], button[2], button[3]), button[4]])

        self.click = False
        if self.input_method.upper().strip() == 'SELECTOR':
            self.runner = 0
            self.selector = selector

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.click:
            if self.input_method.upper().strip() == 'MOUSE':
                for button in self.buttons:
                    if button[0].rect.collidepoint(mouse_pos):
                        button[1] = True
                    print(button[1])

            elif self.input_method.upper().strip() == 'SELECTOR':
                self.buttons[self.runner][1] = True
                print(self.buttons[self.runner][1])

            self.click = False

        if self.input_method.upper().strip() == 'SELECTOR':
            if self.selector != '':
                self.selector.rect.center = self.buttons[self.runner][0].rect.center

    def draw(self, display, color=(255, 0, 0)):
        if self.input_method.upper().strip() == 'SELECTOR':
            if self.selector != '':
                self.selector.draw(display, color=color)
        for button in self.buttons:
            button[0].draw(display, color=color)


def load_image(path, size):
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (int(image.get_width() * size), int(image.get_height() * size)))
    return image


global animation_frames
animation_frames = {}


def load_animation(name, path, frame_durations, size):
    global animation_frames
    animation_name = name
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = load_image(img_loc, size)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1

    return animation_frame_data


def collision_2d(colliders, bory, direction):
    for collider in colliders:
        if direction == 'right':
            bory.rect.right = collider.left
        elif direction == 'left':
            bory.rect.left = collider.right
        elif direction == 'bottom':
            bory.rect.bottom = collider.top
            bory.gravity = 0
            bory.air_time = 0
        elif direction == 'top':
            bory.rect.top = collider.bottom
            bory.gravity = 0


def test_collision_list(colliders, bory):
    colliders_list = []
    for collider in colliders:
        if bory.rect.colliderect(collider) and bory.rect != collider:
            colliders_list.append(collider)
            break
    return colliders_list


def draw_line():
    print('-' * 15)


def set_entities_positions(entity, click, display, scroll, group, positions):
    mouse = pygame.mouse.get_pos()
    entity.rect.center = (mouse)
    entity.draw(display, [0, 0])

    if click:
        entity.rect.x += scroll[0]
        entity.rect.y += scroll[1]
        group.add(entity)
        positions.append([entity.rect.x, entity.rect.y])

    counter = 0
    for entity in group:
        if pygame.mouse.get_pressed()[2] and entity.rect.collidepoint((mouse[0] + scroll[0], mouse[1] + scroll[1])):
            group.remove(entity)
            positions.pop(counter)
        counter = len(group) - 1

    for entity in group:
        entity.draw(display, scroll)

    keys = pygame.key.get_pressed()
    if keys[K_p]:
        draw_line()
        print(positions)
        draw_line()

    return False


def get_entities(entity, image, positions, group):
    for position in positions:
        entity_copy = copy.deepcopy(entity)
        entity_copy.rect.x = position[0]
        entity_copy.rect.y = position[1]
        if image != '':
            entity_copy.image = image
            entity_copy.rect2 = image.get_rect()
        group.add(entity_copy)


def scroll_wasd(scroll, scroll_speed):
    keys = pygame.key.get_pressed()

    if keys[K_w] or keys[K_UP]:
        scroll[1] -= scroll_speed
    if keys[K_s] or keys[K_DOWN]:
        scroll[1] += scroll_speed
    if keys[K_a] or keys[K_LEFT]:
        scroll[0] -= scroll_speed
    if keys[K_d] or keys[K_RIGHT]:
        scroll[0] += scroll_speed

    return scroll


def scroll_player(player, display_size, scroll, delay, first_time, directions):
    if first_time:
        delay = 1
        first_time = False
    if directions[0]:
        scroll[0] += int((player.rect.x - scroll[0] - (display_size[0] / 2 - player.rect.w / 2)) / delay)
    if directions[1]:
        scroll[1] += int((player.rect.y - scroll[1] - (display_size[1] / 2 - player.rect.h / 2)) / delay)

    return scroll, first_time


def draw_group(display, scroll, group):
    for entity in group:
        entity.draw(display, scroll)

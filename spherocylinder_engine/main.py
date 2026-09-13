import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

icon = pygame.image.load("assets\\icon.png")
hit_sound = pygame.mixer.Sound("assets\\hit.mp3")
Arial = pygame.font.SysFont('Arial', 15)
debug = pygame.font.SysFont('Arial', 10)

sound = True
debug_txt = True

fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Spherocylinder Engine")
pygame.display.set_icon(icon)

velocity_x = 0
velocity_y = 0

acceleration_x = 0
acceleration_y = 0

obj_x = 320
obj_y = 240

gravity = 500

bounciness = 0.5

while True:
    dt = fpsClock.tick(fps) / 1000
    screen.fill((0, 0, 0))
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                sound = not sound
            if event.key == pygame.K_h:
                debug_txt = not debug_txt

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            last_obj_x = obj_x
            last_obj_y = obj_y
    
    if pygame.mouse.get_pressed()[0]:
        velocity_x, velocity_y = 0, 0
        acceleration_x, acceleration_y = 0, 0

        acceleration_x += (last_obj_x - mouse_x) * 250
        acceleration_y += (last_obj_y - mouse_y) * 250

        obj_x, obj_y = mouse_x, mouse_y

    else:
        velocity_x += acceleration_x * dt
        velocity_y += acceleration_y * dt

        obj_x += velocity_x * dt
        obj_y += velocity_y * dt

        acceleration_y = gravity
        acceleration_x = 0

    if obj_x <= 5 or obj_x >= width - 5:
        if sound:
            hit_sound.play()

        if obj_x <= 5:
            obj_x = 5
        else:
            obj_x = width - 5

        velocity_x *= bounciness * -1


    if obj_y <= 5 or obj_y >= height - 5:
        if sound:
            hit_sound.play()

        if obj_y <= 5:
            obj_y = 5
        else:
            obj_y = height - 5

        velocity_y *= bounciness * -1

    pygame.draw.circle(screen, (255, 255, 255), (obj_x, obj_y), 5)

    text_surface = Arial.render(f'Fps: {int(fpsClock.get_fps())}', False, (255, 255, 255))

    obj_pos_text = debug.render(f'obj x, obj y: {int(obj_x)}, {int(obj_y)}', False, (255, 255, 255))
    vel_text = debug.render(f'vel x, vel y: {int(velocity_x)}, {int(velocity_y)}', False, (255, 255, 255))
    acc_text = debug.render(f'acc x, acc y: {int(acceleration_x)}, {int(acceleration_y)}', False, (255, 255, 255))
    grav_text = debug.render(f'grav: {float(gravity)}', False, (255, 255, 255))
    bounce_text = debug.render(f'bounce: {float(bounciness)}', False, (255, 255, 255))
    sound_text = debug.render(f'sound: {bool(sound)}', False, (255, 255, 255))

    screen.blit(text_surface, (10, 10))

    if debug_txt:
        screen.blit(obj_pos_text, (10, 30))
        screen.blit(vel_text, (10, 50))
        screen.blit(acc_text, (10, 70))
        screen.blit(grav_text, (10, 90))
        screen.blit(bounce_text, (10, 110))
        screen.blit(sound_text, (10, 130))

    pygame.display.flip()
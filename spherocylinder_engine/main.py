import pygame
from pygame.locals import *
import functions

pygame.init()
pygame.font.init()

icon = pygame.image.load("assets\\icon.png")
hit_sound = pygame.mixer.Sound(functions.sounds["hit"])
Arial = pygame.font.SysFont('Arial', 15)
debug = pygame.font.SysFont('Arial', 10)

sound = True
debug_txt = True
trajectory = True
rgb = True

fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Spherocylinder Engine")
pygame.display.set_icon(icon)

trajectory_surface = pygame.Surface((width, height), pygame.SRCALPHA)

color = (255, 255, 255)

velocity_x = 0
velocity_y = 0

acceleration_x = 0
acceleration_y = 0

obj_x = 320
obj_y = 240

last_obj_x = 320
last_obj_y = 240

gravity = 500

bounciness = 0.5

timewarp = 1

trajectory_length = 100
trajectory_dt = 1 / fps

while True:
    dt = fpsClock.tick(fps) / 1000 * timewarp
    screen.fill((0, 0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x = max(0, min(mouse_x, width))
    mouse_y = max(0, min(mouse_y, height))

    if rgb:
        color = functions.rgb(1)
    else:
        color = (255, 255, 255)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                sound = not sound
            if event.key == pygame.K_h:
                debug_txt = not debug_txt
            if event.key == pygame.K_f:
                trajectory = not trajectory
            if event.key == pygame.K_j:
                rgb = not rgb

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                timewarp += 0.1
            elif event.y < 0:
                timewarp -= 0.1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                last_obj_x = mouse_x
                last_obj_y = mouse_y
            if event.button == 2:
                timewarp = 1
    
    if pygame.mouse.get_pressed()[0]:
        velocity_x, velocity_y = 0, 0
        acceleration_x, acceleration_y = 0, 0

        acceleration_x += (last_obj_x - mouse_x) * 250
        acceleration_y += (last_obj_y - mouse_y) * 250

        obj_x, obj_y = mouse_x, mouse_y

        trajectory_x = obj_x
        trajectory_y = obj_y

        trajectory_velocity_x = acceleration_x * trajectory_dt
        trajectory_velocity_y = acceleration_y * trajectory_dt

        previous_x = trajectory_x
        previous_y = trajectory_y

        trajectory_surface.fill((0, 0, 0, 0))
        for i in range(trajectory_length):
            
            trajectory_x += trajectory_velocity_x * trajectory_dt
            trajectory_y += trajectory_velocity_y * trajectory_dt

            trajectory_velocity_y += gravity * trajectory_dt

            if trajectory_x <= 5 or trajectory_x >= width - 5:
                if trajectory_x <= 5:
                    trajectory_x = 5
                else:
                    trajectory_x = width - 5

                trajectory_velocity_x *= bounciness * -1


            if trajectory_y <= 5 or trajectory_y >= height - 5:
                if trajectory_y <= 5:
                    trajectory_y = 5
                else:
                    trajectory_y = height - 5

                trajectory_velocity_y *= bounciness * -1

            if trajectory:
                pygame.draw.line(trajectory_surface, (255, 255, 255, 128), (previous_x, previous_y), (trajectory_x, trajectory_y), 2)

            previous_x = trajectory_x
            previous_y = trajectory_y

        screen.blit(trajectory_surface, (0, 0))

    else:
        velocity_x += acceleration_x * dt
        if obj_y < height - 5 or velocity_y < 0 or acceleration_y != gravity:
            velocity_y += acceleration_y * dt

        obj_x += velocity_x * dt
        obj_y += velocity_y * dt

        acceleration_y = gravity
        acceleration_x = 0

    if obj_x <= 5 or obj_x >= width - 5:
        obj_x = 5 if obj_x <= 5 else width - 5

        if abs(velocity_x) > 5:
            if sound:
                hit_sound.play()
            velocity_x *= -bounciness
        else:
            velocity_x = 0

    if obj_y <= 5 or obj_y >= height - 5:
        obj_y = 5 if obj_y <= 5 else height - 5

        if abs(velocity_y) > 5:
            if sound:
                hit_sound.play()
            velocity_y *= -bounciness
        else:
            velocity_y = 0

    pygame.draw.circle(screen, color, (obj_x, obj_y), 5)

    text_surface = Arial.render(f'Fps: {int(fpsClock.get_fps())}', False, (255, 255, 255))

    obj_pos_text = debug.render(f'obj x, obj y: {int(obj_x)}, {int(obj_y)}', False, (255, 255, 255))
    vel_text = debug.render(f'vel x, vel y: {int(velocity_x)}, {int(velocity_y)}', False, (255, 255, 255))
    acc_text = debug.render(f'acc x, acc y: {int(acceleration_x)}, {int(acceleration_y)}', False, (255, 255, 255))
    grav_text = debug.render(f'grav: {float(gravity)}', False, (255, 255, 255))
    bounce_text = debug.render(f'bounce: {float(bounciness)}', False, (255, 255, 255))
    timewarp_text = debug.render(f'timewarp: {timewarp:.1f}', False, (255, 255, 255))
    trajectory_text = debug.render(f'traj, length: {bool(trajectory)}, {int(trajectory_length)}', False, (255, 255, 255))
    delta_text = debug.render(f'dt, traj dt: {float(dt)}, {float(trajectory_dt)}', False, (255, 255, 255))
    color_text = debug.render(f'rgb, color: {bool(rgb)}, {(color)}', False, (255, 255, 255))
    sound_text = debug.render(f'sound: {bool(sound)}', False, (255, 255, 255))

    screen.blit(text_surface, (10, 10))

    if debug_txt:
        screen.blit(obj_pos_text, (10, 30))
        screen.blit(vel_text, (10, 50))
        screen.blit(acc_text, (10, 70))
        screen.blit(grav_text, (10, 90))
        screen.blit(bounce_text, (10, 110))
        screen.blit(timewarp_text, (10, 130))
        screen.blit(trajectory_text, (10, 150))
        screen.blit(delta_text, (10, 170))
        screen.blit(color_text, (10, 190))
        screen.blit(sound_text, (10, 210))

    pygame.display.flip()
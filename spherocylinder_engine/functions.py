import pygame
import colorsys

sounds = {
    "vine": ("assets\\sounds\\vine.mp3"),
    "fah": ("assets\\sounds\\fah.mp3"),
    "hit": ("assets\\sounds\\hit.mp3"),
    "goggins": ("assets\\sounds\\goggins.mp3"),
    "rizz": ("assets\\sounds\\rizz.mp3"),
    "shotgun": ("assets\\sounds\\shotgun.mp3"),
    "error": ("assets\\sounds\\error.mp3"),
    "ah": ("assets\\sounds\\ah.mp3"),
    "bruh": ("assets\\sounds\\bruh.mp3"),
    "xp": ("assets\\sounds\\xp.mp3")
}

def rgb(speed):
    hue = (pygame.time.get_ticks() / (speed * 1000)) % 1

    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)

    return int(r * 255), int(g * 255), int(b * 255)
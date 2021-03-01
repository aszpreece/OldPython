import math
import pygame as pg


def clamp(val, minimum, maximum):
    return min(maximum, max(minimum, val))


def calculate_angle_diff(a1, a2):
    diff_angle = a1 - a2
    return (diff_angle + 180) % 360 - 180


def angle_between_points(v1, v2):
    diff = v1 - v2
    return math.degrees(math.atan2(-diff.y, diff.x)) % 360


def get_acceleration_delta(angle, amount):
    return pg.Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle))) * amount

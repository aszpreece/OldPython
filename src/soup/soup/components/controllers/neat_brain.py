import math
from src.util.util import get_acceleration_delta
import pygame as pg
from random import Random

from src.soup.soup.components.controller import Controller


class NeatBrain(Controller):
    def __init__(self, brain, v_acceleration=0.005, r_acceleration=0.1):
        super().__init__()
        self.brain = brain
        self.v_acceleration = v_acceleration
        self.r_acceleration = r_acceleration

    def update(self, entity):
        eye_left = entity.get_component_by_name('eyeL').activation
        eye_right = entity.get_component_by_name('eyeR').activation
        
        self.brain.set('bias', 1)
        self.brain.set('eyeL', eye_left)
        self.brain.set('eyeR', eye_right)
        self.brain.calculate()
        
        v = self.brain.get('v_accel')
        r = self.brain.get('r_accel')

        vel = entity.get_component_by_name('velocity')
        vel.vel += get_acceleration_delta(entity._rot, self.v_acceleration * v) 
        vel.rot_v += 2 * (r -0.5) * self.r_acceleration
 
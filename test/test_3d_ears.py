import unittest

from pygame import Vector2
from experiment.swarm_2d.swarm_2d import Swarm2D, CreatureBrain2D, Swarm2DConfig
import pygame.math
import math


class TestBrain(CreatureBrain2D):

    def get_movement(self) -> float:
        return 0

    def get_rotation(self) -> float:
        return 0

    def get_sound(self) -> float:
        return 1

    def update(self, sounds, obst_in_front, x, y, obst_dist=0) -> None:
        self.sounds = sounds
        self.obst_in_front = obst_in_front
        self.x = x
        self.y = y
        self.obst_dist = obst_dist


class Ears3D(unittest.TestCase):

    def test_correct_inputs(self):
        brain = TestBrain()
        instance = Swarm2D([brain], Swarm2DConfig())

        res = instance.calculate_input_to_ear(Vector2(0, 1), Vector2(0, 1), 10)
        self.assertAlmostEqual(res, 10)

        res = instance.calculate_input_to_ear(Vector2(0, 1), Vector2(1, 0), 0)
        self.assertAlmostEqual(res, 0)

        res = instance.calculate_input_to_ear(
            Vector2(0, 1), Vector2(0, -1), 10)
        self.assertAlmostEqual(res, 0)

        res = instance.calculate_input_to_ear(
            Vector2(0, 1), Vector2(math.cos(math.pi/4), math.sin(math.pi/4)), 10)
        self.assertAlmostEqual(res, 10 * math.cos(math.pi/4))

    def test_correct_ears(self):
        brain1 = TestBrain()
        brain2 = TestBrain()
        brain3 = TestBrain()

        instance = Swarm2D([brain1, brain2, brain3], Swarm2DConfig())

        instance.birds[0].pos = Vector2(0, 0)
        instance.birds[1].pos = Vector2(1, 0)
        instance.birds[2].pos = Vector2(2, 2)

        instance.update()

        ear_expected = [(1 + math.cos(math.pi/4) * 1) / 3, (math.cos(math.pi/4) * 1+1) / 3,
                        math.cos(math.pi/4) / 3, 0, 0, 0, 0, math.cos(math.pi/4) / 3]

        for s, e in zip(instance.birds[0].brain.sounds, ear_expected):
            self.assertAlmostEqual(s, e)


from random import Random
from src.soup.soup.system.rigid_body_system import RigidBodySystem
from src.soup.soup.system.food_system import FoodSystem
from src.soup.soup.components.controllers.camera_controller import CameraController
import pygame as pg
import matplotlib.pyplot as plt

import src.soup.engine.ecs as ecs
from experiment.run_experiment import train_neat
from src.neat.genotype import (ConnectionGene, Genotype, NodeGene,
                               generate_perceptron_connections, mod_sigmoid,
                               sigmoid)
from src.neat.mutate import DefaultMutationManager
from src.neat.neat_config import NeatConfig
from src.neat.phenotype import Phenotype
from src.neat.reproduction import DefaultReproductionManager
from src.soup.soup.components import Camera, Circle, Friction, Velocity
from src.soup.soup.system import (FrictionSystem, MovementSystem, Render,
                                  VelocitySystem, ControllerSystem, BrainSystem, SoundSystem)

from src.soup.soup.components.mouth import Mouth
from src.soup.soup.system.eye_system import EyeSystem
from src.soup.soup.system.mouth_system import MouthSystem

import json

if __name__ == '__main__':

    # Keep track of how much food was eaten per generation
    food_eaten_history = []
    critter_scores_history = []

    entity_data = None
    with open('C:/_development/fyp/test/test_entity.json') as entity_json:
        entity_data = json.loads(entity_json.read())

    def fitness_function(genotypes):
        world_width = 200
        world_height = 200
        food_count = len(genotypes) * 9

        manager = ecs.ECS(world_width, world_height, 10)
        manager.add_entity(pos=pg.Vector2(0, 0)) \
            .attach(Camera({})) \
            .attach(CameraController({'camera_acceleration': 0.1})) \
            .attach(Velocity({'name': 'velocity'})) \
            .attach(Friction({'mass': 1, 'coef_f': 0.01}))

        rand = Random()
        critters = []
        for genotype in genotypes:
            x = rand.randrange(0, world_width)
            y = rand.randrange(0, world_height)
            vx = 0
            vy = 0
            rot = rand.randrange(0, 360)
            brain = Phenotype(genotype)
            critter = manager.add_entity(pos=pg.Vector2(
                x, y), rot=rot).from_dict(entity_data)
            critter.get_component_by_name('brain').brain = brain

            # Log the this genome's entity
            critters.append(critter)

        manager.add_system(BrainSystem(manager))
        manager.add_system(ControllerSystem(manager))
        # manager.add_system(RigidBodySystem(manager))
        manager.add_system(SoundSystem(manager))
        manager.add_system(MovementSystem(manager))
        manager.add_system(VelocitySystem(manager))
        manager.add_system(FrictionSystem(manager))
        manager.add_system(EyeSystem(manager))
        manager.add_system(MouthSystem(manager))
        manager.add_system(FoodSystem(manager, food_count, 6))

        time_delay = round(1000.0/60)
        time_delay = 0
        screen = pg.display.set_mode((1000, 1000))
        pg.display.set_caption('Soup')

        manager.add_system(Render(manager, screen))

        # 60 ticks per second, so to run for 30 seconds = 30 * 60
        for i in range(30 * 60):
            pg.init()
            screen.fill((255, 255, 255))
            pg.event.pump()
            manager.update()
            pg.display.flip()
            # pg.time.delay(time_delay)  # 1 second == 1000 milliseconds

        pg.display.quit()
        pg.quit()

        total_eaten = 0
        critter_scores = []
        for genotype, critter in zip(genotypes, critters):
            mouths = critter.get_components(Mouth.c_type_id)
            [mouth] = mouths
            genotype.fitness = mouth.eaten_count
            total_eaten += mouth.eaten_count
            critter_scores.append(mouth.eaten_count)

        food_eaten_history.append(total_eaten)
        critter_scores_history.append(critter_scores)

    base_genotype = Genotype()
    base_genotype.from_dict(
        list(filter(lambda c: c['class'] == 'Brain', entity_data['components']))[0])

    config = NeatConfig(
        activation_func=sigmoid,
        fitness_function=fitness_function,
        base_genotype=base_genotype,
        reproduction=DefaultReproductionManager(),
        generation_size=150,
        mutation_manager=DefaultMutationManager(base_genotype),
        species_target=10,
        species_mod=0.1,
        prob_crossover=0,  # 0.8,
        weight_perturb_scale=1,
        new_weight_power=0.8,
        sim_disjoint_weight=1.0,
        sim_excess_weight=1.0,
        sim_weight_diff_weight=0.3,
        sim_genome_length_threshold=20,
        sim_threshold=3.0,
        species_stag_thresh=40,
        allow_recurrence=True,
        prob_inherit_from_fitter=0.5,
        weight_random_type='gaussian',
        run_id=f'test_soup',
        fitness_function_type='population',
        initial_seeding_style='random'
    )

    # plt.ion()
    fig, axarr = plt.subplots(2, figsize=(6, 8))
    plt.subplots_adjust(wspace=0.5, hspace=1)
    fig.show()
    fig.canvas.draw()

    def result_func(neat):

        axarr[0].clear()
        axarr[0].set(title=f"Food eaten",
                     xlabel='Generation', ylabel='Pellets Eaten')
        axarr[0].plot(food_eaten_history)

        axarr[1].clear()
        axarr[1].set(title=f"Score histogram generation: {neat.generation_num}",
                     xlabel='Pellets Eaten', ylabel='Critters')
        axarr[1].hist(critter_scores_history[neat.generation_num - 1], bins=20)

        pass

        fig.canvas.draw()

    train_neat(fitness_func=fitness_function,
               result_func=result_func, config=config)

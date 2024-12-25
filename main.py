import neat
import pygame

from app import gui


def run_manual():
    gui.main()


def run_generation():
    # setup config
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # init NEAT
    p = neat.Population(config)

    # run NEAT
    print("Running NEAT")
    p.run(gui.run_generation, 1000)
    print("NEAT finished")


if __name__ == '__main__':
    run_generation()
    pygame.quit()

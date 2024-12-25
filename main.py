import neat
import pygame

import app.gui.manual
import app.gui.neat
import app.gui.hamilton


def run_manual():
    app.gui.manual.main()


def run_generation():
    # setup config
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # init NEAT
    p = neat.Population(config)

    # run NEAT
    print("Running NEAT")
    p.run(app.gui.neat.run_generation, 1000)
    print("NEAT finished")


def run_hamilton():
    app.gui.hamilton.main()


if __name__ == '__main__':
    run_hamilton()
    pygame.quit()

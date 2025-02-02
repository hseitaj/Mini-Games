#!/usr/bin/env python3
# libraries needed:
# pip install pygame
# to run in terminal: python main.py
# This script is intended to be compiled with pygbag for web deployment.

import pygame
import sys

# Import the main functions from your mini game modules.
# Make sure each game module has a main() function defined.
# For example, if arena_clash.py, two_player_tetris.py, and zombie_lane.py are in your games folder,
# ensure that each one has a callable main() that starts the game.
from games.arena_clash import main as arena_clash_main
from games.two_player_tetris import main as tetris_main
from games.zombie_lane import main as zombie_lane_main  # Adjust if your third game has a different name

# Define the list of games for the launcher.
GAMES = [
    ("Arena Clash: Valor vs Nemesis", arena_clash_main),
    ("Two-Player Tetris", tetris_main),
    ("Zombie Lane", zombie_lane_main)
]


def run_launcher():
    """
    Runs a simple launcher menu that lets the user select one of the mini games.
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Mini Games Launcher")
    font = pygame.font.SysFont("Arial", 36)
    clock = pygame.time.Clock()

    selected = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(GAMES)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(GAMES)
                elif event.key == pygame.K_RETURN:
                    # Call the selected game's main function.
                    # Note: This call will block the launcher loop and run the game.
                    GAMES[selected][1]()
                    # After the game exits, reinitialize the launcher.
                    pygame.display.set_mode((800, 600))

        screen.fill((0, 0, 0))
        title = font.render("Select a Mini Game", True, (255, 255, 255))
        screen.blit(title, (200, 50))

        for i, (game_name, _) in enumerate(GAMES):
            color = (255, 215, 0) if i == selected else (255, 255, 255)
            text = font.render(game_name, True, color)
            screen.blit(text, (100, 150 + i * 50))

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    run_launcher()

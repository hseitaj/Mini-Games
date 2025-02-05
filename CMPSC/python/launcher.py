# #!/usr/bin/env python3
# # This launcher lets the user choose among your mini games.
# # It is intended to be compiled with pygbag for web deployment.
#
# import pygame
# import sys
#
# # Import the main functions from your mini game modules.
# # Ensure each game module defines a main() function.
# from CMPSC.python.arena_clash import main as arena_clash_main
# from CMPSC.python.two_player_tetris import main as tetris_main
# from CMPSC.python.zombie_lane import main as zombie_lane_main  # Adjust the name if necessary
#
# # List of games as (display_name, main_function)
# GAMES = [
#     ("Arena Clash: Valor vs Nemesis", arena_clash_main),
#     ("Two-Player Tetris", tetris_main),
#     ("Zombie Lane", zombie_lane_main)
# ]
#
#
# def run_launcher():
#     pygame.init()
#     screen = pygame.display.set_mode((800, 600))
#     pygame.display.set_caption("Mini Games Launcher")
#     font = pygame.font.SysFont("Arial", 36)
#     clock = pygame.time.Clock()
#
#     selected = 0
#     running = True
#
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#                 pygame.quit()
#                 sys.exit()
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     selected = (selected - 1) % len(GAMES)
#                 elif event.key == pygame.K_DOWN:
#                     selected = (selected + 1) % len(GAMES)
#                 elif event.key == pygame.K_RETURN:
#                     # Run the selected game; note that this call blocks until the game exits.
#                     GAMES[selected][1]()
#                     # After the game exits, reinitialize the launcher display.
#                     pygame.display.set_mode((800, 600))
#
#         screen.fill((0, 0, 0))
#         title = font.render("Select a Mini Game", True, (255, 255, 255))
#         screen.blit(title, (200, 50))
#
#         for i, (game_name, _) in enumerate(GAMES):
#             color = (255, 215, 0) if i == selected else (255, 255, 255)
#             text = font.render(game_name, True, color)
#             screen.blit(text, (100, 150 + i * 50))
#
#         pygame.display.flip()
#         clock.tick(30)
#
#
# if __name__ == '__main__':
#     run_launcher()

#!/usr/bin/env python3
# libraries needed
# pip install pygame pytest
# to run it in terminal: python arena_clash.py

import pygame
import sys
import math
import random

# Global constants for the game.
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Hero constants.
HERO_SIZE = 50
HERO_SPEED = 5
ATTACK_RANGE = 60
ATTACK_DAMAGE = 10
ATTACK_COOLDOWN = 500  # milliseconds

# Minion constants (adjusted: smaller and less damage).
MINION_SIZE = 20
MINION_SPEED = 3
MINION_HEALTH = 20
MINION_ATTACK_DAMAGE = 2
MINION_ATTACK_RANGE = 40
MINION_ATTACK_COOLDOWN = 700  # milliseconds
MINION_PRODUCTION_COOLDOWN = 2000  # milliseconds

# Define colors.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
# New hero colors.
VALOR_COLOR = (30, 144, 255)  # Dodger Blue.
NEMESIS_COLOR = (220, 20, 60)  # Crimson.


def distance_between(point1, point2):
    """
    Calculate the Euclidean distance between two points.

    Args:
        point1 (tuple of float): Coordinates (x, y) of the first point.
        point2 (tuple of float): Coordinates (x, y) of the second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx * dx + dy * dy)


def draw_background(surface):
    """
    Draw background visuals on the given surface.

    A dark gray background with grid lines is drawn to improve UI visuals.

    Args:
        surface (pygame.Surface): The surface to draw on.
    """
    surface.fill((50, 50, 50))
    grid_color = (70, 70, 70)
    cell_size = 50
    for x in range(0, SCREEN_WIDTH, cell_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, cell_size):
        pygame.draw.line(surface, grid_color, (0, y), (SCREEN_WIDTH, y))


def draw_instructions(surface, font):
    """
    Draw game instructions on the given surface.

    The instructions are displayed at the bottom left of the screen.

    Args:
        surface (pygame.Surface): The surface to draw on.
        font (pygame.font.Font): The font used for rendering text.
    """
    instructions = [
        "Valor (Player 1): Arrow keys to move, Space to attack, R to produce minion",
        "Nemesis (Player 2): WASD to move, Q to attack, E to produce minion"
    ]
    x = 20
    y = SCREEN_HEIGHT - (len(instructions) * 30) - 20
    for line in instructions:
        text_surface = font.render(line, True, WHITE)
        surface.blit(text_surface, (x, y))
        y += 30


class Hero:
    """
    Class representing a hero unit in the game.
    """

    def __init__(self, x, y, color, controls, name):
        """
        Initialize the hero.

        Args:
            x (int): Initial x position.
            y (int): Initial y position.
            color (tuple): RGB color of the hero.
            controls (dict): Dictionary mapping actions ('up', 'down', 'left', 'right', 'attack', 'produce')
                             to pygame key constants.
            name (str): Name of the hero.
        """
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.name = name
        self.health = 100
        self.last_attack_time = 0
        self.minions = []
        self.last_minion_production = 0

    def get_center(self):
        """
        Get the center coordinates of the hero.

        Returns:
            tuple: (x, y) coordinates of the hero's center.
        """
        return (self.x + HERO_SIZE // 2, self.y + HERO_SIZE // 2)

    def move(self, dx, dy):
        """
        Move the hero by (dx, dy) while ensuring they remain within screen bounds.

        Args:
            dx (int): Change in x position.
            dy (int): Change in y position.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        # Ensure the hero stays within the screen boundaries.
        new_x = max(0, min(new_x, SCREEN_WIDTH - HERO_SIZE))
        new_y = max(0, min(new_y, SCREEN_HEIGHT - HERO_SIZE))

        self.x = new_x
        self.y = new_y

    def can_attack(self, current_time):
        """
        Check if the hero can attack based on the cooldown timer.

        Args:
            current_time (int): The current time in milliseconds.

        Returns:
            bool: True if the hero can attack, False otherwise.
        """
        return (current_time - self.last_attack_time) >= ATTACK_COOLDOWN

    def attack(self, enemy_hero, enemy_minions, current_time):
        """
        Attack the enemy hero or an enemy minion if within range and if the attack cooldown has elapsed.

        The hero will attack the enemy hero if in range; otherwise, it will check enemy minions.

        Args:
            enemy_hero (Hero): The enemy hero.
            enemy_minions (list): List of enemy minions.
            current_time (int): The current time in milliseconds.

        Returns:
            bool: True if the attack was successful, False otherwise.
        """
        if not self.can_attack(current_time):
            return False

        # Attack enemy hero if in range.
        if distance_between(self.get_center(), enemy_hero.get_center()) <= ATTACK_RANGE:
            enemy_hero.health -= ATTACK_DAMAGE
            self.last_attack_time = current_time
            return True

        # Otherwise, attack enemy minions.
        for minion in enemy_minions:
            if distance_between(self.get_center(), minion.get_center()) <= ATTACK_RANGE:
                minion.health -= ATTACK_DAMAGE
                self.last_attack_time = current_time
                return True

        self.last_attack_time = current_time
        return False

    def produce_minion(self, enemy, current_time):
        """
        Produce a minion if the production cooldown has passed.

        The minion is spawned near the hero's center.

        Args:
            enemy (Hero): The enemy hero (target for the minion).
            current_time (int): The current time in milliseconds.

        Returns:
            bool: True if a minion was produced, False otherwise.
        """
        if (current_time - self.last_minion_production) >= MINION_PRODUCTION_COOLDOWN:
            spawn_x = self.x + HERO_SIZE // 2 - MINION_SIZE // 2
            spawn_y = self.y + HERO_SIZE // 2 - MINION_SIZE // 2
            new_minion = Minion(spawn_x, spawn_y, self.color)
            self.minions.append(new_minion)
            self.last_minion_production = current_time
            return True
        return False

    def handle_movement(self, keys):
        """
        Update the hero's position based on the pressed keys.

        Args:
            keys (list): List of boolean values representing the state of all keys.
        """
        if keys[self.controls['up']]:
            self.move(0, -HERO_SPEED)
        if keys[self.controls['down']]:
            self.move(0, HERO_SPEED)
        if keys[self.controls['left']]:
            self.move(-HERO_SPEED, 0)
        if keys[self.controls['right']]:
            self.move(HERO_SPEED, 0)

    def draw(self, surface, font, position):
        """
        Draw the hero and its health bar on the given surface.

        Also draws hero info (health and current minion count) at a specified position.

        Args:
            surface (pygame.Surface): The surface to draw on.
            font (pygame.font.Font): Font to render text.
            position (tuple): (x, y) position to draw the hero's info.
        """
        center = (self.x + HERO_SIZE // 2, self.y + HERO_SIZE // 2)
        radius = HERO_SIZE // 2
        # Draw hero as a circle.
        pygame.draw.circle(surface, self.color, center, radius)

        # Draw health bar above the hero.
        health_bar_width = HERO_SIZE
        health_bar_height = 5
        health_percentage = max(self.health, 0) / 100
        current_health_width = health_bar_width * health_percentage
        health_bar_rect = pygame.Rect(self.x, self.y - health_bar_height - 2, current_health_width, health_bar_height)
        border_rect = pygame.Rect(self.x, self.y - health_bar_height - 2, health_bar_width, health_bar_height)
        pygame.draw.rect(surface, RED, border_rect)  # Health bar background.
        pygame.draw.rect(surface, (0, 255, 0), health_bar_rect)  # Green health bar.

        # Draw hero info (health and minion count).
        info_text = f"{self.name} Health: {self.health} | Minions: {len(self.minions)}"
        text_surface = font.render(info_text, True, WHITE)
        surface.blit(text_surface, position)


class Minion:
    """
    Class representing a minion unit.
    """

    def __init__(self, x, y, color):
        """
        Initialize the minion.

        Args:
            x (int): Initial x position.
            y (int): Initial y position.
            color (tuple): RGB color of the minion.
        """
        self.x = x
        self.y = y
        self.color = color
        self.health = MINION_HEALTH
        self.last_attack_time = 0

    def get_center(self):
        """
        Get the center coordinates of the minion.

        Returns:
            tuple: (x, y) coordinates of the minion's center.
        """
        return (self.x + MINION_SIZE // 2, self.y + MINION_SIZE // 2)

    def update(self, enemy_hero, current_time):
        """
        Update the minion's position and attack behavior.

        The minion moves toward the enemy hero. If within attack range and the attack cooldown
        has passed, it attacks the enemy hero.

        Args:
            enemy_hero (Hero): The enemy hero to target.
            current_time (int): The current time in milliseconds.
        """
        center = self.get_center()
        enemy_center = enemy_hero.get_center()
        dx = enemy_center[0] - center[0]
        dy = enemy_center[1] - center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > MINION_ATTACK_RANGE:
            # Normalize direction and move.
            if dist != 0:
                norm_dx = dx / dist
                norm_dy = dy / dist
            else:
                norm_dx = 0
                norm_dy = 0
            self.x += norm_dx * MINION_SPEED
            self.y += norm_dy * MINION_SPEED
        else:
            # Attack enemy hero if cooldown allows.
            if (current_time - self.last_attack_time) >= MINION_ATTACK_COOLDOWN:
                enemy_hero.health -= MINION_ATTACK_DAMAGE
                self.last_attack_time = current_time

    def draw(self, surface):
        """
        Draw the minion and its health bar on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        center = (int(self.x + MINION_SIZE // 2), int(self.y + MINION_SIZE // 2))
        radius = MINION_SIZE // 2
        pygame.draw.circle(surface, self.color, center, radius)
        # Draw health bar above the minion.
        health_bar_width = MINION_SIZE
        health_bar_height = 4
        health_percentage = max(self.health, 0) / MINION_HEALTH
        current_health_width = health_bar_width * health_percentage
        health_bar_rect = pygame.Rect(self.x, self.y - health_bar_height - 2, current_health_width, health_bar_height)
        border_rect = pygame.Rect(self.x, self.y - health_bar_height - 2, health_bar_width, health_bar_height)
        pygame.draw.rect(surface, RED, border_rect)
        pygame.draw.rect(surface, (0, 255, 0), health_bar_rect)


def main():
    """
    Main function to run the enhanced two-player minigame.

    In this version, two heroes—Valor (Player 1) and Nemesis (Player 2)—face off in an arena.
    They can move, attack, and produce minions to fight for them.
    Improved visuals and UI instructions are provided, and when the game is over the minions stop updating.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Arena Clash: Valor vs Nemesis")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # Define controls for each hero.
    valor_controls = {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'attack': pygame.K_SPACE,
        'produce': pygame.K_r
    }
    nemesis_controls = {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'attack': pygame.K_q,
        'produce': pygame.K_e
    }

    # Create two heroes.
    valor = Hero(100, SCREEN_HEIGHT // 2 - HERO_SIZE // 2, VALOR_COLOR, valor_controls, "Valor")
    nemesis = Hero(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - HERO_SIZE // 2, NEMESIS_COLOR, nemesis_controls, "Nemesis")

    game_over = False
    winner = None

    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                # Handle hero attacks.
                if event.key == valor.controls['attack']:
                    valor.attack(nemesis, nemesis.minions, current_time)
                if event.key == nemesis.controls['attack']:
                    nemesis.attack(valor, valor.minions, current_time)
                # Handle minion production.
                if event.key == valor.controls['produce']:
                    valor.produce_minion(nemesis, current_time)
                if event.key == nemesis.controls['produce']:
                    nemesis.produce_minion(valor, current_time)

        # Handle continuous movement.
        keys = pygame.key.get_pressed()
        if not game_over:
            valor.handle_movement(keys)
            nemesis.handle_movement(keys)

        # Update minions only if the game is not over.
        if not game_over:
            for minion in valor.minions[:]:
                minion.update(nemesis, current_time)
                if minion.health <= 0:
                    valor.minions.remove(minion)
            for minion in nemesis.minions[:]:
                minion.update(valor, current_time)
                if minion.health <= 0:
                    nemesis.minions.remove(minion)

        # Check for game over.
        if valor.health <= 0:
            game_over = True
            winner = nemesis.name
        if nemesis.health <= 0:
            game_over = True
            winner = valor.name

        # Drawing.
        draw_background(screen)
        # Draw heroes and their info.
        valor.draw(screen, font, (20, 20))
        nemesis.draw(screen, font, (SCREEN_WIDTH - 400, 20))
        # Draw minions.
        for minion in valor.minions:
            minion.draw(screen)
        for minion in nemesis.minions:
            minion.draw(screen)
        # Draw game instructions.
        draw_instructions(screen, font)

        # If game over, display winner.
        if game_over:
            game_over_text = font.render(f"Game Over! {winner} wins!", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()

# ==============================
# Pytest Unit Tests
# To run the tests, use the command: pytest arena_clash.py
# ==============================
import pytest


@pytest.mark.parametrize("point1, point2, expected", [
    ((0, 0), (3, 4), 5.0),
    ((100, 100), (100, 100), 0.0),
    ((-1, -1), (2, 3), 5.0)
])
def test_distance_between_ValidInputs_CorrectDistance(point1, point2, expected):
    """
    Test the distance_between function for correct Euclidean distance calculation.
    """
    result = distance_between(point1, point2)
    assert pytest.approx(result, rel=1e-2) == expected


@pytest.mark.parametrize("last_attack, current_time, expected", [
    (1000, 1500, True),
    (1000, 1400, False),
    (0, 0, True)
])
def test_HeroCanAttack_CooldownBehavior_Expectations(last_attack, current_time, expected):
    """
    Test the Hero.can_attack method to ensure cooldown is respected.
    """
    controls = {'up': None, 'down': None, 'left': None, 'right': None, 'attack': None, 'produce': None}
    hero = Hero(0, 0, (0, 0, 0), controls, "Test")
    hero.last_attack_time = last_attack
    assert hero.can_attack(current_time) == expected


@pytest.mark.parametrize("attacker_pos, enemy_pos, expected_attack_result", [
    ((100, 100), (130, 130), True),  # In range for hero attack.
    ((100, 100), (500, 500), False)  # Out of range.
])
def test_HeroAttack_TargetSelection_Expectations(attacker_pos, enemy_pos, expected_attack_result):
    """
    Test the Hero.attack method to check if the attack targets the correct enemy unit.
    """
    controls = {'up': None, 'down': None, 'left': None, 'right': None, 'attack': None, 'produce': None}
    attacker = Hero(attacker_pos[0], attacker_pos[1], (0, 0, 0), controls, "Attacker")
    enemy = Hero(enemy_pos[0], enemy_pos[1], (0, 0, 0), controls, "Enemy")
    # Add a dummy minion to enemy.
    enemy.minions.append(Minion(enemy_pos[0], enemy_pos[1], (0, 0, 0)))
    current_time = 3000
    result = attacker.attack(enemy, enemy.minions, current_time)
    assert result == expected_attack_result
    if expected_attack_result:
        if distance_between(attacker.get_center(), enemy.get_center()) <= ATTACK_RANGE:
            assert enemy.health == 100 - ATTACK_DAMAGE
        else:
            # If the attack hit a minion, check its health.
            assert enemy.minions[0].health == MINION_HEALTH - ATTACK_DAMAGE
    else:
        assert enemy.health == 100


@pytest.mark.parametrize("production_time, current_time, expected", [
    (0, 2500, True),  # Enough time passed.
    (0, 1500, False)  # Not enough time passed.
])
def test_HeroProduceMinion_ProductionCooldown_Expectations(production_time, current_time, expected):
    """
    Test the Hero.produce_minion method to ensure minion production respects the cooldown.
    """
    controls = {'up': None, 'down': None, 'left': None, 'right': None, 'attack': None, 'produce': None}
    hero = Hero(0, 0, (0, 0, 0), controls, "Test")
    hero.last_minion_production = production_time
    enemy = Hero(100, 100, (0, 0, 0), controls, "Enemy")
    result = hero.produce_minion(enemy, current_time)
    assert result == expected


@pytest.mark.parametrize("minion_x, minion_y, enemy_x, enemy_y, current_time, expected_enemy_health", [
    (100, 100, 150, 150, 3000, 100 - MINION_ATTACK_DAMAGE),  # In range, attack occurs.
    (100, 100, 300, 300, 3000, 100)  # Out of range, no attack.
])
def test_MinionUpdate_AttackBehavior_Expectations(minion_x, minion_y, enemy_x, enemy_y, current_time,
                                                  expected_enemy_health):
    """
    Test the Minion.update method to ensure it attacks the enemy hero when in range.
    """
    minion = Minion(minion_x, minion_y, (0, 0, 0))
    enemy = Hero(enemy_x, enemy_y, (0, 0, 0),
                 {'up': None, 'down': None, 'left': None, 'right': None, 'attack': None, 'produce': None}, "Enemy")
    enemy.health = 100
    minion.last_attack_time = current_time - MINION_ATTACK_COOLDOWN
    minion.update(enemy, current_time)
    assert enemy.health == expected_enemy_health

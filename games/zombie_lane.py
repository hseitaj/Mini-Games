#!/usr/bin/env python3
# libraries needed:
# pip install pygame
# to run in terminal: python zombie_lane.py

import pygame
import random
import sys

# Screen and lane dimensions
WIDTH = 600
HEIGHT = 800
LANE_WIDTH = 400
LANE_LEFT = (WIDTH - LANE_WIDTH) // 2
LANE_RIGHT = LANE_LEFT + LANE_WIDTH

FPS = 60

# Colors
BACKGROUND_COLOR = (30, 30, 30)    # Dark background
LANE_COLOR = (50, 50, 50)          # Lane color
PLAYER_COLOR = (0, 255, 0)         # Green player
BULLET_COLOR = (255, 255, 0)       # Yellow bullet
ZOMBIE_COLORS = [(255, 0, 0), (200, 0, 0), (255, 50, 50)]  # Different shades of red
UPGRADE_COLOR = (0, 255, 255)      # Cyan for upgrade collectibles

# Speeds and timing
PLAYER_SPEED = 5
BULLET_SPEED = 10
ZOMBIE_SPEED = 3
SCROLL_SPEED = 2  # Used for background/upgrades (simulate forward motion)
SPAWN_ZOMBIE_INTERVAL = 1500  # milliseconds between zombie spawns
SPAWN_UPGRADE_INTERVAL = 5000  # milliseconds between upgrade spawns
BULLET_COOLDOWN = 300  # ms between shots

# Gun appearance definitions by level (index 0 is level 1, etc.)
GUN_APPEARANCES = [
    {"color": (255, 255, 255), "thickness": 2},  # Level 1: white, thin line
    {"color": (0, 255, 255), "thickness": 4},      # Level 2: cyan, thicker line
    {"color": (255, 0, 255), "thickness": 6},      # Level 3: magenta, even thicker
    {"color": (255, 255, 0), "thickness": 8},      # Level 4: yellow, thick line
]
MAX_GUN_LEVEL = len(GUN_APPEARANCES)

class Player:
    """
    Represents the player in Zombie Lane.
    The player is constrained to move horizontally within the lane.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.gun_level = 0
        self.last_shot_time = 0

    def move(self, dx):
        """
        Move the player horizontally by dx pixels, constrained to the lane.
        """
        self.x += dx
        if self.x < LANE_LEFT:
            self.x = LANE_LEFT
        if self.x + self.width > LANE_RIGHT:
            self.x = LANE_RIGHT - self.width

    def shoot(self, current_time):
        """
        Shoot a bullet if cooldown allows.
        Returns a Bullet object, or None if still in cooldown.
        """
        if current_time - self.last_shot_time >= BULLET_COOLDOWN:
            self.last_shot_time = current_time
            bullet_x = self.x + self.width // 2
            bullet_y = self.y
            return Bullet(bullet_x, bullet_y, self.gun_level)
        return None

    def upgrade_gun(self):
        """
        Upgrade the player's gun by increasing its level.
        """
        if self.gun_level < MAX_GUN_LEVEL - 1:
            self.gun_level += 1

    def draw(self, screen):
        """
        Draw the player and its gun on the screen.
        """
        # Draw the player as a rectangle.
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))
        # Draw the gun as a line extending from the top-center of the player.
        gun_props = GUN_APPEARANCES[self.gun_level]
        start_pos = (self.x + self.width // 2, self.y)
        end_pos = (self.x + self.width // 2, self.y - 20)
        pygame.draw.line(screen, gun_props["color"], start_pos, end_pos, gun_props["thickness"])

class Bullet:
    """
    Represents a bullet fired by the player.
    The bullet moves upward (in the negative y direction).
    """
    def __init__(self, x, y, gun_level):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = BULLET_SPEED
        self.gun_level = gun_level

    def update(self):
        """
        Update the bullet's position.
        """
        self.y -= self.speed

    def draw(self, screen):
        """
        Draw the bullet as a circle.
        """
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), self.radius)

    def off_screen(self):
        """
        Check whether the bullet has left the screen.
        """
        return self.y < 0

class Zombie:
    """
    Represents a zombie enemy in the lane.
    Zombies move downward and have a random color from a predefined list.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.color = random.choice(ZOMBIE_COLORS)
        self.speed = ZOMBIE_SPEED

    def update(self):
        """
        Update the zombie's position.
        """
        self.y += self.speed

    def draw(self, screen):
        """
        Draw the zombie as a rectangle.
        """
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def off_screen(self):
        """
        Check if the zombie has left the screen.
        """
        return self.y > HEIGHT

class Upgrade:
    """
    Represents a gun upgrade collectible.
    Collecting an upgrade increases the player's gun level.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20

    def update(self):
        """
        Update the upgrade's position (moves downward with the background).
        """
        self.y += SCROLL_SPEED

    def draw(self, screen):
        """
        Draw the upgrade as a square.
        """
        pygame.draw.rect(screen, UPGRADE_COLOR, (self.x, self.y, self.size, self.size))

    def off_screen(self):
        """
        Check if the upgrade has left the screen.
        """
        return self.y > HEIGHT

def main():
    """
    Main game loop for Zombie Lane.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombie Lane")
    clock = pygame.time.Clock()

    # Initialize player at the bottom center of the lane.
    player = Player((LANE_LEFT + LANE_RIGHT) // 2 - 20, HEIGHT - 100)
    bullets = []
    zombies = []
    upgrades = []
    score = 0

    zombie_timer = 0
    upgrade_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement (left/right only)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-PLAYER_SPEED)
        if keys[pygame.K_RIGHT]:
            player.move(PLAYER_SPEED)
        if keys[pygame.K_SPACE]:
            bullet = player.shoot(current_time)
            if bullet:
                bullets.append(bullet)

        # Spawn zombies periodically
        if current_time - zombie_timer > SPAWN_ZOMBIE_INTERVAL:
            zombie_timer = current_time
            z_x = random.randint(LANE_LEFT, LANE_RIGHT - 30)
            z_y = -30
            zombies.append(Zombie(z_x, z_y))

        # Spawn upgrade collectibles periodically
        if current_time - upgrade_timer > SPAWN_UPGRADE_INTERVAL:
            upgrade_timer = current_time
            u_x = random.randint(LANE_LEFT, LANE_RIGHT - 20)
            u_y = -20
            upgrades.append(Upgrade(u_x, u_y))

        # Update bullets and remove if off screen
        for bullet in bullets[:]:
            bullet.update()
            if bullet.off_screen():
                bullets.remove(bullet)

        # Update zombies, check for bullet collisions and player collisions
        for zombie in zombies[:]:
            zombie.update()
            if zombie.off_screen():
                zombies.remove(zombie)
            # Collision with bullet
            for bullet in bullets[:]:
                if (zombie.x < bullet.x < zombie.x + zombie.width and
                    zombie.y < bullet.y < zombie.y + zombie.height):
                    zombies.remove(zombie)
                    bullets.remove(bullet)
                    score += 10
                    break
            # Collision with player (game over)
            if (player.x < zombie.x + zombie.width and
                player.x + player.width > zombie.x and
                player.y < zombie.y + zombie.height and
                player.y + player.height > zombie.y):
                running = False

        # Update upgrades and check if player collects them
        for upgrade in upgrades[:]:
            upgrade.update()
            if upgrade.off_screen():
                upgrades.remove(upgrade)
            if (player.x < upgrade.x + upgrade.size and
                player.x + player.width > upgrade.x and
                player.y < upgrade.y + upgrade.size and
                player.y + player.height > upgrade.y):
                player.upgrade_gun()
                upgrades.remove(upgrade)

        # Drawing section
        screen.fill(BACKGROUND_COLOR)
        # Draw lane
        pygame.draw.rect(screen, LANE_COLOR, (LANE_LEFT, 0, LANE_WIDTH, HEIGHT))
        # Draw game objects
        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)
        for upgrade in upgrades:
            upgrade.draw(screen)
        # Display score
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

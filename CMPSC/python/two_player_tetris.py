#!/usr/bin/env python3
"""
A minimal two‐player Tetris game using Pygame.

Player 1 uses:
    - Left/Right arrows to move left/right
    - Up arrow to rotate
    - Down arrow to soft drop
    - Space to hard drop

Player 2 uses:
    - A/D to move left/right
    - W to rotate
    - S to soft drop
    - Q to hard drop
"""
# libraries needed
# pip install pygame pytest
# to run it in terminal: python two_player_tetris.py

import sys
import random
import pygame

# Global constants for the game
CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
MARGIN = 20

# Define some colors.
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# List of tetromino shapes and their colors.
# Each shape is defined as a list of (x, y) coordinates.
# They will be normalized (shifted so that the minimum coordinate is (0,0)).
TETROMINO_SHAPES = [
    ([(0, 0), (1, 0), (2, 0), (3, 0)], CYAN),   # I piece
    ([(0, 0), (0, 1), (1, 1), (2, 1)], BLUE),    # J piece
    ([(2, 0), (0, 1), (1, 1), (2, 1)], ORANGE),  # L piece
    ([(1, 0), (2, 0), (1, 1), (2, 1)], YELLOW),  # O piece
    ([(1, 0), (2, 0), (0, 1), (1, 1)], GREEN),   # S piece
    ([(1, 0), (0, 1), (1, 1), (2, 1)], PURPLE),  # T piece
    ([(0, 0), (1, 0), (1, 1), (2, 1)], RED)       # Z piece
]


def normalize_shape(shape):
    """
    Normalize a tetromino shape so that its coordinates start at (0, 0).

    Args:
        shape (list of tuple of int): The list of (x, y) coordinates for the shape.

    Returns:
        list of tuple of int: The normalized shape.
    """
    min_x = min(x for x, y in shape)
    min_y = min(y for x, y in shape)
    return [(x - min_x, y - min_y) for x, y in shape]


def rotate_shape(shape):
    """
    Rotate a shape 90 degrees clockwise within its minimal bounding box.

    The function computes the minimal bounding box of the shape,
    rotates each block using (x, y) -> (y, (width-1)-x) and then normalizes
    the result so that the minimum coordinate is (0, 0).

    Args:
        shape (list of tuple of int): The list of (x, y) coordinates of the shape.

    Returns:
        list of tuple of int: The rotated shape.
    """
    if not shape:
        return shape
    max_x = max(x for x, y in shape)
    w = max_x + 1
    # Rotate each block.
    new_shape = [(y, (w - 1 - x)) for x, y in shape]
    # Normalize the new shape so that its smallest coordinate is (0, 0).
    min_x = min(x for x, y in new_shape)
    min_y = min(y for x, y in new_shape)
    new_shape = [(x - min_x, y - min_y) for x, y in new_shape]
    return new_shape


class Tetromino:
    """
    Class representing a tetromino piece.
    """

    def __init__(self, shape, color):
        """
        Initialize a tetromino.

        Args:
            shape (list of tuple of int): The list of (x, y) coordinates for the tetromino.
            color (tuple of int): The RGB color of the tetromino.
        """
        self.shape = shape
        self.color = color

    def get_rotated_shape(self):
        """
        Get the shape rotated 90 degrees clockwise.

        Returns:
            list of tuple of int: The rotated shape.
        """
        return rotate_shape(self.shape)


class TetrisBoard:
    """
    Class representing a Tetris board.
    """

    def __init__(self, width, height, drop_interval=500):
        """
        Initialize a Tetris board.

        Args:
            width (int): The width (number of cells) of the board.
            height (int): The height (number of cells) of the board.
            drop_interval (int, optional): Milliseconds between automatic drops. Defaults to 500.
        """
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.drop_interval = drop_interval  # milliseconds
        self.drop_timer = 0
        self.game_over = False
        self.score = 0
        self.spawn_piece()

    def get_piece_width(self, shape):
        """
        Get the width of a tetromino shape.

        Args:
            shape (list of tuple of int): The tetromino shape coordinates.

        Returns:
            int: The width in cells.
        """
        return max(x for x, y in shape) + 1

    def can_move(self, shape, x, y):
        """
        Check if a piece with a given shape can be placed at the given board position.

        Args:
            shape (list of tuple of int): The tetromino shape.
            x (int): The x-coordinate (cell) on the board.
            y (int): The y-coordinate (cell) on the board.

        Returns:
            bool: True if the piece can be placed, False otherwise.
        """
        for block in shape:
            new_x = x + block[0]
            new_y = y + block[1]
            # Check board boundaries.
            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                return False
            # Check if the grid cell is already occupied.
            if self.grid[new_y][new_x] is not None:
                return False
        return True

    def spawn_piece(self):
        """
        Spawn a new tetromino piece at the top of the board.
        If the new piece cannot be placed, mark the board as game over.
        """
        shape, color = random.choice(TETROMINO_SHAPES)
        shape = normalize_shape(shape)
        self.current_piece = Tetromino(shape, color)
        self.current_x = (self.width - self.get_piece_width(self.current_piece.shape)) // 2
        self.current_y = 0
        if not self.can_move(self.current_piece.shape, self.current_x, self.current_y):
            self.game_over = True

    def move_piece(self, dx, dy):
        """
        Attempt to move the current piece by (dx, dy).

        Args:
            dx (int): Change in the x-direction.
            dy (int): Change in the y-direction.

        Returns:
            bool: True if the piece was moved, False otherwise.
        """
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if self.can_move(self.current_piece.shape, new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False

    def rotate_piece(self):
        """
        Attempt to rotate the current piece.

        Returns:
            bool: True if rotation succeeded, False otherwise.
        """
        new_shape = self.current_piece.get_rotated_shape()
        if self.can_move(new_shape, self.current_x, self.current_y):
            self.current_piece.shape = new_shape
            return True
        return False

    def drop_piece(self):
        """
        Drop the current piece by one row.
        If the piece cannot move down, lock it in place.
        """
        if not self.move_piece(0, 1):
            self.lock_piece()

    def hard_drop(self):
        """
        Hard drop the current piece to the lowest possible position.
        """
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        """
        Lock the current piece in place and update the board grid.
        Then clear any full lines and spawn a new piece.
        """
        for block in self.current_piece.shape:
            x = self.current_x + block[0]
            y = self.current_y + block[1]
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """
        Check for and clear completed lines on the board.
        Increase the score by the number of lines cleared.
        """
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = self.height - len(new_grid)
        for _ in range(lines_cleared):
            new_grid.insert(0, [None for _ in range(self.width)])
        self.grid = new_grid
        self.score += lines_cleared

    def update(self, dt):
        """
        Update the board's state based on the elapsed time.

        Args:
            dt (int): Milliseconds elapsed since the last update.
        """
        self.drop_timer += dt
        if self.drop_timer > self.drop_interval:
            self.drop_timer = 0
            if not self.game_over:
                self.drop_piece()

    def draw(self, surface, offset_x, offset_y):
        """
        Draw the board grid and the current piece on a given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            offset_x (int): The x-offset (in pixels) to draw the board.
            offset_y (int): The y-offset (in pixels) to draw the board.
        """
        # Draw the fixed blocks.
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                rect = pygame.Rect(offset_x + x * CELL_SIZE,
                                   offset_y + y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                if cell is None:
                    pygame.draw.rect(surface, GRAY, rect, 1)
                else:
                    pygame.draw.rect(surface, cell, rect)
        # Draw the current falling piece.
        if not self.game_over:
            for block in self.current_piece.shape:
                x = self.current_x + block[0]
                y = self.current_y + block[1]
                if y >= 0:
                    rect = pygame.Rect(offset_x + x * CELL_SIZE,
                                       offset_y + y * CELL_SIZE,
                                       CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, self.current_piece.color, rect)
        # Draw "Game Over" text if needed.
        if self.game_over:
            font = pygame.font.SysFont("Arial", 24)
            text = font.render("Game Over", True, RED)
            surface.blit(text, (offset_x + 10, offset_y + self.height * CELL_SIZE // 2))


def main():
    """
    The main function to run the two-player Tetris game.
    """
    pygame.init()
    # Calculate the screen size for two boards with margins.
    screen_width = BOARD_WIDTH * CELL_SIZE * 2 + MARGIN * 3
    screen_height = BOARD_HEIGHT * CELL_SIZE + MARGIN * 2
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Two-Player Tetris")
    clock = pygame.time.Clock()

    # Create two Tetris boards.
    board1 = TetrisBoard(BOARD_WIDTH, BOARD_HEIGHT)
    board2 = TetrisBoard(BOARD_WIDTH, BOARD_HEIGHT)

    running = True
    while running:
        dt = clock.tick(60)  # milliseconds since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # --- Player 1 Controls (Arrow keys + Space) ---
                if event.key == pygame.K_LEFT:
                    board1.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    board1.move_piece(1, 0)
                elif event.key == pygame.K_UP:
                    board1.rotate_piece()
                elif event.key == pygame.K_DOWN:
                    board1.move_piece(0, 1)
                elif event.key == pygame.K_SPACE:
                    board1.hard_drop()
                # --- Player 2 Controls (WASD + Q) ---
                elif event.key == pygame.K_a:
                    board2.move_piece(-1, 0)
                elif event.key == pygame.K_d:
                    board2.move_piece(1, 0)
                elif event.key == pygame.K_w:
                    board2.rotate_piece()
                elif event.key == pygame.K_s:
                    board2.move_piece(0, 1)
                elif event.key == pygame.K_q:
                    board2.hard_drop()

        # Update both boards.
        board1.update(dt)
        board2.update(dt)

        # Draw the boards.
        screen.fill(BLACK)
        board1.draw(screen, MARGIN, MARGIN)
        board2.draw(screen, BOARD_WIDTH * CELL_SIZE + MARGIN * 2, MARGIN)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()


# ==============================
# Pytest Unit Tests
# To run the tests, run: pytest <this_file.py>
# ==============================
import pytest

@pytest.mark.parametrize("input_shape, expected_output", [
    # I piece horizontal becomes vertical after rotation.
    ([(0, 0), (1, 0), (2, 0), (3, 0)],
     [(0, 0), (0, 1), (0, 2), (0, 3)]),
    # J piece: [(0,0),(0,1),(1,1),(2,1)] rotates to [(1,0),(1,1),(1,2),(0,2)] (order may vary).
    ([(0, 0), (0, 1), (1, 1), (2, 1)],
     [(1, 0), (1, 1), (1, 2), (0, 2)]),
])
def test_rotate_shape(input_shape, expected_output):
    """
    Test the rotate_shape function with various input shapes.
    """
    rotated = rotate_shape(input_shape)
    # Sorting since the order of blocks does not matter.
    assert sorted(rotated) == sorted(expected_output)


@pytest.mark.parametrize("input_shape, expected_output", [
    # Normalize a shape that does not start at (0,0).
    ([(1, 0), (2, 0), (1, 1), (2, 1)],
     [(0, 0), (1, 0), (0, 1), (1, 1)]),
    ([(2, 1), (3, 1), (2, 2), (3, 2)],
     [(0, 0), (1, 0), (0, 1), (1, 1)]),
])
def test_normalize_shape(input_shape, expected_output):
    """
    Test the normalize_shape function.
    """
    normalized = normalize_shape(input_shape)
    assert sorted(normalized) == sorted(expected_output)


@pytest.mark.parametrize("shape, x, y, expected", [
    ([(0, 0)], 0, 0, True),
    ([(0, 0)], -1, 0, False),
    ([(0, 0)], BOARD_WIDTH, 0, False),
    ([(0, 0)], 0, BOARD_HEIGHT, False),
])
def test_can_move(shape, x, y, expected):
    """
    Test the TetrisBoard.can_move method for various positions.
    """
    board = TetrisBoard(BOARD_WIDTH, BOARD_HEIGHT)
    # Clear the board grid.
    board.grid = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    result = board.can_move(shape, x, y)
    assert result == expected

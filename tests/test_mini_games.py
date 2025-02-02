import sys
import os
# Ensure the repository root is in sys.path so the games package is discoverable.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import pytest

# Import for Arena Clash tests
from games.arena_clash import (
    Hero,
    Minion,
    distance_between,
    ATTACK_RANGE,
    ATTACK_DAMAGE,
    MINION_ATTACK_DAMAGE,
    MINION_ATTACK_COOLDOWN,
    MINION_HEALTH
)

# Import for Two-Player Tetris tests
from games.two_player_tetris import (
    rotate_shape,
    normalize_shape,
    TetrisBoard,
    BOARD_WIDTH,
    BOARD_HEIGHT
)

# ==============================
# Arena Clash Tests
# ==============================

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
    (0, 0, False)  # With no elapsed time, cooldown is not met.
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
    ((100, 100), (500, 500), False)   # Out of range.
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
        # If the enemy hero is within attack range, its health should decrease.
        if distance_between(attacker.get_center(), enemy.get_center()) <= ATTACK_RANGE:
            assert enemy.health == 100 - ATTACK_DAMAGE
        else:
            # Otherwise, if a minion was attacked, its health should be reduced.
            assert enemy.minions[0].health == MINION_HEALTH - ATTACK_DAMAGE
    else:
        assert enemy.health == 100


@pytest.mark.parametrize("production_time, current_time, expected", [
    (0, 2500, True),   # Enough time passed.
    (0, 1500, False)   # Not enough time passed.
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
    # In-range test: enemy is positioned so that the centers are within MINION_ATTACK_RANGE.
    (100, 100, 110, 110, 3000, 100 - MINION_ATTACK_DAMAGE),
    # Out-of-range test.
    (100, 100, 300, 300, 3000, 100)
])
def test_MinionUpdate_AttackBehavior_Expectations(minion_x, minion_y, enemy_x, enemy_y, current_time, expected_enemy_health):
    """
    Test the Minion.update method to ensure it attacks the enemy hero when in range.
    """
    minion = Minion(minion_x, minion_y, (0, 0, 0))
    enemy = Hero(enemy_x, enemy_y, (0, 0, 0),
                 {'up': None, 'down': None, 'left': None, 'right': None, 'attack': None, 'produce': None}, "Enemy")
    enemy.health = 100
    # Set last attack time such that the minion is allowed to attack.
    minion.last_attack_time = current_time - MINION_ATTACK_COOLDOWN
    minion.update(enemy, current_time)
    assert enemy.health == expected_enemy_health


# ==============================
# Two-Player Tetris Tests
# ==============================

@pytest.mark.parametrize("input_shape, expected_output", [
    ([(0, 0), (1, 0), (2, 0), (3, 0)],
     [(0, 0), (0, 1), (0, 2), (0, 3)]),
    ([(0, 0), (0, 1), (1, 1), (2, 1)],
     [(1, 0), (1, 1), (1, 2), (0, 2)])
])
def test_rotate_shape(input_shape, expected_output):
    """
    Test the rotate_shape function with various input shapes.
    """
    rotated = rotate_shape(input_shape)
    assert sorted(rotated) == sorted(expected_output)


@pytest.mark.parametrize("input_shape, expected_output", [
    ([(1, 0), (2, 0), (1, 1), (2, 1)],
     [(0, 0), (1, 0), (0, 1), (1, 1)]),
    ([(2, 1), (3, 1), (2, 2), (3, 2)],
     [(0, 0), (1, 0), (0, 1), (1, 1)])
])
def test_normalize_shape(input_shape, expected_output):
    """
    Test the normalize_shape function.
    """
    normalized = normalize_shape(input_shape)
    assert sorted(normalized) == sorted(expected_output)


@pytest.mark.parametrize("input_shape, x, y, expected", [
    ([(0, 0)], 0, 0, True),
    ([(0, 0)], -1, 0, False),
    ([(0, 0)], BOARD_WIDTH, 0, False),
    ([(0, 0)], 0, BOARD_HEIGHT, False),
])
def test_TetrisBoard_can_move(input_shape, x, y, expected):
    """
    Test the TetrisBoard.can_move method for various positions.
    """
    board = TetrisBoard(BOARD_WIDTH, BOARD_HEIGHT)
    # Clear the board grid.
    board.grid = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    result = board.can_move(input_shape, x, y)
    assert result == expected

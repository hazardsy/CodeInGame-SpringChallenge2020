import copy
import math
import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# TODO : Use better choice than random if all possibilities are equal
# TODO : Ajust diffusing numbers
# TODO : Move pacs one by one starting with the one with better move and adjusts scores based on that
# TODO : Deal with late game
# TODO : What to do when pacs see nothing ?
# TODO : Diffuse every cell but change their value depending on last known information
# TODO : Increase diffuse range for every pac based on time since last pellet eaten
# TODO : Better spells usage :D
# IDEA : Adjust diffuse parameters based on remaining pellets ?
# IDEA : Adjust diffuse parameters based on number of neighbors ?
# IDEA : Adjust agressivity of pacs based on state of the game ?
# ==========================Constants==============================
WINNERS_AGAINST: Dict = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}
# ==========================Utils==================================
def is_my_pac_winning(my_type: Optional[str], foe_type: Optional[str]) -> bool:
    return WINNERS_AGAINST.get("foe_type") == my_type


def get_neighbors(
    coords: Tuple[int, int], width: int, height: int
) -> List[Tuple[int, int]]:
    return [
        ((coords[0] - 1) % width, coords[1]),
        ((coords[0] + 1) % width, coords[1]),
        (coords[0], (coords[1] - 1) % height),
        (coords[0], (coords[1] + 1) % height),
    ]


def log_err(mess: Any):
    print(mess, file=sys.stderr)


def get_action(pac: Dict) -> str:
    if pac.get("cooldown", 1) < 1:
        return f"SPEED {pac.get('id')}"
    return f"MOVE {pac.get('id')} {pac.get('target', {}).get('x')} {pac.get('target', {}).get('y')}"


def diffuse(
    cells: Dict,
    starting_point: Optional[Tuple[int, int]],
    starting_value: float,
    decaying_factor: float,
    eta: float,
) -> Dict:
    current_value: float = starting_value
    visited_cells: List[Optional[Tuple[int, int]]] = []

    neighbors: List[Optional[Tuple[int, int]]] = [starting_point]
    while abs(current_value) > eta:
        next_neighbors: List[Optional[Tuple[int, int]]] = []
        for neighbor in neighbors:
            cells[neighbor]["value"] += current_value
            visited_cells.append(neighbor)
            next_neighbors.extend(
                [
                    n
                    for n in cells.get(neighbor, {}).get("neighbors", [])
                    if n not in visited_cells and n not in next_neighbors
                ]
            )
        current_value = round(current_value * decaying_factor, 2)
        neighbors = next_neighbors
    return cells


# ==========================Game===================================

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
cells: Dict = {}

for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall
    for x_ind, char in enumerate(row):
        if char != "#":
            cells[(x_ind, i)] = {"value": 0, "neighbors": [], "x": x_ind, "y": i}

# Populate neighbors
for coord in cells.keys():
    cells[coord].get("neighbors").extend(
        [
            neighbor
            for neighbor in get_neighbors(coord, width, height)
            if cells.get(neighbor)
        ]
    )

# game loop
while True:
    current_turn_cells: Dict = copy.deepcopy(cells)

    my_score, opponent_score = [int(j) for j in input().split()]
    visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
    pacs: List[Dict] = []
    for i in range(visible_pac_count):
        # pac_id: pac number (unique within a team)
        # mine: true if this pac is yours
        # x: position in the grid
        # y: position in the grid
        # type_id: unused in wood leagues
        # speed_turns_left: unused in wood leagues
        # ability_cooldown: unused in wood leagues
        (id, mine, x, y, type_id, speed_turns_left, ability_cooldown,) = input().split()

        pacs.append(
            {
                "coordinates": (int(x), int(y)),
                "id": int(id),
                "mine": mine != "0",
                "shape": type_id,
                "cooldown": int(ability_cooldown),
            }
        )

    visible_pellet_count = int(input())  # all pellets in sight

    # Diffuse pellet values
    for i in range(visible_pellet_count):
        # value: amount of points this pellet is worth
        int_x, int_y, value = [int(j) for j in input().split()]
        current_turn_cells = diffuse(
            current_turn_cells, (int_x, int_y), value, 0.9, 0.6 if value == 1 else 1
        )

    # Diffuse pacs values
    for pac in [p for p in pacs if p.get("mine")]:
        current_turn_cells = diffuse(
            current_turn_cells, pac.get("coordinates", (0, 0)), -10, 0.9, 1
        )

    action: str = ""
    for pac in [p for p in pacs if p.get("mine")]:
        current_pac_cells: Dict = copy.deepcopy(current_turn_cells)
        for foe_pac in [p for p in pacs if not p.get("mine")]:
            current_pac_cells = diffuse(
                current_pac_cells,
                pac.get("coordinates"),
                10
                if is_my_pac_winning(pac.get("shape"), foe_pac.get("shape"))
                else -10,
                0.9,
                1,
            )

        neighbors: List[Dict] = [
            current_turn_cells.get(coords, {})
            for coords in get_neighbors(
                pac.get("coordinates", (0, 0)), width=width, height=height
            )
            if current_turn_cells.get(coords)
        ]
        random.shuffle(neighbors)
        pac["target"] = max(neighbors, key=lambda x: x.get("value"))

        action += f"{get_action(pac)} |"

        log_err(pac)
        log_err(neighbors)

    print(action)

import copy
import math
import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# TODO : Store every visited position and diffuse negatively depending on age
# TODO : Diffuse big pellets on n_iter depending on map size
# TODO : Increase diffuse range if pellets are in vision but every score is 0
# TODO : Ajust diffusing numbers
# TODO : Move pacs one by one starting with the one with better move and adjusts scores based on that
# TODO : Deal with late game
# TODO : What to do when pacs see nothing ?
# TODO : Diffuse every cell but change their value depending on last known information
# TODO : Increase diffuse range for every pac based on time since last pellet eaten
# TODO : Better spells usage :D
# IDEA : Never target an already targetted position
# IDEA : Adjust diffuse parameters based on remaining pellets ?
# IDEA : Adjust diffuse parameters based on number of neighbors ?
# IDEA : Adjust agressivity of pacs based on state of the game ?
# IDEA : Use better choice than random if all possibilities are equal
# ==========================Constants==============================
WINNERS_AGAINST: Dict = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}
# ==========================Utils==================================
def is_my_pac_winning(my_type: Optional[str], foe_type: Optional[str]) -> bool:
    return WINNERS_AGAINST.get("foe_type") == my_type


def get_adjacents(
    coords: Tuple[int, int], width: int, height: int
) -> List[Tuple[int, int]]:
    return [
        ((coords[0] - 1) % width, coords[1]),
        ((coords[0] + 1) % width, coords[1]),
        (coords[0], (coords[1] - 1) % height),
        (coords[0], (coords[1] + 1) % height),
    ]


def get_action(pac: Dict) -> str:
    if pac.get("cooldown", 1) < 1:
        return f"SPEED {pac.get('id')}"
    return f"MOVE {pac.get('id')} {pac.get('target', {}).get('x')} {pac.get('target', {}).get('y')}"


def diffuse(
    cells: Dict,
    starting_point: Optional[Tuple[int, int]],
    starting_value: float,
    decaying_factor: float,
    max_iter: int = 10,
) -> Dict:
    current_value: float = starting_value
    visited_cells: List[Optional[Tuple[int, int]]] = []

    neighbors: List[Optional[Tuple[int, int]]] = [starting_point]
    _iter = 0
    while _iter < max_iter:
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
        _iter += 1
    return cells


# ==========================Game===================================
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
            for neighbor in get_adjacents(coord, width, height)
            if cells.get(neighbor)
        ]
    )

pacs: Dict[str, Dict[str, Dict]] = {"mine": {}, "foe": {}}

while True:
    current_turn_cells: Dict = copy.deepcopy(cells)

    my_score, opponent_score = [int(j) for j in input().split()]
    visible_pac_count = int(input())
    for i in range(visible_pac_count):
        (id, mine, x, y, type_id, speed_turns_left, ability_cooldown,) = input().split()

        last_coordinates = pacs.get("mine", {}).get(id, {}).get("coordinates")

        pacs["mine" if mine != "0" else "foe"].update(
            {
                id: {
                    "coordinates": (int(x), int(y)),
                    "id": int(id),
                    "mine": mine != "0",
                    "shape": type_id,
                    "cooldown": int(ability_cooldown),
                    "speed_turns_left": int(speed_turns_left),
                    "last_position": last_coordinates,
                }
            }
        )

    print(pacs, file=sys.stderr)
    visible_pellet_count = int(input())

    # Diffuse pellet values
    for i in range(visible_pellet_count):
        int_x, int_y, value = [int(j) for j in input().split()]
        current_turn_cells = diffuse(current_turn_cells, (int_x, int_y), value, 0.5,)

    action: str = ""
    for pac in [p for p in pacs.get("mine", {}).values()]:
        current_pac_cells: Dict = copy.deepcopy(current_turn_cells)

        # TODO : Refactor using a single loop and a method for getting diffuse value
        # Diffuse friendly pacs values
        for friend_pac in [
            p for id, p in pacs.get("mine", {}).items() if id != pac.get("id")
        ]:
            current_pac_cells = diffuse(
                current_pac_cells, friend_pac.get("coordinates", (0, 0)), -10, 0.75,
            )

        # Diffuse foe pacs values
        for foe_pac in [p for p in pacs.get("foe", {}).values()]:
            current_pac_cells = diffuse(
                current_pac_cells,
                foe_pac.get("coordinates"),
                100
                if is_my_pac_winning(pac.get("shape"), foe_pac.get("shape"))
                else -100,
                0.1,
                max_iter=3,
            )

        if pac.get("last_position"):
            # Diffuse last position
            current_pac_cells = diffuse(
                current_pac_cells, pac.get("last_position"), -100, 0.1, max_iter=2
            )

        # First order neighbors
        neighbors: List[Dict] = [
            current_pac_cells.get(coords, {})
            for coords in get_adjacents(
                pac.get("coordinates", (0, 0)), width=width, height=height
            )
            if current_pac_cells.get(coords)
        ]

        # Pac is speeding, get the best neighbor's neighbor
        if pac.get("speed_turns_left", 0) > 0:
            neighbors = [
                current_pac_cells.get(coords, {})
                for neighbor in neighbors
                for coords in get_adjacents(
                    (neighbor.get("x", 0), neighbor.get("y", 0)),
                    width=width,
                    height=height,
                )
                if current_pac_cells.get(coords)
                and coords != pac.get("coordinates", (0, 0))
            ]

        best_cells = sorted(neighbors, key=lambda x: x.get("value"), reverse=True)
        pac["target"] = best_cells[0]

        action += f"{get_action(pac)} |"

        print(pac, file=sys.stderr)
        print(best_cells[:2], file=sys.stderr)

    print(action)

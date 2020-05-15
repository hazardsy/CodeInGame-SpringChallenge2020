import copy
import math
import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# BIG TODO :
# At startup : consider each cell as full
# For each cell, store age since last seen and diffuse value based on this
# Only update cells value based on which are seen
# Modify diffuse values based on numbers of step already done in the game
# Diffuse all pacs the same, only values change
# Diffuse previous and current coordinates for all pacs except current

# TODO : Refactor diffusing parameters
# TODO : Increase diffuse range if pellets are in vision but every score is 0
# TODO : Consider any unseen coordinate as containing a pellet and diffuse them. Update as the game goes.
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


def manhattan_distance(A: Tuple[int, ...], B: Tuple[int, ...]) -> int:
    return sum([abs(B[i] - A[i]) for i in range(len(A))])


def get_pac_id(mine: str, id: str) -> str:
    return f"{mine}{id}"


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


def get_diffuse_params(cur_pac: Dict, other_pac: Dict) -> Dict:
    if other_pac.get("mine"):
        return {"starting_value": -10, "decaying_factor": 0.75, "max_iter": 10}
    if is_my_pac_winning(cur_pac.get("shape"), other_pac.get("shape")):
        return {"starting_value": 100, "decaying_factor": 0.1, "max_iter": 3}
    else:
        return {"starting_value": -100, "decaying_factor": 0.1, "max_iter": 3}


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
            cells[(x_ind, i)] = {
                "value": 0,
                "neighbors": [],
                "x": x_ind,
                "y": i,
                "visible": [],
                "last_seen": 0,
            }


for coord, cell in cells.items():
    # Populate neighbors
    cell.get("neighbors").extend(
        [
            neighbor
            for neighbor in get_adjacents(coord, width, height)
            if cells.get(neighbor)
        ]
    )

    # Populate visible cells
    base_x, base_y = cell.get("x"), cell.get("y")

    # Going left
    for cur_x in range(base_x - 1, 0, -1):
        if not cells.get((cur_x, base_y)):
            break
        cell.get("visible").append((cur_x, base_y))

    # Going right
    for cur_x in range(base_x + 1, width):
        if not cells.get((cur_x, base_y)):
            break
        cell.get("visible").append((cur_x, base_y))

    # Going up
    for cur_y in range(base_y - 1, 0, -1):
        if not cells.get((base_x, cur_y)):
            break
        cell.get("visible").append((base_x, cur_y))

    # Going down
    for cur_y in range(base_y + 1, height):
        if not cells.get((base_x, cur_y)):
            break
        cell.get("visible").append((base_x, cur_y))

pacs: Dict[str, Dict] = {}

while True:
    # start_time = time.time()
    current_turn_cells: Dict = copy.deepcopy(cells)

    my_score, opponent_score = [int(j) for j in input().split()]

    # parsing_start_time = time.time()
    visible_pac_count = int(input())
    for i in range(visible_pac_count):
        (id, mine, x, y, type_id, speed_turns_left, ability_cooldown,) = input().split()

        previous_pos: List[Dict] = pacs.get(get_pac_id(mine, id), {}).get(
            "previous_pos", []
        )
        for prev in previous_pos:
            prev["age"] += 1

        if not pacs.get(get_pac_id(mine, id)):
            pacs[get_pac_id(mine, id)] = {}

        prev_coords: Optional[Tuple[int, int]] = pacs.get(get_pac_id(mine, id), {}).get(
            "coordinates"
        )

        if prev_coords:
            previous_pos.append({"coordinates": prev_coords, "age": 0})

        pacs[get_pac_id(mine, id)].update(
            {
                "coordinates": (int(x), int(y)),
                "id": int(id),
                "mine": mine != "0",
                "shape": type_id,
                "cooldown": int(ability_cooldown),
                "speed_turns_left": int(speed_turns_left),
                "previous_pos": previous_pos,
            }
        )

    # print(f"Parsing time : {time.time() - parsing_start_time}", file=sys.stderr)

    visible_pellet_count = int(input())

    # pellet_start_time = time.time()
    small_pellets: List[Tuple[int, int]] = []
    # Diffuse big pellets values
    for i in range(visible_pellet_count):
        int_x, int_y, value = [int(j) for j in input().split()]
        if value == 10:
            current_turn_cells = diffuse(
                current_turn_cells,
                (int_x, int_y),
                value,
                0.9,
                max_iter=(max(width, height) - 2) // 2,
            )
        else:
            small_pellets.append((int_x, int_y))

    # print(
    #     f"Diffusing big pellets values : {time.time() - pellet_start_time}",
    #     file=sys.stderr,
    # )

    action: str = ""
    for pac in [p for p in pacs.values() if p.get("mine")]:
        current_pac_cells: Dict = copy.deepcopy(current_turn_cells)

        # sp_time = time.time()
        # Diffuse all visible small pellets
        visible_pellets = [
            pel
            for pel in small_pellets
            if pel
            in current_pac_cells.get(pac.get("coordinates"), (0, 0)).get("visible")
        ]
        for pel in visible_pellets:
            current_pac_cells = diffuse(
                current_pac_cells,
                pel,
                1,
                0.75,
                manhattan_distance(pac.get("coordinates", (0, 0)), pel),
            )
        # print(f"Diffusing small pellets : {time.time() - sp_time}", file=sys.stderr)

        # diffusing_pacs_time = time.time()
        # Diffuse all other pacs
        for other_pac in [p for p in pacs.values() if p != pac]:
            current_pac_cells = diffuse(
                current_pac_cells,
                other_pac.get("coordinates", (0, 0)),
                **get_diffuse_params(pac, other_pac),
            )
        # print(f"Diffusing pacs : {time.time() - diffusing_pacs_time}", file=sys.stderr)

        # diffusing_pos_time = time.time()
        # Diffuse all previous positions based on their age
        for prev in pac.get("previous_pos", []):
            current_pac_cells = diffuse(
                current_pac_cells,
                prev.get("coordinates"),
                -100 * (0.8 ** prev.get("age", 0)),
                0.1,
                max_iter=1,
            )
        # print(
        #     f"Diffusing previous pos : {time.time() - diffusing_pos_time}",
        #     file=sys.stderr,
        # )

        # target_time = time.time()
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
            dist_two_neighbors = [
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
            neighbors = [*neighbors, *dist_two_neighbors]

        best_cells = sorted(neighbors, key=lambda x: x.get("value"), reverse=True)
        pac["target"] = best_cells[0]

        action += f"{get_action(pac)} |"
        # print(f"Selecting target time : {time.time() - target_time}", file=sys.stderr)

        print(pac, file=sys.stderr)
        print(best_cells[:2], file=sys.stderr)
    # print(time.time() - start_time, file=sys.stderr)

    print(action)

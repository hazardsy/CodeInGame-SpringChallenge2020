import math
import sys
from typing import Dict, List, Optional, Tuple


# ==========================Classes==========================
class Pac(object):
    def __init__(self, x: int, y: int, id: int):
        self.coordinates: Tuple[int, int] = (x, y)
        self.id = id
        self.target: Optional[Dict] = None

    def get_action(self):
        return (
            f"MOVE {self.id} {self.target.coordinates[0]} {self.target.coordinates[1]}"
        )


# ==========================Utils==================================


def get_neighbors(
    coords: Tuple[int, int], width: int, height: int
) -> List[Tuple[int, int]]:
    return [
        ((coords[0] - 1) % width, coords[1]),
        ((coords[0] + 1) % width, coords[1]),
        (coords[0], (coords[1] - 1) % height),
        (coords[0], (coords[1] + 1) % height),
    ]


# ==========================Game===================================

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
cells: Dict = {}

for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall
    for x_ind, char in enumerate(row):
        if char != "#":
            cells[(x_ind, i)] = {"value": 1, "neighbors": [], "coordinates": (x_ind, i)}

# Populate neighbors
# TODO : optimize symmetry
for x, y in cells.keys():
    for target_x in [(x - 1) % width, (x + 1) % width]:
        if cells.get((target_x, y)):
            cells[(x, y)].get("neighbors").append((target_x, y))
    for target_y in [(y - 1) % height, (y + 1) % height]:
        if cells.get((x, target_y)):
            cells[(x, y)].get("neighbors").append((x, target_y))

# game loop
while True:
    my_score, opponent_score = [int(i) for i in input().split()]
    visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
    my_pacs: List[Pac] = []
    for i in range(visible_pac_count):
        # pac_id: pac number (unique within a team)
        # mine: true if this pac is yours
        # x: position in the grid
        # y: position in the grid
        # type_id: unused in wood leagues
        # speed_turns_left: unused in wood leagues
        # ability_cooldown: unused in wood leagues
        (id, mine, x, y, type_id, speed_turns_left, ability_cooldown,) = input().split()
        pac_id = int(id)
        bool_mine = mine != "0"
        int_x = int(x)
        int_y = int(y)
        int_speed_turns_left = int(speed_turns_left)
        int_ability_cooldown = int(ability_cooldown)

        if bool_mine:
            my_pacs.append(Pac(int_x, int_y, pac_id))

    visible_pellet_count = int(input())  # all pellets in sight

    action: str = ""
    for pac in my_pacs:
        neighbors: List[Dict] = [
            cells.get(coords, {})
            for coords in get_neighbors(pac.coordinates, width=width, height=height)
            if cells.get(coords)
        ]

        pac.target = max(neighbors, key=lambda x: x.get("value")).get("coordinates")

        action += f"{pac.get_action()} |"

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # MOVE <pacId> <x> <y>
    print(action)

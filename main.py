import sys
import math
from typing import Tuple, List, Optional

# Classes
class Pellet(object):
    def __init__(self, x: int, y: int, value: int):
        self.coordinates: Tuple[int, int] = (x, y)
        self.value = value


class Pac(object):
    def __init__(self, x: int, y: int, id: int):
        self.coordinates: Tuple[int, int] = (x, y)
        self.id = id
        self.target: Optional[Pellet] = None

    def get_action(self):
        return (
            f"MOVE {self.id} {self.target.coordinates[0]} {self.target.coordinates[1]}"
        )


# Utils
def get_manhattan(pac: Pac, pellet: Pellet) -> int:
    return sum(
        [
            abs(pac.coordinates[i] - pellet.coordinates[i])
            for i in range(len(pac.coordinates))
        ]
    )


def get_closest_pellet(pac: Pac, pellets: List[Pellet]) -> Pellet:
    return sorted(pellets, key=lambda pel: get_manhattan(pac, pel))[0]


# Game

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall

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

    pellets: List[Pellet] = []
    for i in range(visible_pellet_count):
        # value: amount of points this pellet is worth
        int_x, int_y, value = [int(j) for j in input().split()]
        pellets.append(Pellet(int_x, int_y, value))

    sps: List[Pellet] = [p for p in pellets if p.value == 10]
    non_sps: List[Pellet] = [p for p in pellets if p.value != 10]

    action: str = ""
    for pac in my_pacs:
        if len(sps) > 0:
            pac.target = get_closest_pellet(pac, sps)
        else:
            pac.target = get_closest_pellet(pac, non_sps)

        action += f"{pac.get_action()} |"

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # MOVE <pacId> <x> <y>
    print(action)

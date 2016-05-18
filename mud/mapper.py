import math


class Map(object):
    def __init__(self, grid):
        self.grid = grid

    def echo_to_actor(self, actor):
        for row in reversed(self.grid):
            line = ''.join(row)

            actor.echo(line)

class Mapper(object):
    @classmethod
    def generate_map(self, room, actor=None, width=60, height=20, legend=False):
        INITIAL_CELL_VALUE = " "

        grid = []

        for y in xrange(0, height):
            grid.append([])
            for x in xrange(0, width):
                grid[y].append(INITIAL_CELL_VALUE)

        max_x = width - 1
        max_y = height - 1

        def coord_is_invalid(x, y):
            if x < 0 or y < 0 or x > max_x or y > max_y:
                return True
            return grid[y][x] != INITIAL_CELL_VALUE

        middle_x = int(width / 2)
        middle_y = int(height / 2)

        seen_ids = []

        # From the middle, go outward until you've reached the extremities
        # Fill grid with room objects, and go up/down one level
        # Once you've filled the grid, format it to symbols and add legend
        stack = [
            (middle_x, middle_y, room),
        ]

        DIRECTIONS = [
            {
                "id": "north",
                "coords": (0, 2),
                "connector_coords": (0, 1),
                "connector_symbol": "{8|{x",
                "continue": True,
            },
            {
                "id": "east",
                "coords": (2, 0),
                "connector_coords": (1, 0),
                "connector_symbol": "{8-{x",
                "continue": True,
            },
            {
                "id": "south",
                "coords": (0, -2),
                "connector_coords": (0, -1),
                "connector_symbol": "{8|{x",
                "continue": True,
            },
            {
                "id": "west",
                "coords": (-2, 0),
                "connector_coords": (-1, 0),
                "connector_symbol": "{8-{x",
                "continue": True,
            },
            {
                "id": "up",
                "connector_coords": (1, 1),
                "connector_symbol": "{Y,{x",
                "continue": False,
            },
            {
                "id": "down",
                "connector_coords": (-1, -1),
                "connector_symbol": "{y'{x",
                "continue": False,
            },
        ]

        max_count = width * height
        while len(stack):

            entry = stack.pop(0)

            current_x, current_y, current_room = entry

            # FIXME use symbols appropriately
            grid[current_y][current_x] = '{C#{x'

            for direction in DIRECTIONS:
                # FIXME detect hidden/etc. and doors
                exit = current_room.get_exit(direction["id"])

                # Exit not found, no room.
                if not exit:
                    continue

                connector_x, connector_y = direction["connector_coords"]
                connector_x += current_x
                connector_y += current_y

                # Off the map.
                if coord_is_invalid(connector_x, connector_y):
                    continue

                grid[connector_y][connector_x] = direction["connector_symbol"]

                # This direction does not continue to be mapped.
                if not direction["continue"]:
                    continue

                next_room = exit.get_room()
                next_x, next_y = direction["coords"]
                next_x += current_x
                next_y += current_y

                # Off the map.
                if coord_is_invalid(next_x, next_y):
                    continue

                next_entry = (next_x, next_y, next_room)
                stack.append(next_entry)

        # Place your marker.
        grid[middle_y][middle_x] = "{R@{x"

        return Map(grid)

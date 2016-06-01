import math


class Map(object):
    def __init__(self, grid):
        self.grid = grid

    def get_lines(self):
        lines = []

        for row in reversed(self.grid):
            line = ''.join(row)
            lines.append(line)

        return lines

    def echo_to_actor(self, actor):
        for line in self.get_lines():
            actor.echo(line)

class Mapper(object):
    @classmethod
    def generate_map(self, room=None, actor=None, width=79, height=20, legend=False, border=False):
        INITIAL_CELL_VALUE = " "

        grid = []

        for y in range(0, height):
            grid.append([])
            for x in range(0, width):
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

        if room is None:
            room = actor.get_room()

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
                "connector_grid": [["{8|{x"]],
                "continue": True,
            },
            {
                "id": "east",
                "coords": (3, 0),
                "connector_coords": (1, 0),
                "connector_grid": [["{8-{x","{8-{x"]],
                "continue": True,
            },
            {
                "id": "south",
                "coords": (0, -2),
                "connector_coords": (0, -1),
                "connector_grid": [["{8|{x"]],
                "continue": True,
            },
            {
                "id": "west",
                "coords": (-3, 0),
                "connector_coords": (-2, 0),
                "connector_grid": [["{8-{x","{8-{x"]],
                "continue": True,
            },
            {
                "id": "up",
                "connector_coords": (1, 1),
                "connector_grid": [["{Y,{x"]],
                "continue": False,
            },
            {
                "id": "down",
                "connector_coords": (-1, -1),
                "connector_grid": [["{y'{x"]],
                "continue": False,
            },
        ]

        max_count = width * height
        while len(stack):

            entry = stack.pop(0)

            current_x, current_y, current_room = entry
            if not current_room:
                continue

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

                # Cycle through symbols grid for connector to see what to draw.
                symbols_grid = direction["connector_grid"]
                for cy in range(0, len(symbols_grid)):
                    for cx in range(0, len(symbols_grid[0])):
                        cdy = connector_y + cy
                        cdx = connector_x + cx

                        # Off the map.
                        if coord_is_invalid(cdx, cdy):
                            continue

                        symbol = symbols_grid[cy][cx]
                        grid[cdy][cdx] = symbol


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

        if border:
            grid[0][0] = '+'
            grid[max_y][0] = '+'
            grid[0][max_x] = '+'
            grid[max_y][max_x] = '+'

            for y in [0, height - 1]:
                for x in range(1, width - 1):
                    grid[y][x] = '-'

            for y in range(1, height - 1):
                for x in [0, width - 1]:
                    grid[y][x] = '|'

        return Map(grid)

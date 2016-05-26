from mud.mapper import Mapper
from mud.entities.object import Object
from mud.entities.character import Character
from mud.entities.actor import Actor
from settings.directions import DIRECTIONS


def look_command(actor, game, *args, **kwargs):
    room = actor.get_room()

    title_line = "{}{{x {} ({}) ({}) [Room {}] [ID {}]".format(
        "{B" + room.name + "{x",
        "{R[{WNOLOOT{R]{x",
        room.area_id,
        "{Wbuilding{x",
        room.id,
        room.uid,
    )

    output = []
    output.append(title_line)

    for index, line in enumerate(room.description):

        if index == 0:
            line = "  " + line

        output.append(line)

    output.append('')

    exits = []
    doors = []
    secrets = []

    def format_exits(exits):
        if not exits:
            return "none"
        return " ".join([exit["colored_name"] for exit in exits])

    for exit_id, exit in DIRECTIONS.items():
        room_exit = room.get_exit(exit_id)

        if not room_exit:
            continue

        if room_exit.has_flag("door") and room_exit.has_flag("closed"):
            if room_exit.has_flag("secret"):
                secrets.append(exit)
            else:
                doors.append(exit)
        else:
            exits.append(exit)

    exit_options = [
        ("Exits", exits),
        ("Doors", doors),
    ]
    # FIXME Add immortality check.
    if True:
        exit_options.append(("Secret", secrets))

    exit_line_parts = []
    for label, options in exit_options:
        exit_line_parts.append("{{x[{{G{}{{g:{{x {}{{x]".format(
            label,
            format_exits(options)
        ))

    output.append('   '.join(exit_line_parts))

    for cls in [Object, Actor, Character]:
        for other in cls.query_by_room_uid(actor.room_uid, game=game):
            if not actor.can_see(other) or other == actor:
                continue

            line = str(other.format_room_flags_to(actor))

            # Only add space if there's a set of flags.
            if line:
                line += ' '

            if type(other) is Object:
                line = '     ' + line

            line += str(other.format_room_name_to(actor))

            output.append(line)

    # Generate and prepend minimap.
    prefix_with_minimap = True

    if prefix_with_minimap:
        map_width = 11
        map_height = 7
        map_pad_width = 2

        map = Mapper.generate_map(actor=actor, border=True, width=map_width, height=map_height)
        map_lines = map.get_lines()

        minimapped_output = []

        for y in range(0, max(len(map_lines), len(output))):
            prefix_line = ' ' * (map_width + map_pad_width)
            if y < len(map_lines):
                prefix_line = map_lines[y] + (' ' * map_pad_width)

            output_line = output[y] if y < len(output) else ''

            minimapped_output.append(prefix_line + output_line)

        output = minimapped_output

    for line in output:
        actor.echo(line)

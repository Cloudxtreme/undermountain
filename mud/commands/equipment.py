def equipment_command(actor, *args, **kwargs):
    from settings.game import ACTOR_EQUIPMENT_LOCATIONS
    from utils.ansi import Ansi

    # FIXME Make this actually look up items.
    for location in ACTOR_EQUIPMENT_LOCATIONS:
        list_name = location.get("list_name", location.get("uid"))
        show_if_empty = location.get("show_if_empty", True)

        if show_if_empty:
            output = ""
            output += Ansi.pad_right(("{{G<{{C{}{{G>".format(list_name)), 14)
            output += " {xNothing"

            actor.echo(output)

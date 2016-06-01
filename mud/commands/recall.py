def recall_command(actor, game, *args, **kwargs):
    from mud.entities.room import Room

    room = Room.find_by("id", "3001", game=game)

    if not room:
        actor.echo("You failed.")
        return

    actor.set_room(room)
    actor.force("look")

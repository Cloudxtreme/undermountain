def goto_command(actor, game, params, *args, **kwargs):
    from mud.entities.room import Room

    actor.echo("Warning: Mob and character goto not yet supported.")

    room_id = "3001"
    if params:
        room_id = params[0]

    target_room = Room.find_by("uid", room_id, game=game)
    if not target_room:
        target_room = Room.find_by("id", room_id, game=game)
        if not target_room:
            actor.echo("Could not find room by id or uid.")
            return

    actor.set_room(target_room)
    actor.force("look")

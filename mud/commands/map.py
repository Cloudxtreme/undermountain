def map_command(actor, *args, **kwargs):
    from mud.mapper import Mapper

    room = actor.get_room()

    map = Mapper.generate_map(room)

    actor.echo("Testing map:")
    actor.echo()

    map.echo_to_actor(actor)

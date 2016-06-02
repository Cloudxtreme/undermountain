def social_command(actor, command, game, params, *args, **kwargs):
    from mud.entities.social import Social
    from mud.entities.actor import Actor
    from mud.entities.character import Character

    social = Social.find_by("name", command, game=game)

    if not params:
        actor.echo(social["me_room"])
        actor.act_around(social["actor_room"])
        return

    target_name = params[0]
    target = actor.find_room_entity(keyword=target_name, types=[Character, Actor])

    if target_name == "self":
        target = actor

    if target and actor == target:
        actor.echo(social["me_self"])
        actor.act_around(social["actor_self"])

    elif target:
        actor.echo(social["me_actor"])
        actor.act_to(target, social["actor_me"])
        actor.act_around(social["actor_other"], exclude=[target])

    else:
        actor.echo("Target not found.")
        # FIXME make use of the social not-found messaging?
        # actor.echo(social["me_no_target"])

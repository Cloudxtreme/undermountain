def emote_command(actor, params, *args, **kwargs):
    action = ' '.join(params)
    actor.echo("{{B{} {}{{x".format(actor.name, action))
    actor.act_around("{{B[actor.name] {}{{x".format(action))

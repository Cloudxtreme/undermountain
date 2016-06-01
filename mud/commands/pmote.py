def pmote_command(actor, params, *args, **kwargs):
    action = ' '.join(params)
    actor.echo("{{c{} {}{{x".format(actor.name, action))
    actor.act_around("{{c[actor.name] {}{{x".format(action))

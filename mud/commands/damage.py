def damage_command(actor, params, *args, **kwargs):
    try:
        amount = int(params[0])
    except Exception:
        amount = 1

    actor.damage(target=actor, amount=amount)

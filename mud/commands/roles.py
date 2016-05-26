def roles_command(actor, params, command, game, *args, **kwargs):
    from mud.entities.character import Character

    def params_details():
        actor.echo("Usage: {} <name> - List roles".format(command))
        actor.echo("       {} <name> add <role> - Add a role".format(command))
        actor.echo("       {} <name> remove <role> - Remove a role".format(command))

    remainder = list(params)
    if not remainder:
        actor.echo("You must provide a name.")
        params_details()
        return

    name = remainder.pop(0)

    target = Character.find_by("name", name, game)
    if not target:
        actor.echo("Target not found.")
        return

    actor.echo("Target: {}".format(target.name))
    if not remainder:
        actor.echo("{}'s roles: {}".format(
            target.name,
            ', '.join(target.get_roles())
        ))
    else:
        action = remainder.pop(0).lower()

        if not remainder:
            actor.echo("A role must be provided.")
            params_details()
            return

        role = remainder.pop(0).lower()

        if action == "add":
            target.add_role(role)
            actor.echo("Added role '{}' to {}.".format(
                role,
                target.name
            ))
        elif action == "remove":
            if not target.has_role(role):
                actor.echo("{} does not have role '{}'.".format(
                    target.name,
                    role,
                ))
                return

            target.remove_role(role)
            actor.echo("Removed role '{}' to {}.".format(
                role,
                target.name
            ))
        else:
            actor.echo("Invalid action '{}'.".format(action))
            params_details()
            return

        actor.echo("Updateed roles: {}".format(
            ', '.join(target.get_roles())
        ))

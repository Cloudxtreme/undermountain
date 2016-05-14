def sockets_command(actor, game, *args, **kwargs):
    actor.echo("[Num Connected_State        Login@       Idl] Player Name  Host")
    actor.echo("-" * 79)

    count = 0
    for connection in game.query_connections():
        count += 1

        other = connection.actor
        actor_name = other.name if other else "UNKNOWN"

        line = "["
        line += str(connection.id).rjust(3)
        line += " "
        line += connection.state[max(len(connection.state) - 16, 0):].center(16)
        line += " "
        line += "2016-05-13 XX:XX:00 "  # FIXME logged in date/time
        line += "   "  # FIXME idle time
        line += "] "
        line += actor_name.ljust(13)
        line += connection.ip
        if connection.hostname != connection.ip:
            line += "({})" + connection.hostname

        actor.echo(line)

    actor.echo()
    actor.echo("{} users".format(count))

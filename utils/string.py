from utils.ansi import Ansi


def pad_left(message, length, symbol=" "):
    stripped = Ansi.decolorize(message)
    return (symbol * max(0, length - len(stripped))) + message

def pad_right(message, length, symbol=" "):
    stripped = Ansi.decolorize(message)
    return message + (symbol * max(0, length - len(stripped)))

"""
CHANNELS
Methods of conversation across the Game to other Players.

SETTINGS
========

STRINGS
-------
- id: the channel that this channel uses as its primary flag
- fallback: if access fails, fallback to another channel
- scope: "room" "area" or "global" (defaults to "global")

TEMPLATE STRINGS
----------------
These strings have access to [actor.name] and [message] to format echos:
- send_template
- receive_template
- crosstalk_template - If received across ports, adds [environment] field

LISTS
-----
- roles: role(s) that have access to this command

BOOLEANS
--------
- name_always: boolean to always show name properly
- togglable: boolean for this channel to be player-togglable
- default: boolean to define if this channel defaults to being on for newbies
- crosstalk: can this channel be accessed cross-ports?

FUNCTIONS
---------
- access(actor, target): function for checking Player can send on this channel
    after the built-in nochan checks
- filter(actor): function for checking Player can see messages from channel
    after the built-in toggle checks
"""

CHANNELS = {
    "ask": {
        "send_template": "You [Q/A] Ask '{Y[message]{x'",
        "receive_template": "[actor.name] [Q/A] Asks '{Y[message]{x'",
        "default": True,
    },
    "answer": {
        "id": "ask",
        "send_template": "You [Q/A] Answer '{Y[message]{x'",
        "receive_template": "[actor.name] [Q/A] Answers '{Y[message]{x'",
    },
    "ooc": {
        "name_always": True,
        "default": True,
        "send_template": "{WYou OOC {8'{w[message]{8'{x",
        "receive_template": "{W[*OOC*]{c[actor.name] {8'{w[message]{8'{x",

    },
    "immtalk": {
        "default": True,
        "roles": ["immortal"],
        "send_template": "{w[actor.name]: {W[message]{x",
        "receive_template": "{w[actor.name]: {W[message]{x",
    },
    "music": {
        "send_template": "You MUSIC: '{C[message]{x'",
        "receive_template": "[actor.name] MUSIC: '{C[message]{x'",
    },
    "cgossip": {
        "access": lambda actor: actor.has_clan(),
        "filter": lambda actor, target: target.has_clan(),
        "send_template": "You cgossip '{R[message]{x'",
        "receive_template": "[actor.name] cgossips '{R[message]{x'",
    },
    "cgooc": {
        "id": "cgossip",
        "fallback": "cgossip",
        "access": lambda actor: actor.has_clan(),
        "filter": lambda actor, target: target.has_clan(),
        "send_template": "You cgossip [OOC] '{R[message]{x'",
        "receive_template": "[actor.name] cgossips [OOC] '{R[message]{x'",
    },
    "heronet": {
        "send_template": "{g[{RYou {GHero-Net{g]:'[message]'{x",
        "receive_template": "{g[{R[actor.name] {GHero-Nets{g]:'[message]'{x",
        "default": True,
    },
    "clan": {
        "default": True,
        "send_template": "You clan '{M[message]{x'",
        "access": lambda actor: actor.has_clan(),
        "filter": lambda actor, target: target.clan_id == actor.clan_id,
        "receive_template": "[actor.name] clans '{M[message]{x'",
    },
    "clooc": {
        "id": "clan",
        "send_template": "You clan [OOC] '{M[message]{x'",
        "access": lambda actor: actor.has_clan(),
        "filter": lambda actor, target: target.clan_id == actor.clan_id,
        "receive_template": "[actor.name] clans [OOC] '{M[message]{x'",
    },
    "auction": {
        "default": True,
        "send_template": "{xYou {R<{G-{Y={MA/B{Y={G-{R> {CAuction {x'{G[message]{x'",
        "receive_template": "{x[actor.name] {R<{G-{Y={MA/B{Y={G-{R> {CAuctions {x'{G[message]{x'",
    },
    "bid": {
        "id": "auction",
        "send_template": "{xYou {R<{G-{Y={MA/B{Y={G-{R> {CBid {x'{G[message]{x'",
        "receive_template": "{x[actor.name] {R<{G-{Y={MA/B{Y={G-{R> {CBids {x'{G[message]{x'",
    },
    "quote": {
        "default": True,
        "send_template": "You quote '{g[message]{x'",
        "receive_template": "[actor.name] quotes '{g[message]{x'",
    },
    # TODO IQ check
    "qgossip": {
        "send_template": "{xYou {C({Wqg{Bo{bs{Bs{Wip{C) {x'{C[message]{x'",
        "receive_template": "{x[actor.name] {C({Wqg{Bo{bss{Bi{Wps{C) {x'{C[message]{x'",
    },
    # TODO MA check
    "machat": {
        "send_template": "{m[{MMA Chat{m] {x[actor.name]{m: {W[message]{x",
        "receive_template": "{m[{MMA Chat{m] {x[actor.name]{m: {W[message]{x",
    },
    "cleader": {
        "send_template": "You {8<{RL{reader{8> {x: '{R[message]{x'",
        "receive_template": "[actor.name] {8<{RL{readers{8> {x: '{R[message]{x'",
    },
    "bitch": {
        "send_template": "{YYou BITCH {8'{Y[message]{8'{x",
        "receive_template": "{x[actor.name] {RB{ri{Bt{bc{Bh{re{Rs {8'{Y[message]{8'{x",
    },
    "imptalk": {
        "roles": ["admin"],
        "default": True,
        "togglable": False,
        "send_template": "{y[{wIMP Talk{y] {W[actor.name]{r: {C[message]{x",
        "receive_template": "{y[{wIMP Talk{y] {W[actor.name]{r: {C[message]{x",
    }
}


# crosstalk
# gossip
# agossip
# yell
# mgoss
# shout
# grats
# gtell
# tell
# whisper
# reply
# announce

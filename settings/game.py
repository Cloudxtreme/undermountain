"""
GENERAL GAME SETTINGS
"""
MAX_LEVEL = 101


"""
The slots that a piece of equipment can go in.

@type {list(string)}
"""
EQUIPMENT_SLOTS = [
    "head", "ear", "face", "neck", "clan_symbol", "tattoo", "torso", "body",
    "arms", "wrist", "hands", "finger", "waist", "legs", "ankle", "feet",
    "surrounding", "light", "floating", "weapon", "shield", "lance",
    "airship_key", "award", "instrument", "id_badge",
]

"""
Locations on the body that a piece of equipment can be worn on.

@key {string} uid Unique identifier for this slot.
@key {string} [slot=uid] The EQUIPMENT_SLOT that can be used here.
@key {string} [list_name=uid] The name to display on the "equipment" command list.
@key {string} [name=uid] The full name of the slot, defaults to uid with underscores removed.
@key {bool} [show_if_empty=True] Display this on the "equipment list if empty?
"""
ACTOR_EQUIPMENT_LOCATIONS = [
    {"uid": "award", "show_if_empty": False},
    {"uid": "head"},
    {"uid": "left_ear", "slot": "ear", "list_name": "l. ear"},
    {"uid": "right_ear", "slot": "ear", "list_name": "r. ear"},
    {"uid": "face"},
    {"uid": "first_neck", "slot": "neck", "list_name": "neck"},
    {"uid": "second_neck", "slot": "neck", "list_name": "neck"},
    {"uid": "clan_symbol", "slot": "clan_symbol", "list_name": "clan"},
    {"uid": "tattoo"},
    {"uid": "torso"},
    {"uid": "body"},
    {"uid": "arms"},
    {"uid": "left_wrist", "slot": "wrist", "list_name": "l. wrist"},
    {"uid": "right_wrist", "slot": "wrist", "list_name": "r. wrist"},
    {"uid": "hands"},
    {"uid": "left_finger", "slot": "finger", "list_name": "l. finger"},
    {"uid": "right_finger", "slot": "finger", "list_name": "r. finger"},
    {"uid": "waist"},
    {"uid": "legs"},
    {"uid": "left_ankle", "slot": "ankle", "list_name": "l. ankle"},
    {"uid": "right_ankle", "slot": "ankle", "list_name": "r. ankle"},
    {"uid": "feet"},
    {"uid": "surrounding"},
    {"uid": "light"},
    {"uid": "floating"},
    {"uid": "primary_weapon", "slot": "weapon", "list_name": "pri. weapon"},
    {"uid": "shield"},
    {"uid": "secondary_weapon", "slot": "weapon", "list_name": "sec. weapon"},
    {"uid": "lance", "list_name": "lance weapon"},
    {"uid": "airship_key", "show_if_empty": False, "list_name": "airship key"},
    {"uid": "id_badge", "show_if_empty": False, "list_name": "{RI.D."},
    {"uid": "instrument", "show_if_empty": False},
]

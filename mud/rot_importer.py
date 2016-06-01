"""
Import ROT Data
"""

class RotImporter(object):
    @classmethod
    def handle_area_header_line(cls, area, line):
        stripped = line.strip()
        parts = stripped.split(" ")

        # #AREADATA
        # Name Westbridge~
        # Builders None~
        # VNUMs 2810 3399
        # Credits [ Public ] City Of Westbridge~
        # Security 10
        # Recall 3001
        # Faction faction2~
        # AQpoints 5
        # Realm 4
        # Zone 1

        if parts[0] == "Name":
            area["name"] = " ".join(parts[1:]).rstrip("~")
        elif parts[0] == "Builders":
            return
        elif parts[0] == "VNUMs":
            area["vnums"] = [int(parts[1]), int(parts[2])]
        elif parts[0] == "Credits":
            area["credits"] = " ".join(parts[1:]).rstrip("~")
        elif parts[0] == "Security":
            area["security"] = int(parts[1])
        elif parts[0] == "Recall":
            area["recall_room_id"] = int(parts[1])
        elif parts[0] == "Faction":
            area["faction_id"] = parts[1].rstrip("~")
        elif parts[0] == "AQpoints":
            area["area_quest_points"] = int(parts[1])
        elif parts[0] == "Realm":
            area["realm_id"] = int(parts[1])
        elif parts[0] == "Zone":
            area["zone_id"] = int(parts[1])
        else:
            raise Exception("Unhandled area header line: " + line)

    @classmethod
    def import_area_from_file(cls, path, debug=False):
        state = "ready_to_start_section"
        path_parts = path.split("/")
        filename = path_parts[-1]
        uid = filename.replace(".are", "")

        area = {
            "uid": uid,
            "id": uid,
            "mobiles": {},
            "objects": {},
            "rooms": {},
            "subroutines": []
        }
        mobile = None
        room = None
        exit = None
        room_extra = None

        with open(path, "r") as fh:
            line_index = 0
            for line in fh:
                line_index += 1
                if debug:
                    print(line_index, state, line)
                try:
                    if state == "ready_to_start_section":
                        if line.strip() == "":
                            continue
                        elif line.startswith("#$"):
                            return area
                        elif line.startswith("#AREADATA"):
                            state = "area_header"
                            continue
                        elif line.startswith("#MOBILES"):
                            state = "mobiles_header"
                            continue
                        elif line.startswith("#OBJECTS"):
                            state = "objects_header"
                            continue
                        elif line.startswith("#ROOMS"):
                            state = "rooms_header"
                            continue
                        elif line.startswith("#SPECIALS"):
                            state = "specials_header"
                            continue
                        elif line.startswith("#RESETS"):
                            state = "resets_header"
                            continue
                        elif line.startswith("#SHOPS"):
                            state = "shops_header"
                            continue
                        elif line.startswith("#MOBPROGS"):
                            state = "mobprogs_header"
                            continue
                        elif line.startswith("#$"):
                            # DONE?
                            continue
                        else:
                            raise Exception("Unhandled section identifier: " + line)

                    elif state == "mobprogs_header":
                        if debug:
                            print("SKIP MOBPROGS FOR NOW", line)
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "shops_header":
                        if debug:
                            print("SKIP SHOPS FOR NOW", line)
                        if line.strip() == "0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "specials_header":
                        if debug:
                            print("SKIP SPECIALS FOR NOW", line)
                        if line.strip() == "S":
                            state = "ready_to_start_section"
                        continue

                    elif state == "resets_header":
                        if debug:
                            print("SKIP RESETS FOR NOW", line)
                        if line.strip() == "S":
                            state = "ready_to_start_section"
                        continue

                    elif state == "objects_header":
                        if debug:
                            print("SKIP OBJECTS FOR NOW", line)
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "rooms_header":
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        elif line.startswith("#"):
                            if room:
                                area["rooms"][room["vnum"]] = room
                            room = {
                                "vnum": line.strip("\n#"),
                                "extras": {},
                                "exits": {}
                            }
                            state = "room_name"
                        continue

                    elif state == "room_name":
                        room["name"] = line.strip("\n~")
                        state = "room_wanted"

# Name.............[Market Square]
# Area.............[   30] Westbridge
# SpyVnum..........[    0]
# Sector...........[cityst]
# Room flags.......[law]
# Room 2 flags.....[none]
# Region...........[none]
# Health recovery..[100]
# Mana recovery....[100]
# Clan.............[0] none
# Owner............[]
# Faction..........[]
# Deed Owner.......[]
# Business.........[]
# Renter...........[]
# Rent Cost........[0]
# Rent Due.........[0]
# Property Value...[0]
# Desc Kwds........[sign]
# Characters.......[kelemvor westbridgian westbridge]
# Objects..........[portal fountain bench plaque statue airship]
# -north to [ 3107] Key: [    0]  Exit flags: [none]
# -east to [ 3015] Key: [    0]  Exit flags: [none]
# -south to [ 2889] Key: [    0]  Exit flags: [none]
# -west to [ 3013] Key: [    0]  Exit flags: [none]
# -up to [34803] Key: [    0]  Exit flags: [none]
# -down to [  430] Key: [    0]  Exit flags: [door closed]
                    elif state == "room_wanted":
                        room["wanted_area_vnum"] = line.strip("\n~")
                        room["description"] = []
                        state = "room_description"
                        continue

                    elif state == "room_description":
                        cleaned = line.strip("\n~")

                        if "~" not in line or cleaned:
                            room["description"].append(cleaned)

                        if "~" in line:
                            state = "room_flags"

                        continue

                    elif state == "room_flags":
                        room["flags_raw"] = line.strip()
                        state = "room_flags2"
                        continue

                    elif state == "room_flags2":
                        room["flags2_raw"] = line.strip()
                        state = "room_exit_or_extra"
                        continue

                    elif state == "room_exit_or_extra":
                        if line.strip() == "E":
                            state = "room_extra_keywords"
                            continue
                        elif line.startswith("D"):
                            state = "room_exit_description"
                            exit = {
                                "direction": ["north", "east", "south", "west", "up", "down"][int(line[1])],
                                "description": []
                            }
                            continue
                        elif line.strip("~\n") == "S":
                            state = "rooms_header"
                            continue
                        else:
                            if debug:
                                print(state, "UNHANDLED LINE", line)

                    elif state == "room_extra_keywords":
                        room_extra = {
                            "keywords": line.strip("\n~"),
                            "description": []
                        }
                        state = "room_extra_description"

                    elif state == "room_extra_description":
                        room_extra["description"].append(line.strip("\n~"))
                        if "~" in line:
                            room["extras"][room_extra["keywords"]] = room_extra
                            if "keywords" in room_extra:
                                del room_extra["keywords"]
                            room_extra = None
                            state = "room_exit_or_extra"
                            continue

                    elif state == "room_exit_description":
                        exit["description"].append(line.strip("\n~"))
                        if "~" in line:
                            state = "room_exit_description2"
                            continue

                    elif state == "room_exit_description2":
                        if debug:
                            print("UNKNOWN SECTION AFTER EXIT DESCRIPTION", line)
                        if "~" in line:
                            state = "room_exit_vnums"
                            continue

                    elif state == "room_exit_vnums":
                        parts = line.strip("\n~").split()
                        exit["flags_raw"] = parts[1]
                        exit["room_id"] = parts[2]
                        room["exits"][exit["direction"]] = exit
                        if "direction" in exit:
                            del exit["direction"]
                        exit = None
                        state = "room_exit_or_extra"
                        continue

                    elif state == "mobiles_header" or \
                        state == "mobile_attachments" and line.startswith("#"):
                        index = 0
                        if line.startswith("#"):
                            if mobile:
                                area["mobiles"][mobile["vnum"]] = mobile

                            mobile_id = int(line.lstrip("#"))
                            if mobile_id == 0:
                                state = "ready_to_start_section"
                                continue
                            else:
                                state = "mobile_header"
                                index = 0
                                mobile = {
                                    "vnum": mobile_id,
                                    "description": [],
                                    "subroutines": []
                                }
                                continue
                        else:
                            raise Exception("Invalid mobiles header line: " + line)
                        continue

                    elif state == "mobile_header":
                        index += 1

                        if index == 1:
                            mobile["keywords"] = line.rstrip("~")
                        elif index == 2:
                            mobile["name"] = line.rstrip("~")
                        elif index == 3:
                            mobile["room_name"] = line.rstrip("~")
                        elif index == 4:
                            state = "mobile_description"
                        else:
                            raise Exception("Unhandled mobile header line: " + line)

                    elif state == "mobile_description":
                        if line.strip().endswith("~"):
                            state = "mobile_stats_race"
                        else:
                            mobile["description"].append(line)

                    elif state == "mobile_stats_race":
                        mobile["race_id"] = line.strip().rstrip("~")
                        state = "mobile_stats_flags"

                    elif state == "mobile_stats_flags":
                        mobile["raw_flags"] = line.strip()
                        state = "mobile_stats_flags2"

                    elif state == "mobile_stats_flags2":
                        mobile["raw_flags2"] = line.strip()
                        state = "mobile_stats_flags3"

                    elif state == "mobile_stats_flags3":
                        mobile["raw_flags3"] = line.strip()
                        state = "mobile_stats_flags4"

                    elif state == "mobile_stats_flags4":
                        mobile["raw_flags4"] = line.strip()
                        state = "mobile_stats_flags5"

                    elif state == "mobile_stats_flags5":
                        mobile["raw_flags5"] = line.strip()
                        state = "mobile_stats_flags6"

                    elif state == "mobile_stats_flags6":
                        mobile["raw_flags6"] = line.strip()
                        state = "mobile_attachments"

                    elif state == "mobile_attachments":
                        parts = line.strip().split(" ")
                        if parts[0] == "D":
                            mobile["d_flags"] = line.strip()
                            continue
                        elif parts[0] == "T":
                            mobile["t_flags"] = line.strip()
                            continue
                        elif parts[0] == "M":
                            mobile["subroutines"].append(line)
                            continue
                        elif parts[0] == "F":
                            if parts[1] == "for":
                                mobile["raw_form"] = parts[2]
                            elif parts[1] == "aff":
                                mobile["raw_affected"] = parts[2]
                            elif parts[1] == "off":
                                mobile["raw_off"] = parts[2]
                            elif parts[1] == "imm":
                                mobile["raw_immunities"] = parts[2]
                            elif parts[1] == "res":
                                mobile["raw_resistances"] = parts[2]
                            elif parts[1] == "par":
                                mobile["raw_parts"] = parts[2]
                            elif parts[1] == "act":
                                mobile["raw_acts"] = parts[2]
                            elif parts[1] == "vul":
                                mobile["raw_vulns"] = parts[2]
                            else:
                                raise Exception("Unhandled attachment form line: " + line)

                            mobile["subroutines"].append(line)
                            continue
                        else:
                            raise Exception("Unhandled mobile attachments line: " + line)

                    elif state == "area_header":
                        if line.strip() == "End":
                            state = "ready_to_start_section"
                            continue

                        cls.handle_area_header_line(area, line)
                        continue

                    else:
                        raise Exception("Unhandled line: " + line)
                except Exception as e:
                    print("** EXCEPTION **")
                    print("Filename: {} ".format(path))
                    print("State: {}".format(state))
                    print("Line: {}".format(line_index))
                    print(e)
                    break

        return area

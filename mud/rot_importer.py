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
    def import_area_from_file(cls, path):
        state = "ready_to_start_section"
        path_parts = path.split("/")
        filename = path_parts[-1]
        uid = filename.replace(".are", "")

        area = {
            "uid": uid,
            "id": uid,
            "mobiles": [],
            "objects": [],
            "subroutines": []
        }
        mobile = None

        with open(path, "r") as fh:
            line_index = 0
            for line in fh:
                line_index += 1
                print(line_index, state, line)
                try:
                    if state == "ready_to_start_section":
                        if line.strip() == "":
                            continue
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
                        print("SKIP MOBPROGS FOR NOW", line)
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "shops_header":
                        print("SKIP SHOPS FOR NOW", line)
                        if line.strip() == "0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "specials_header":
                        print("SKIP SPECIALS FOR NOW", line)
                        if line.strip() == "S":
                            state = "ready_to_start_section"
                        continue

                    elif state == "resets_header":
                        print("SKIP RESETS FOR NOW", line)
                        if line.strip() == "S":
                            state = "ready_to_start_section"
                        continue

                    elif state == "objects_header":
                        print("SKIP OBJECTS FOR NOW", line)
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "rooms_header":
                        print("SKIP ROOMS FOR NOW", line)
                        if line.strip() == "#0":
                            state = "ready_to_start_section"
                        continue

                    elif state == "mobiles_header" or \
                        state == "mobile_attachments" and line.startswith("#"):
                        index = 0
                        if line.startswith("#"):
                            if mobile is not None:
                                area["mobiles"].append(mobile)

                            mobile_id = int(line.lstrip("#"))
                            if mobile_id == 0:
                                state = "ready_to_start_section"
                                continue
                            else:
                                state = "mobile_header"
                                index = 0
                                mobile = {
                                    "id": mobile_id,
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
                            elif parts[1] == "par":
                                mobile["raw_parts"] = parts[2]
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
                    print("At line {}: ".format(line_index))
                    print("State: {}".format(state))
                    print(e)
                    print("Current Mobile: ")
                    print(mobile)
                    break

        return area

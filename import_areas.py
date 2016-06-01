from mud.rot_importer import RotImporter

import json

area_vnum = "westbridge"
area = RotImporter.import_area_from_file("imports/areas/{}.are".format(area_vnum))

with open("data/live/areas/{}.json".format(area_vnum), "w") as output_file:
    output_file.write(json.dumps(area, indent=4))

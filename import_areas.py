from mud.rot_importer import RotImporter

import json
import glob

SKIPS = [
    "social.are",
    "helps.are",
]
for full_path in glob.glob("imports/areas/*.are"):
    filename = full_path.split("/")[-1]

    if filename in SKIPS:
        print("** SKIPPING '{}' as requested in SKIPS list".format(filename))
        continue

    area_vnum = filename.split(".are")[0]

    area = RotImporter.import_area_from_file("imports/areas/{}.are".format(area_vnum))

    output_filename = "{}.json".format(area_vnum)
    with open("data/live/areas/{}".format(output_filename), "w") as output_file:
        output_file.write(json.dumps(area, indent=4))
        print("Imported area '{}' to '{}'".format(
            filename,
            output_filename,
        ))

import json
from shutil import copyfile
from munch import Munch


class RmrTriplet(object):

    def __init__(self, origin_file_name, triplet_root_name):
        self.origin_file_name = origin_file_name
        self.triplet_root_name = triplet_root_name
        self.user_file_name = triplet_root_name + ".user.json"
        self.proposed_file_name = triplet_root_name + ".proposed.json"
        self.baseline_file_name = triplet_root_name + ".baseline.json"
        self.user_instance = {}
        self.user = Munch()
        self.proposed_instance = {}
        self.proposed = Munch()
        self.baseline_instance = {}
        self.baseline = Munch()
        self.create_triplet_instances()
        self.proposed_err = False
        self.baseline_err = False

    def create_triplet_instances(self):
        copyfile(self.origin_file_name, self.user_file_name)
        with open(self.user_file_name, "r") as instance_file:
            self.user_instance = json.load(instance_file)
            self.user = Munch.fromDict(self.user_instance)
            self.user.transformation_stage = "USER"
        copyfile(self.origin_file_name, self.proposed_file_name)
        with open(self.proposed_file_name, "r") as instance_file:
            self.proposed_instance = json.load(instance_file)
            self.proposed = Munch.fromDict(self.proposed_instance)
            self.proposed.transformation_stage = "PROPOSED"
        copyfile(self.origin_file_name, self.baseline_file_name)
        with open(self.baseline_file_name, "r") as instance_file:
            self.baseline_instance = json.load(instance_file)
            self.baseline = Munch.fromDict(self.baseline_instance)
            self.baseline.transformation_stage = "BASELINE"

    def save_instances(self):
        with open(self.user_file_name, "w") as instance_file:
            json.dump(self.user, instance_file, indent=2)
        with open(self.proposed_file_name, "w") as instance_file:
            json.dump(self.proposed, instance_file, indent=2)
        with open(self.baseline_file_name, "w") as instance_file:
            json.dump(self.baseline, instance_file, indent=2)

    def check_rules(self):
        print("------------------------")
        print("Checking rules for:")
        print(f"  {self.user_file_name}")
        print(f"  {self.proposed_file_name}")
        print(f"  {self.baseline_file_name}")

        self.check_exterior_lights_6a_1()

        if self.proposed_err:
            print("Proposed RMR file fails.")
        else:
            print("Proposed RMR file passes.")
        if self.baseline_err:
            print("Baseline RMR file fails.")
        else:
            print("Baseline RMR file passes.")
        print("")

    def check_exterior_lights_6a_1(self):
        # Last paragraph of baseline side of Table G3.1 part 6 and Table G3.6
        tableG3_6 = {"PARKING_LOTS_AND_DRIVES": ["tradable" ,0.15, "W/sqft"],  # should be 0.15
                        "WALKWAYS_NARROW": ["tradable", 1.0, "W/ft"],
                        "WALKWAYS_WIDE": ["tradable", 0.2, "W/sqft"],
                        "PLAZA_AREAS": ["tradable", 0.2, "W/sqft"],
                        "SPECIAL_FEATURE_AREAS": ["tradable", 0.2, "W/sqft"],
                        "STAIRWAYS": ["tradable", 1.0, "W/sqft"],
                        "MAIN_ENTRIES": ["tradable", 30, "W/ft"],
                        "OTHER_DOORS": ["tradable", 20, "W/ft"],
                        "CANOPIES": ["tradable", 1.25, "W/sqft"],
                        "OPEN_OUTDOOR_SALES": ["tradable", 0.5, "W/sqft"],
                        "STREET_FRONTAGE_VEHICLE_SALES_LOTS": ["tradable", 20, "W/ft"],
                        "BUILDING_FACADES": ["nontradable", 0.0, ""],
                        "AUTOMATED_TELLER_MACHINE": ["nontradable", 0.0, ""],
                        "NIGHT_DEPOSITORIES": ["nontradable", 0.0, ""],
                        "GATEHOUSE_INSPECTION_STATIONS": ["nontradable", 0.0, ""],
                        "LOADING_AREAS_EMERGENCY_RESPONDERS": ["nontradable", 0.0, ""],
                        "DRIVE_UP_WINDOW_FAST_FOOD": ["nontradable", 0.0, ""],
                        "PARKING_NEAR_24_HR_RETAIL_ENTRANCES": ["nontradable", 0.0, ""]}

        for exterior_lighting_areas in self.baseline.ExteriorLightingAreas:
            print(f"Confirming rule 6a_1 for {exterior_lighting_areas.name}")
            status, multiplier, units = tableG3_6[exterior_lighting_areas.category]
            if status == "tradable":
                if units == "W/sqft":
                    expected_power = exterior_lighting_areas.area * multiplier
                    if exterior_lighting_areas.power != expected_power:
                        print(f"  No, invalid power found: {exterior_lighting_areas.power} but expected {expected_power}")
                        self.baseline_err = True
                    else:
                        print(f"  Yes, power same as expected: {expected_power}")
                else:
                    print("  Rule not checked except for W/sqft tradable areas.")
            else:
                print("  Non-tradable area rules not yet checked.")

        if self.user.ExteriorLightingAreas == self.proposed.ExteriorLightingAreas:
            print("  Yes, proposed ExteriorLightingAreas matches user")
        else:
            print("  No, proposed ExteriorLightingAreas does not match user")
            self.proposed_err = True

import json
from shutil import copyfile
from munch import Munch
from copy import deepcopy


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

    def check_rules(self, rules_to_check):
        if "all" in rules_to_check:
            rules_to_check = ["6a_1", "18a_1"]

        if rules_to_check:
            print("------------------------")
            print("Checking rules for:")
            print(f"  {self.user_file_name}")
            print(f"  {self.proposed_file_name}")
            print(f"  {self.baseline_file_name}")
            print(f"  Specific rules checked: {rules_to_check}")

            if "6a_1" in rules_to_check:
                self.check_exterior_lights_6a_1()
            if "18a_1" in rules_to_check:
                self.check_system_selection_18a_1()

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

        # remove changing portions to see if rest is the same
        altered_user = deepcopy(self.user.ExteriorLightingAreas)
        for exterior_lighting_areas in altered_user:
            exterior_lighting_areas.power = 0
        altered_baseline = deepcopy(self.baseline.ExteriorLightingAreas)
        for exterior_lighting_areas in altered_baseline:
            exterior_lighting_areas.power = 0
        if altered_user == altered_baseline:
            print("  Yes, rest of baseline ExteriorLightingAreas matches user")
        else:
            print("  No, rest of baseline ExteriorLightingAreas does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.ExteriorLightingAreas == self.proposed.ExteriorLightingAreas:
            print("  Yes, proposed ExteriorLightingAreas matches user")
        else:
            print("  No, proposed ExteriorLightingAreas does not match user")
            self.proposed_err = True


    def check_system_selection_18a_1(self):
        # G3.1.1a, table G3.1.1-3, table G3.1.1-4

        TableG3_1_1_3 = {
            "RESIDENTIAL": ["SYSTEM_1_PTAC", "SYSTEM_2_PTHP"],
            "PUBLIC_ASSEMBLY_SMALL": ["SYSTEM_3_PSZ_AC","SYSTEM_4_PSZ_HP"],
            "PUBLIC_ASSEMBLY_LARGE": ["SYSTEM_12_SINGLE_ZONE_CONSTANT_HOT_WATER", "SYSTEM_13_SINGLE_ZONE_CONSTANT_ELECTRIC"],
            "HEATED_ONLY_STORAGE": ["SYSTEM_9_HEATING_AND_VENTILATION_GAS", "SYSTEM_10_HEATING_AND_VENTILATION_ELECTRIC"],
            "RETAIL_TWO_FLOOR_OR_LESS": ["SYSTEM_3_PSZ_AC", "SYSTEM_4_PSZ_HP"],
            "OTHER_NONRESIDENTIAL_SMALL": ["SYSTEM_3_PSZ_AC", "SYSTEM_4_PSZ_HP"],
            "OTHER_NONRESIDENTIAL_MEDIUM": ["SYSTEM_5_PACKAGED_VAV_WITH_REHEAT", "SYSTEM_6_PACKAGED_VAV_WITH_PFP_BOXES"],
            "OTHER_NONRESIDENTIAL_LARGE": ["SYSTEM_7_VAV_WITH_REHEAT", "SYSTEM_8_VAV_WITH_PFP_BOXES"]
        }

        total_area = 0
        highest_floor = -1
        first_building_area_type = self.user.Building.ThermalBlocks[0].building_area_type
        all_area_types_same = True
        for thermal_block in self.user.Building.ThermalBlocks:
            total_area += thermal_block.gross_conditioned_floor_area
            if thermal_block.floor_number > highest_floor:
                highest_floor = thermal_block.floor_number
            if thermal_block.building_area_type != first_building_area_type:
                all_area_types_same = False

        if not all_area_types_same:
            print("  Rules not checked that apply to buildings with multiple building types.")
        else:
            if first_building_area_type != "OFFICE":
                print("  Rules not checked that apply to buildings other than office buildings.")
            else:
                building_type_subcategory = "OTHER_NONRESIDENTIAL_MEDIUM"
                if total_area < 25000 and highest_floor <=3:
                    building_type_subcategory = "OTHER_NONRESIDENTIAL_SMALL"
                elif total_area > 150000 or highest_floor > 5:
                    building_type_subcategory = "OTHER_NONRESIDENTIAL_LARGE"

                expected_baseline_system, baseline_system_climate_zones_0_to_3A = TableG3_1_1_3[building_type_subcategory]
                if self.user.climate_zone in ["0A", "0B", "1A", "1B", "2A", "2B", "3A", "3B", "3C"]:
                    expected_baseline_system = baseline_system_climate_zones_0_to_3A

                for hvac_system in self.baseline.Building.HeatingVentilationAirConditioningSystems:
                    print(f"Confirming rule 18a_1 for {hvac_system.tag}")
                    if hvac_system.hvac_system_type == expected_baseline_system:
                        print(f"  Yes, baseline HVAC system: {hvac_system.hvac_system_type} matches expected for {hvac_system.tag}")
                    else:
                        print(f"  No, baseline HVAC system {hvac_system.hvac_system_type} does not match expected {expected_baseline_system} for {hvac_system.tag}")
                        self.proposed_err = True

        # remove changing portions to see if rest is the same
        altered_user = deepcopy(self.user.Building.HeatingVentilationAirConditioningSystems)
        for hvac_system in altered_user:
            hvac_system.hvac_system_type = ""
        altered_baseline = deepcopy(self.baseline.Building.HeatingVentilationAirConditioningSystems)
        for hvac_system in altered_baseline:
            hvac_system.hvac_system_type = ""
        if altered_user == altered_baseline:
            print("  Yes, rest of baseline HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, rest of baseline HeatingVentilationAirConditioningSystems does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.Building.HeatingVentilationAirConditioningSystems == self.proposed.Building.HeatingVentilationAirConditioningSystems:
            print("  Yes, proposed HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, proposed HeatingVentilationAirConditioningSystems does not match user")
            self.proposed_err = True

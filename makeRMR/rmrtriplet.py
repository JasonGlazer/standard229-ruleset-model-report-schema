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
            rules_to_check = ["6a_1", "18a_1", "19v_4", "5c_1", "5h_1"]

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
            if "19v_4" in rules_to_check:
                self.check_fan_power_19v_4()
            if "5c_1" in rules_to_check:
                self.vertical_fenestration_percentage_5c_1()
            if "5h_1" in rules_to_check:
                self.vertical_fenestration_assembly_5h_1()

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
        table_g3_6 = {
            "PARKING_LOTS_AND_DRIVES": ["tradable", 0.15, "W/sqft"],  # should be 0.15
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
            status, multiplier, units = table_g3_6[exterior_lighting_areas.category]
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
            print("  Yes, the other portions of baseline ExteriorLightingAreas matches user")
        else:
            print("  No, the other portions of baseline ExteriorLightingAreas does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.ExteriorLightingAreas == self.proposed.ExteriorLightingAreas:
            print("  Yes, proposed ExteriorLightingAreas matches user")
        else:
            print("  No, proposed ExteriorLightingAreas does not match user")
            self.proposed_err = True

    def check_system_selection_18a_1(self):
        # G3.1.1a, table G3.1.1-3, table G3.1.1-4

        table_g3_1_1_3 = {
            "RESIDENTIAL": ["SYSTEM_1_PTAC", "SYSTEM_2_PTHP"],
            "PUBLIC_ASSEMBLY_SMALL": ["SYSTEM_3_PSZ_AC", "SYSTEM_4_PSZ_HP"],
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
                if total_area < 25000 and highest_floor <= 3:
                    building_type_subcategory = "OTHER_NONRESIDENTIAL_SMALL"
                elif total_area > 150000 or highest_floor > 5:
                    building_type_subcategory = "OTHER_NONRESIDENTIAL_LARGE"

                expected_baseline_system, baseline_system_climate_zones_0_to_3a = table_g3_1_1_3[building_type_subcategory]
                if self.user.climate_zone in ["0A", "0B", "1A", "1B", "2A", "2B", "3A", "3B", "3C"]:
                    expected_baseline_system = baseline_system_climate_zones_0_to_3a

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
            print("  Yes, the other portions of baseline HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, the other portions of baseline HeatingVentilationAirConditioningSystems does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.Building.HeatingVentilationAirConditioningSystems == self.proposed.Building.HeatingVentilationAirConditioningSystems:
            print("  Yes, proposed HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, proposed HeatingVentilationAirConditioningSystems does not match user")
            self.proposed_err = True

    def check_fan_power_19v_4(self):
        # G3.1.2.9 System Fan Power, Table G3.1.2.9, Table G3.9.1
        # Users Manual for 90.1-2016 - Example G-M

        section_g3_1_2_9_mapping = {
            "SYSTEM_1_PTAC": "CFMs",
            "SYSTEM_2_PTHP": "CFMs",
            "SYSTEM_3_PSZ_AC": "bhp/fan motor efficiency",
            "SYSTEM_4_PSZ_HP": "bhp/fan motor efficiency",
            "SYSTEM_5_PACKAGED_VAV_WITH_REHEAT": "bhp/fan motor efficiency",
            "SYSTEM_6_PACKAGED_VAV_WITH_PFP_BOXES": "bhp/fan motor efficiency",
            "SYSTEM_7_VAV_WITH_REHEAT": "bhp/fan motor efficiency",
            "SYSTEM_8_VAV_WITH_PFP_BOXES": "bhp/fan motor efficiency",
            "SYSTEM_9_HEATING_AND_VENTILATION_GAS": "CFMsPlusNonMechanicalCooling",
            "SYSTEM_10_HEATING_AND_VENTILATION_ELECTRIC": "CFMsPlusNonMechanicalCooling",
            "SYSTEM_11_SINGLE_ZONE_VAV": "bhp/fan motor efficiency",
            "SYSTEM_12_SINGLE_ZONE_CONSTANT_HOT_WATER": "bhp/fan motor efficiency",
            "SYSTEM_13_SINGLE_ZONE_CONSTANT_ELECTRIC": "bhp/fan motor efficiency"
        }

        table_g3_1_2_9_mapping = {
            "SYSTEM_3_PSZ_AC": 0.00094,
            "SYSTEM_4_PSZ_HP": 0.00094,
            "SYSTEM_5_PACKAGED_VAV_WITH_REHEAT": 0.0013,
            "SYSTEM_6_PACKAGED_VAV_WITH_PFP_BOXES": 0.0013,
            "SYSTEM_7_VAV_WITH_REHEAT": 0.0013,
            "SYSTEM_8_VAV_WITH_PFP_BOXES": 0.0013,
            "SYSTEM_11_SINGLE_ZONE_VAV": 0.00062,
            "SYSTEM_12_SINGLE_ZONE_CONSTANT_HOT_WATER": 0.00094,
            "SYSTEM_13_SINGLE_ZONE_CONSTANT_ELECTRIC": 0.00094
        }

        table_g3_9_1_mapping = {
            1.0: 82.5,
            1.5: 84.0,
            2.0: 84.0,
            3.0: 87.5,
            5.0: 87.5,
            7.5: 89.5,
            10.0: 89.5,
            15.0: 91.0,
            20.0: 91.0,
            25.0: 91.0,
            30.0: 92.4,
            40.0: 93.0,
            50.0: 93.0,
            60.0: 93.6,
            75.0: 94.1,
            100.0: 94.5,
            125.0: 94.5,
            150.0: 95.0,
            200.0: 95.0
        }

        for hvac_system in self.baseline.Building.HeatingVentilationAirConditioningSystems:
            print(f"Confirming rule 19v_4 for {hvac_system.tag}")
            fan_power_calculation_method = section_g3_1_2_9_mapping[hvac_system.hvac_system_type]

            expected_electric_power_to_fan_motor = 0
            if fan_power_calculation_method == "CFMsPlusNonMechanicalCooling":
                print("  Rules not checked for fan power related to non-mechanical cooling.")
                fan_power_calculation_method = "CFMs"

            if fan_power_calculation_method == "CFMs":
                expected_electric_power_to_fan_motor = 0.3 * hvac_system.design_supply_fan_airflow_rate
            elif fan_power_calculation_method == "bhp/fan motor efficiency":
                supply_volume_multiplier = table_g3_1_2_9_mapping[hvac_system.hvac_system_type]
                expected_brake_horse_power = supply_volume_multiplier * hvac_system.design_supply_fan_airflow_rate

                if self.nearly_equal(hvac_system.fan_brake_horsepower, expected_brake_horse_power, 0.5):
                    print(f"  Yes, fan break horsepower {hvac_system.fan_brake_horsepower} nearly same as expected: {expected_brake_horse_power}")
                else:
                    print(f"  No, invalid fan break horsepower: {hvac_system.fan_brake_horsepower} but expected {expected_brake_horse_power}")
                    self.baseline_err = True

                shaft_input_power_limits = table_g3_9_1_mapping.keys()
                shaft_input_power_selected = 0
                for limit in shaft_input_power_limits:
                    # print(limit)
                    if expected_brake_horse_power <= limit:
                        shaft_input_power_selected = limit
                if shaft_input_power_selected != 0:
                    motor_efficiency = table_g3_9_1_mapping[shaft_input_power_selected]
                    print(f"  Motor efficiency of {motor_efficiency} selected based {shaft_input_power_selected} which is next larger from {expected_brake_horse_power}")
                else:
                    print(f"  Look up of motor efficiency did not work for {hvac_system.tag} with a size of {expected_brake_horse_power} so selecting 95%")
                    motor_efficiency = 95
                expected_electric_power_to_fan_motor = expected_brake_horse_power * 0.746 / (motor_efficiency / 100)
                print(f"  Rules not checked related to A adjustment from Section 6.5.3.1.1 for {hvac_system.tag}")
            else:
                print("  No, unknown fan power calculation method")
                self.proposed_err = True

            if self.nearly_equal(hvac_system.electric_power_to_fan_motor, expected_electric_power_to_fan_motor, 0.5):
                print(f"  Yes, power {hvac_system.electric_power_to_fan_motor} nearly same as expected: {expected_electric_power_to_fan_motor}")
            else:
                print(f"  No, invalid power found: {hvac_system.electric_power_to_fan_motor} but expected {expected_electric_power_to_fan_motor}")
                self.baseline_err = True

        # remove changing portions to see if rest is the same
        altered_user = deepcopy(self.user.Building.HeatingVentilationAirConditioningSystems)
        for hvac_system in altered_user:
            hvac_system.electric_power_to_fan_motor = 0
            hvac_system.fan_brake_horsepower = 0
        altered_baseline = deepcopy(self.baseline.Building.HeatingVentilationAirConditioningSystems)
        for hvac_system in altered_baseline:
            hvac_system.electric_power_to_fan_motor = 0
            hvac_system.fan_brake_horsepower = 0
        if altered_user == altered_baseline:
            print("  Yes, the other portions of baseline HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, the other portions of baseline HeatingVentilationAirConditioningSystems does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.Building.HeatingVentilationAirConditioningSystems == self.proposed.Building.HeatingVentilationAirConditioningSystems:
            print("  Yes, proposed HeatingVentilationAirConditioningSystems matches user")
        else:
            print("  No, proposed HeatingVentilationAirConditioningSystems does not match user")
            self.proposed_err = True

    def vertical_fenestration_percentage_5c_1(self):
        # Table G3.1 Part 5 - Baseline paragraph (c)
        # Table G3.1.1-1
        table_g3_1_1_1 = {
            "GROCERY_STORE": 0.07,
            "HEALTHCARE_OUTPATIENT": 0.21,
            "HOSPITAL": 0.27,
            "HOTEL_LARGE": 0.24,
            "HOTEL_SMALL": 0.34,
            "OFFICE_SMALL": 0.19,
            "OFFICE_MEDIUM": 0.31,
            "OFFICE_LARGE": 0.40,
            "RESTAURANT_QUICK_SERVICE": 0.34,
            "RESTAURANT_FULL_SERVICE0": 0.24,
            "RETAIL_STAND_ALONE": 0.11,
            "RETAIL_STRIP_MALL": 0.20,
            "SCHOOL_PRIMARY": 0.22,
            "SCHOOL_SECONDARY_AND_UNIVERSITY": 0.22,
            "WAREHOUSE_NON_REFRIGERATED": 0.06
        }
        user_total_floor_area = 0
        user_total_wall_area = 0
        user_total_fenestration_area = 0
        first_building_area_type = self.user.Building.ThermalBlocks[0].building_area_type
        all_area_types_same = True
        for thermal_block in self.user.Building.ThermalBlocks:
            user_total_floor_area += thermal_block.gross_conditioned_floor_area
            if thermal_block.building_area_type != first_building_area_type:
                all_area_types_same = False
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                user_total_wall_area += exterior_above_grade_wall.area
                user_total_fenestration_area += exterior_above_grade_wall.area * exterior_above_grade_wall.vertical_fenestration_percentage / 100

        user_overall_fenestration_fraction = user_total_fenestration_area / user_total_wall_area

        print(f"  User total floor area:              {user_total_floor_area}")
        print(f"  User total wall area:               {user_total_wall_area}")
        print(f"  User total fenestration area:       {user_total_fenestration_area}")
        print(f"  User overall fenestration fraction: {user_overall_fenestration_fraction}")

        if not all_area_types_same:
            print("  Rules not checked that apply to buildings with multiple building types.")
        else:
            if first_building_area_type == "OFFICE":
                if user_total_floor_area <= 5000:
                    first_building_area_type = "OFFICE_SMALL"
                elif user_total_floor_area > 50000:
                    first_building_area_type = "OFFICE_LARGE"
                else:
                    first_building_area_type = "OFFICE_MEDIUM"

            if first_building_area_type in table_g3_1_1_1.keys():
                expected_fenestration_fraction = table_g3_1_1_1[first_building_area_type]
                print(f"  The expected fenestration fraction is {expected_fenestration_fraction} for building type {first_building_area_type}")
                expected_total_fenestration_area = expected_fenestration_fraction * user_total_wall_area
                baseline_total_fenestration_area = 0
                for thermal_block in self.baseline.Building.ThermalBlocks:
                    for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                        baseline_total_fenestration_area += exterior_above_grade_wall.area * exterior_above_grade_wall.vertical_fenestration_percentage / 100
                if self.nearly_equal(expected_total_fenestration_area, baseline_total_fenestration_area, 1):
                    print(f"  Yes, baseline fenestration area {baseline_total_fenestration_area} as expected.")
                else:
                    print(f"  No, baseline fenestration area {baseline_total_fenestration_area} does not match expected fenestration area {expected_total_fenestration_area}")
                    self.proposed_err = True
            else:
                print(f"  Rules not checked that apply to buildings with building type: {first_building_area_type}")

        # remove changing portions to see if rest is the same
        altered_user = deepcopy(self.user.Building.ThermalBlocks)
        for thermal_block in altered_user:
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                exterior_above_grade_wall.vertical_fenestration_percentage = 0
        altered_baseline = deepcopy(self.baseline.Building.ThermalBlocks)
        for thermal_block in altered_baseline:
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                exterior_above_grade_wall.vertical_fenestration_percentage = 0
        if altered_user == altered_baseline:
            print("  Yes, the other portions of baseline ThermalBlocks matches user")
        else:
            print("  No, the other portions of baseline ThermalBlocks does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.Building.ThermalBlocks == self.proposed.Building.ThermalBlocks:
            print("  Yes, proposed ThermalBlocks matches user")
        else:
            print("  No, proposed ThermalBlocks does not match user")
            self.proposed_err = True

    def vertical_fenestration_assembly_5h_1(self):
        # Table G3.1 Part 5 - Baseline paragraph (d) Vertical Fenestration Assemblies
        # Table G3.4-4 Envelope for Climate Zones 4 (A,B,C)
        table_g_4_climate_zone_lookup = {
            "0A": "0A_0B_1A_1B",
            "0B": "0A_0B_1A_1B",
            "1A": "0A_0B_1A_1B",
            "1B": "0A_0B_1A_1B",
            "2A": "2A_2B",
            "2B": "2A_2B",
            "3A": "3A_3B",
            "3B": "3A_3B",
            "3C": "3C",
            "4A": "4A_4B_4C",
            "4B": "4A_4B_4C",
            "4C": "4A_4B_4C",
            "5A": "5A_5B_5C",
            "5B": "5A_5B_5C",
            "5C": "5A_5B_5C",
            "6A": "6A_6B",
            "6B": "6A_6B",
            "7": "7",
            "8": "8"
        }

        table_g3_4_fenestration_assembly = {
            "0A_0B_1A_1B":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 40.0, 1.22, 0.25, 0.28]   # fenestration percentage low, fenestration percentage low, U, SHGC, VT
                    ],
                    "RESIDENTIAL": [
                        [0.0, 40.0, 1.22, 0.25, 0.28]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ]
                },
            "2A_2B":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 40.0, 1.22, 0.25, 0.28]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 10.0, 1.22, 0.39, 0.43],
                        [10.1, 40.0, 1.22, 0.25, 0.28]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "3A_3B":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 10.0, 0.57, 0.39, 0.43],
                        [10.1, 40.0, 0.57, 0.25, 0.28]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 20.0, 0.57, 0.39, 0.43],
                        [20.1, 40.0, 0.57, 0.25, 0.28]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "3C":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 10.0, 1.22, 0.61, 0.67],
                        [10.1, 30.0, 1.22, 0.39, 0.43],
                        [30.1, 40.0, 1.22, 0.34, 0.37]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 20.0, 1.22, 0.61, 0.67],
                        [20.1, 30.0, 1.22, 0.39, 0.43],
                        [30.1, 40.0, 1.22, 0.34, 0.37]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "4A_4B_4C":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "5A_5B_5C":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 10.0, 0.57, 0.49, 0.54],
                        [10.1, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 10.0, 0.57, 0.49, 0.54],
                        [10.1, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "6A_6B":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 10.0, 0.57, 0.49, 0.54],
                        [10.1, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 10.0, 0.57, 0.49, 0.54],
                        [10.1, 40.0, 0.57, 0.39, 0.43]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "7":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 40.0, 0.57, 0.49, 0.54]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 40.0, 0.57, 0.49, 0.54]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                },
            "8":
                {
                    "NONRESIDENTIAL": [
                        [0.0, 40.0, 0.46, 0.40, 0.44]
                    ],
                    "RESIDENTIAL": [
                        [0.0, 40.0, 0.46, 0.40, 0.44]
                    ],
                    "SEMIHEATED": [
                        [0.0, 40.0, 1.22, 0.40, 0.44]
                    ],
                }
        }

        combined_climate_zone = table_g_4_climate_zone_lookup[self.user.climate_zone]
        for thermal_block in self.baseline.Building.ThermalBlocks:
            print(f"  For thermal block{thermal_block.name}")
            if thermal_block.building_area_type == "MULTIFAMILY":
                space_conditioning_category = "RESIDENTIAL"
            elif thermal_block.building_area_type == "WAREHOUSE":
                space_conditioning_category = "SEMIHEATED"
            else:
                space_conditioning_category = "NONRESIDENTIAL"
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                fenestration_percentage = exterior_above_grade_wall.vertical_fenestration_percentage
                if fenestration_percentage > 40:
                    fenestration_percentage = 40
                criteria_options = table_g3_4_fenestration_assembly[combined_climate_zone][space_conditioning_category]
                expected_u_all, expected_shgc_all, expected_vt_all = 0, 0, 0
                for criteria_option in criteria_options:
                    low, high, expected_u_all, expected_shgc_all, expected_vt_all = criteria_option
                    if low < fenestration_percentage < high:
                        break
                for fenestration_assembly in exterior_above_grade_wall.FenestrationAssemblies:
                    if fenestration_assembly.u_factor == expected_u_all:
                        print(f"  Yes, baseline fenestration U factor {expected_u_all} as expected.")
                    else:
                        print(f"  No, baseline fenestration U factor {fenestration_assembly.u_factor} does not match expected fenestration U factor {expected_u_all}")
                        self.proposed_err = True
                    if fenestration_assembly.solar_heat_gain_coefficient == expected_shgc_all:
                        print(f"  Yes, baseline fenestration SHGC {expected_shgc_all} as expected.")
                    else:
                        print(f"  No, baseline fenestration SHGC {fenestration_assembly.solar_heat_gain_coefficient} does not match expected fenestration SHGC {expected_shgc_all}")
                        self.proposed_err = True
                    if fenestration_assembly.visible_transmittance == expected_vt_all:
                        print(f"  Yes, baseline fenestration VT {expected_vt_all} as expected.")
                    else:
                        print(f"  No, baseline fenestration VT {fenestration_assembly.visible_transmittance} does not match expected fenestration VT {expected_vt_all}")
                        self.proposed_err = True

        # remove changing portions to see if rest is the same
        altered_user = deepcopy(self.user.Building.ThermalBlocks)
        for thermal_block in altered_user:
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                for fenestration_assembly in exterior_above_grade_wall.FenestrationAssemblies:
                    fenestration_assembly.u_factor = 0
                    fenestration_assembly.solar_heat_gain_coefficient = 0
                    fenestration_assembly.visible_transmittance = 0
        altered_baseline = deepcopy(self.baseline.Building.ThermalBlocks)
        for thermal_block in altered_baseline:
            for exterior_above_grade_wall in thermal_block.ExteriorAboveGradeWalls:
                for fenestration_assembly in exterior_above_grade_wall.FenestrationAssemblies:
                    fenestration_assembly.u_factor = 0
                    fenestration_assembly.solar_heat_gain_coefficient = 0
                    fenestration_assembly.visible_transmittance = 0
        if altered_user == altered_baseline:
            print("  Yes, the other portions of baseline ThermalBlocks matches user")
        else:
            print("  No, the other portions of baseline ThermalBlocks does not match user")
            self.baseline_err = True

        # user and proposed should match
        if self.user.Building.ThermalBlocks == self.proposed.Building.ThermalBlocks:
            print("  Yes, proposed ThermalBlocks matches user")
        else:
            print("  No, proposed ThermalBlocks does not match user")
            self.proposed_err = True

    @staticmethod
    def nearly_equal(a, b, acceptable_range):
        absolute_difference = abs(a - b)
        # print(f"the absolute difference is {absolute_difference} and range {range}")
        # print(f"so the nearly equal is {absolute_difference < range}")
        return absolute_difference < acceptable_range

import os
import json
import fastjsonschema

from rmrtriplet import RmrTriplet

def validator_for_schema():
    with open("../standard229-ruleset-model-report.schema.json") as schema_file:
        schema229 = json.load(schema_file)
        #print(json.dumps(schema229, indent=4))
    schema_validator = fastjsonschema.compile(schema229)
    return(schema_validator)

def check_rmrs(validator):
    for instance_file in os.scandir("../"):
        if instance_file.path.endswith(".json") and not instance_file.path.endswith(".schema.json"):
            print(instance_file.path)
            with open(instance_file.path, "r") as instance_file:
                instance_229 = json.load(instance_file)
                try:
                    validator(instance_229)
                except fastjsonschema.JsonSchemaException as err:
                    print(err.message)
                    print(f"invalid value {err.value}")
                    print(f"rule broken is {err.rule} and definition is {err.rule_definition}")
                    print()

def recreate_test_cases():
    # exterior lights 6a-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../exterior-lights-test-6a-1-recreated")
    rmr_triplet.baseline.ExteriorLightingAreas[0].power = 150  #should be 150
    rmr_triplet.save_instances()
    rmr_triplet.check_rules(["6a_1",])

    # baseline system selection 18a-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../baseline-system-selection-18a-1-recreated")
    rmr_triplet.user.Building.HeatingVentilationAirConditioningSystems[0].hvac_system_type = "SYSTEM_4_PSZ_HP"
    rmr_triplet.proposed.Building.HeatingVentilationAirConditioningSystems[0].hvac_system_type = "SYSTEM_4_PSZ_HP"
    rmr_triplet.baseline.Building.HeatingVentilationAirConditioningSystems[0].hvac_system_type = "SYSTEM_5_PACKAGED_VAV_WITH_REHEAT"
    rmr_triplet.save_instances()
    rmr_triplet.check_rules(["",])

    # system fan power 19v-4
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../system-fan-power-test-19v-4-recreated")
    rmr_triplet.baseline.Building.HeatingVentilationAirConditioningSystems[0].fan_brake_horsepower = 156
    rmr_triplet.baseline.Building.HeatingVentilationAirConditioningSystems[0].electric_power_to_fan_motor = 122
    rmr_triplet.save_instances()
    rmr_triplet.check_rules(["",])

    # vertical fenestration area 5c-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../vertical-fenestration-area-test-5c-1-recreated")
    rmr_triplet.baseline.Building.ThermalBlocks[0].ExteriorAboveGradeWalls[0].vertical_fenestration_percentage = 19
    rmr_triplet.baseline.Building.ThermalBlocks[1].ExteriorAboveGradeWalls[0].vertical_fenestration_percentage = 19
    rmr_triplet.save_instances()
    rmr_triplet.check_rules(["",])

    # vertical fenestration assembly 5h-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../vertical-fenestration-assembly-test-5h-1-recreated")
    for thermal_block in rmr_triplet.baseline.Building.ThermalBlocks:
        thermal_block.ExteriorAboveGradeWalls[0].FenestrationAssemblies[0].u_factor = 0.57
        thermal_block.ExteriorAboveGradeWalls[0].FenestrationAssemblies[0].solar_heat_gain_coefficient = 0.39
        thermal_block.ExteriorAboveGradeWalls[0].FenestrationAssemblies[0].visible_transmittance = 0.43
    rmr_triplet.save_instances()
    rmr_triplet.check_rules(["",])

if __name__ == '__main__':
    #bad_validate_rmr()
    recreate_test_cases()
    validator = validator_for_schema()
    check_rmrs(validator)



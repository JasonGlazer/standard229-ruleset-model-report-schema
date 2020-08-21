import os
import json
import fastjsonschema
from shutil import copyfile

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

# test method, probably can be deleted
def bad_validate_rmr():
    with open("../standard229-ruleset-model-report.schema.json") as schema_file:
        schema229 = json.load(schema_file)
        #print(json.dumps(schema229, indent=4))
        schema_validator = fastjsonschema.compile(schema229)
        with open("../baseline-system-selection-18a-1.baseline.json") as instance_file:
            instance229 = json.load(instance_file)
            #print(json.dumps(instance229, indent=4))
            instance229["climate-zone"] = "13"
            #print(json.dumps(instance229, indent=4))
            try:
                schema_validator(instance229)
            except fastjsonschema.JsonSchemaException as err:
                print(err.message)
                print(f"invalid value {err.value}")
                print(f"rule broken is {err.rule} and definition is {err.rule_definition}")

def recreate_test_cases():
    # exterior lights 6a-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../exterior-lights-test-6a-1-recreated")
    rmr_triplet.baseline_instance["exterior-lighting-areas"][0]["power"] = 150
    rmr_triplet.save_instances()

    # baseline system selection 18a-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../baseline-system-selection-18a-1-recreated")
    rmr_triplet.user_instance["building"]["hvac-systems"][0]["hvac-system-type"] = "system_4_PSZ-HP"
    rmr_triplet.proposed_instance["building"]["hvac-systems"][0]["hvac-system-type"] = "system_4_PSZ-HP"
    rmr_triplet.baseline_instance["building"]["hvac-systems"][0]["hvac-system-type"] = "system_5_packaged_VAV_with_reheat"
    rmr_triplet.save_instances()

    # system fan power 19v-4
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../system-fan-power-test-19v-4-recreated")
    rmr_triplet.baseline_instance["building"]["hvac-systems"][0]["fan-brake-horsepower"] = 156
    rmr_triplet.baseline_instance["building"]["hvac-systems"][0]["electric-power-to-fan-motor"] = 122
    rmr_triplet.save_instances()

    # vertical fenestration area 5c-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../vertical-fenestration-area-test-5c-1-recreated")
    rmr_triplet.baseline_instance["building"]["thermal-blocks"][0]["exterior-above-grade-walls"][0]["vertical-fenestration-percentage"] = 19
    rmr_triplet.baseline_instance["building"]["thermal-blocks"][1]["exterior-above-grade-walls"][0]["vertical-fenestration-percentage"] = 19
    rmr_triplet.save_instances()

    # vertical fenestration assembly 5h-1
    rmr_triplet = RmrTriplet("../combined-feasibility.user.json", "../vertical-fenestration-assembly-test-5h-1-recreated")
    for thermal_block in rmr_triplet.baseline_instance["building"]["thermal-blocks"]:
        thermal_block["exterior-above-grade-walls"][0]["fenestration-assemblies"][0]["UFactor"] = 0.57
        thermal_block["exterior-above-grade-walls"][0]["fenestration-assemblies"][0]["SHGC"] = 0.39
        thermal_block["exterior-above-grade-walls"][0]["fenestration-assemblies"][0]["visible-transmittance"] = 0.43

    rmr_triplet.save_instances()

if __name__ == '__main__':
    #bad_validate_rmr()
    validator = validator_for_schema()
    check_rmrs(validator)
    recreate_test_cases()



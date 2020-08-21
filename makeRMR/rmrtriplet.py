import os
import json
from shutil import copyfile


class RmrTriplet(object):

    def __init__(self, origin_file_name, triplet_root_name):
        self.origin_file_name = origin_file_name
        self.triplet_root_name = triplet_root_name
        self.user_file_name = triplet_root_name + ".user.json"
        self.proposed_file_name = triplet_root_name + ".proposed.json"
        self.baseline_file_name = triplet_root_name + ".baseline.json"
        self.user_instance = {}
        self.proposed_instance = {}
        self.baseline_instance = {}
        self.create_triplet_instances()

    def create_triplet_instances(self):
        copyfile(self.origin_file_name, self.user_file_name)
        with open(self.user_file_name, "r") as instance_file:
            self.user_instance = json.load(instance_file)
            self.user_instance["transformation-stage"] = "user"
        copyfile(self.origin_file_name, self.proposed_file_name)
        with open(self.proposed_file_name, "r") as instance_file:
            self.proposed_instance = json.load(instance_file)
            self.proposed_instance["transformation-stage"] = "proposed"
        copyfile(self.origin_file_name, self.baseline_file_name)
        with open(self.baseline_file_name, "r") as instance_file:
            self.baseline_instance = json.load(instance_file)
            self.baseline_instance["transformation-stage"] = "baseline"

    def save_instances(self):
        with open(self.user_file_name, "w") as instance_file:
            json.dump(self.user_instance, instance_file, indent=2)
        with open(self.proposed_file_name, "w") as instance_file:
            json.dump(self.proposed_instance, instance_file, indent=2)
        with open(self.baseline_file_name, "w") as instance_file:
            json.dump(self.baseline_instance, instance_file, indent=2)


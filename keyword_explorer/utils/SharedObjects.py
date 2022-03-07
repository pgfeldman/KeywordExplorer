import json
from typing import List, Dict, Any, Type

class SharedObjects:
    object_dict_list:List

    def __init__(self):
        self.object_dict_list = []

    def add_object(self, name:str, obj:Any, obj_type:Type):
        d = {"name":name, "object":obj, "type":obj_type}
        self.object_dict_list.append(d)

    def get_object(self, name) -> Any:
        for d in self.object_dict_list:
            if d['name'] == name:
                return d['object']
        return None

    def contains(self, name) -> bool:
        for d in self.object_dict_list:
            if d['name'] == name:
                return True
        return False

    def load_from_file(self, filename:str):
        """Load the dictionary from a JSON file. Currently sets the type as str
        filename: The name of the file
        """
        print("loading{}".format(filename))
        with open(filename) as f:
            d = json.load(f)
            for key, val in d.items():
                self.add_object(key, val, str)

    def print_contents(self):
        d:Dict
        for d in self.object_dict_list:
            print("name = '{}', type = {}, obj = '{}'".format(d['name'], d['type'], d['object']))

def main():
    so = SharedObjects()
    so.load_from_file("../ids.json")
    so.print_contents()

if __name__ == "__main__":
    main()
import json
from typing import List, Any, Type

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
        print("loading{}".format(filename))
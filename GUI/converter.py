from json import (load as jsonload, dump as jsondump)
import pandas as pd  # pip install pandas openpyxl

class Export:
    """
        Class to convert stuff
        :param token: User token
        :rtype: sg.pin
        """
    def __init__(self):
        self.output = ""
        self.file_types = (".json", ".csv")

    def export_as_json(self, content):
        try:
            with open(self.output, 'w') as f:
                jsondump(content, f)
                f.close()
                return True
        except IOError as e:
            # print("Couldn't open or write to file (%s)." % e) # python 2
            print(f"Couldn't open or write to file ({e})")  # py3 f-strings
            return e

    def export_as_shapefile(self, content):
        print("'")

    def export_as(self, file_type, content):
        if file_type == ".json":
            response = self.export_as_json(content)
            return response
        if file_type == ".csv":
            content.to_csv(self.output)
           # self.export_as_csv(content)

import requests
from json import (load as jsonload, dump as jsondump)
import pandas as pd  # pip install pandas openpyxl


class ContentBuilder:
    """
        Class to convert stuff
        :param token: User token
        :rtype: sg.pin
        """

    def __init__(self):
        self.action_names = ("Gewassen", "Percelen", "Statistiek", "Kaartlagen")
        self.file_types = (".json", ".csv")
        self.field_names = []
        self.field_ids = []

    def get_fields(self, server):
        self.field_names = ["Alle percelen"]
        self.field_ids = [9999]
        fields = server.get_request("fields")
        for field in fields:
            self.field_names.append(field["name"])
            self.field_ids.append(field["id"])

    def get_parameters(self, action_name, field_id):
        action = ""
        field = 9999
        extra = ""
        if action_name == self.action_names[0]:
            action = "crops"
        if action_name == self.action_names[1] or action_name == self.action_names[2]:
            action = "fields"
            if field_id != "Alle percelen":
                field = field_id
        if action_name == self.action_names[2]:
            extra = "statistics"
        if action_name == self.action_names[3]:
            action = "layertypes"
        return {"action_name": action, "field_id": field, "extra": extra}

    def get_content(self, server, action_name, field_id):
        parameters = self.get_parameters(action_name, field_id)
        server.field_id = parameters["field_id"]
        server.extra = parameters["extra"]
        content = server.get_request(parameters["action_name"])  # get raw json content
        if type(content) is dict:
            content = [content]
        return content

    def get_content_df(self, content, data_name):
        headers = []
        data = []

        if data_name == "Gewassen":
            headers = ["Gewastype naam", "Gewas code", "Gewas naam", "Gewas code"]
            for row in content:
                for x in row["crop_varieties"]:
                    data.append([x["name"], x["code"], row["name"], row["code"]])

        if data_name == "Kaartlagen":
            headers = [
                ['id', 'code', 'name', 'type', 'image']
            ]
            for row in content:
                data.append([row["id"], row["code"], row["name"], row["type"], row['image']])

        if data_name == "Percelen":
            headers = ["id",
                       "name",
                       "parcel_id",
                       "location_name",
                       "address.road",
                       "address.town",
                       "address.state",
                       "address.country",
                       "address.postcode",
                       "address.country_code",
                       #      "address.house_number",
                       #      "address.municipality",
                       "address.ISO3166-2-lvl4",
                       "country_code",
                       "properties.area_in_ha",
                       "geometry",
                       "reference_point",
                       "notes_count",
                       "customized_field",
                       "is_editable",
                       "has_parcel",
                       "has_statistics_for_season",
                       #      "seasons.id",
                       #     "seasons.season",
                       #     "seasons.crop_code",
                       #     "seasons.crop_name",
                       #    "seasons.crop_variety_code",
                       #    "seasons.crop_variety_name",
                       #    "seasons.planting_date"
                       ]
            for row in content:
                # for x in row["seasons"]:
                #      print(x)
                data.append([row["id"],
                             row["name"],
                             row["parcel_id"],
                             row["location_name"],
                             row["address"]["road"],
                             row["address"]["town"],
                             row["address"]["state"],
                             row["address"]["country"],
                             row["address"]["postcode"],
                             row["address"]["country_code"],
                             #           row["address"]["house_number"],
                             #              row["address"]["municipality"],
                             row["address"]["ISO3166-2-lvl4"],
                             row["country_code"],
                             row["properties"]["area_in_ha"],
                             row["geometry"],
                             row["reference_point"],
                             row["notes_count"],
                             row["customized_field"],
                             row["is_editable"],
                             row["has_parcel"],
                             row["has_statistics_for_season"],
                             #         row["seasons"][0]["id"],
                             #       row["seasons"][0]["season"],
                             #       row["seasons"][0]["crop_code"],
                             #       row["seasons"][0]["crop_name"],
                             #        row["seasons"][0]["crop_variety_code"],
                             #       row["seasons"][0]["crop_variety_name"],
                             #       row["seasons"][0]["planting_date"]
                             ])
        df = pd.DataFrame(data=data, columns=headers)
        return df

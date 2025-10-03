import json
from datetime import datetime


def date_time_coder(obj: datetime):
    return obj.isoformat()


coder_mapping = {
    datetime: date_time_coder
}


class CustomJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        object_type = type(obj)
        if object_type in coder_mapping.keys():
            return coder_mapping[object_type](obj)
        else:
            return json.JSONEncoder.default(self, obj)

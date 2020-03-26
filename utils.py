import datetime
import json


def find_in_dict(obj, key):
    """
    Recursively find an entry in a dictionary
    Parameters
    ----------
    obj : dict
          The dictionary to search
    key : str
          The key to find in the dictionary
    Returns
    -------
    item : obj
           The value from the dictionary
    """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = find_in_dict(v, key)
            if item is not None:
                return item


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

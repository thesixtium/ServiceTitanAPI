import requests
import re
import read_requests


class Bot:
    api_key = ""
    debug_mode = False

    def __init__(self, api_key, debug_mode=False):
        self.api_key = api_key
        self.debug_mode = debug_mode

    def toggle_debug(self):
        if self.debug_mode:
            self.debug_mode = False
            print("Debug mode is now off")
            print()
        else:
            self.debug_mode = True
            print("Debug mode is now on")
            print()

    def ping(self):
        response = requests.get('https://api.close.com/api/v1/me/', auth=(self.api_key, ''))

        if self.debug_mode:
            print("In 'ping'")
            read_requests.read(response)
            print()

        return response

    def connect(self):
        request_url = 'https://api.close.com/api/v1/me/'

        response = requests.get(request_url, auth=(self.api_key, ''))

        if self.debug_mode:
            print("In 'get_access_token'")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response

    def get_by_address(self, address):
        params = {
            "limit": None,
            "query": {
                "negate": False,
                "queries": [{
                    "negate": False,
                    "object_type": "lead",
                    "type": "object_type"
                },
                    {
                        "negate": False,
                        "queries": [{
                            "negate": False,
                            "related_object_type": "address",
                            "related_query": {
                                "negate": False,
                                "queries": [{
                                    "condition": {
                                        "mode": "full_words",
                                        "type": "text",
                                        "value": address
                                    },
                                    "field": {
                                        "field_name": "location",
                                        "object_type": "address",
                                        "type": "regular_field"
                                    },
                                    "negate": False,
                                    "type": "field_condition"
                                }],
                                "type": "and"
                            },
                            "this_object_type": "lead",
                            "type": "has_related"
                        }],
                        "type": "and"
                    }
                ],
                "type": "and"
            },
            "results_limit": None,
            "sort": []
        }

        response = requests.post('https://api.close.com/api/v1/data/search/', json=params,
                                 auth=(self.api_key, ''))

        decoded_responce = response.content.decode("utf-8")

        if self.debug_mode:
            print(f"In 'get_by_address' with address={address}")
            print(f"Decoded Response: {decoded_responce}")
            read_requests.read(response)
            print()

        for lead in re.finditer('(lead_)[^"]+', decoded_responce):
            self.get_by_lead(lead.group())

    def get_by_lead(self, lead):
        response = requests.get('https://api.close.com/api/v1/lead/' + lead + '/',
                                auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'get_by_lead' with lead={lead}")
            read_requests.read(response)
            print()

        print(response.content)
        print()

    def create_opportunity(self, lead_id, status_id, confidence, value, value_period, note):
        if not isinstance(lead_id, str):
            raise ValueError("Lead ID (first parameter) is not a string")
        if not isinstance(status_id, str):
            raise ValueError("Status ID (second parameter) is not a string")
        if not isinstance(confidence, int):
            raise ValueError("Confidence (third parameter) is not an integer")
        if not isinstance(value, int):
            raise ValueError("Value (fourth parameter) is not an integer")
        if not isinstance(value_period, str):
            raise ValueError("Value Period (fifth parameter) is not a string")
        if not isinstance(note, str):
            raise ValueError("Note (sixth parameter) is not a string")

        params = {
            "note": note,
            "confidence": confidence,
            "lead_id": lead_id,
            "status_id": status_id,
            "value": value,
            "value_period": value_period,
        }

        response = requests.post('https://api.close.com/api/v1/opportunity/', json=params,
                                 auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'create_opportunity'")
            read_requests.read(response)
            print()

        return response.content

    def list_statuses(self):
        response = requests.get('https://api.close.com/api/v1/opportunity/',
                                auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'list_statuses'")
            read_requests.read(response)
            print()

        status_display_names = []
        status_ids = []
        return_dict = {}

        for status_display_name in re.finditer('(?:"status_display_name": ")[^"]*', response.content.decode()):
            status_display_names.append(re.sub('(?:"status_display_name": ")', '', status_display_name.group()))

        for status_id in re.finditer('(?:"status_id": ")[^"]*', response.content.decode()):
            status_ids.append(re.sub('(?:"status_id": ")', '', status_id.group()))

        for i in range(0, len(status_display_names)):
            return_dict[status_display_names[i]] = status_ids[i]

        return return_dict

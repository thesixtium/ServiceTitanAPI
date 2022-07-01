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

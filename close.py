import requests
import re
import read_requests


class Bot:
    api_key = ""
    debug_mode = False

    def __init__(self, api_key, debug_mode=False):
        self.api_key = api_key
        self.debug_mode = debug_mode

    def list_functionalities(self):
        print("Functionalities:")
        print("\t- toggle_debug(): Turns off or on the debugging output")
        print("\t- ping(): Pings Close.io server")
        print("\t- connect(): Tries to connect to Close.io server using auth")
        print("\t- get_by_address(address): Searches for Leads via address")
        print("\t- get_by_lead(lead): Obtains lead information")
        print("\t- create_opportunity(lead_id, status_id, confidence, value, value_period, note): Creates an "
              "opportunity for a given lead")
        print("\t- list_statuses(): List all statuses in a dictionary")
        print("\t- create_note(lead_id, note): Create a note for a Lead")

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

        return_responce = []

        for lead in re.finditer('(lead_)[^"]+', decoded_responce):
            return_responce.append(lead.group())

        return return_responce

    def get_by_lead(self, lead):
        response = requests.get('https://api.close.com/api/v1/lead/' + lead + '/',
                                auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'get_by_lead' with lead={lead}")
            read_requests.read(response)
            print()

        return response.content.decode()

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
            print("Params:")
            print("\t" + str(params))
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

    def create_note(self, lead_id, note):
        if not isinstance(lead_id, str):
            raise ValueError("Lead ID (first parameter) is not a string")
        if not isinstance(note, str):
            raise ValueError("Note (sixth parameter) is not a string")

        params = {
            "note": note,
            "lead_id": lead_id
        }

        response = requests.post('https://api.close.com/api/v1/activity/note/', json=params,
                                 auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'create_note'")
            print("Params:")
            print("\t" + str(params))
            read_requests.read(response)
            print()

        return response.content

    def log_phone_call(self, lead_id, contact_id, created_by, direction, notes, duration, phone_number):
        if not isinstance(lead_id, str):
            raise ValueError("Lead ID (first parameter) is not a string")
        if not isinstance(contact_id, str):
            raise ValueError("Contact ID (second parameter) is not a string")
        if not isinstance(created_by, str):
            raise ValueError("Created By (third parameter) is not a string")
        if not (direction == "outbound" or direction == "inbound"):
            raise ValueError("Direction (fourth parameter) is not 'inbound' or 'outbound'")
        if not isinstance(notes, str):
            raise ValueError("Notes (fifth parameter) is not a string")
        if not isinstance(duration, int):
            raise ValueError("Duration (sixth parameter) is not an int")
        if not isinstance(phone_number, str):
            raise ValueError("Phone Number (seventh parameter) is not a string")

        params = {
            "lead_id": lead_id,
            "contact_id": contact_id,
            "created_by": created_by,
            "user_id": created_by,
            "direction": direction,  # outbound or inbound
            "status": "completed",
            "note": notes,
            "duration": duration,
            "phone": phone_number,
        }

        response = requests.post('https://api.close.com/api/v1/activity/call/', json=params,
                                 auth=(self.api_key, ''))

        if self.debug_mode:
            print(f"In 'log_content'")
            print("Params:")
            print("\t" + str(params))
            read_requests.read(response)
            print()

        return response.content

    def get_contacts_from_lead_info(self, lead_id_info):

        contacts_block = re.findall('"contacts": \[\{(.*?)\], "display_name":', lead_id_info)

        return contacts_block

    def get_contacts_from_lead_id(self, lead_id):
        info = []
        while not info:
            info = self.get_contacts_from_lead_info(self.get_by_lead(lead_id))
        return info

import json
import difflib
import requests
from typing import List


class CloseIO:
    api_key = ""

    def __init__(self, api_key):
        self.api_key = api_key

    # TODO: This isn't getting all addresses for some reason
    def get_close_leads_by_address_string(self, address):
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

        res = json.loads(response.content.decode())

        return_response = []

        if "data" in res:
            for data in res["data"]:
                lead_response = requests.get(
                    f'https://api.close.com/api/v1/lead/{data["id"]}/',
                    auth=(self.api_key, '')
                ).content.decode()

                lead_res = json.loads(lead_response)

                if address in lead_res["display_name"] or address is lead_res["display_name"]:
                    return_lead = {
                        "lead_id": data["id"],
                        "oppo_id": [opportunity["id"] for opportunity in lead_res["opportunities"]]
                    }
                    return_response.append(return_lead)

        return return_response

    def create_close_lead(self, street):

        data = {
            "name": street,
            "addresses": [
                {
                    "country": "Canada",
                }
            ]
        }

        lead_response = requests.post(
            f'https://api.close.com/api/v1/lead/',
            auth=(self.api_key, ''),
            json=data
        ).content.decode()

        lead_res = json.loads(lead_response)

        return [{
            "lead_id": lead_res["id"],
            "oppo_id": []
        }]

    def get_close_leads_by_lead_id(self, id):
        return_response = []

        lead_response = requests.get(
            f'https://api.close.com/api/v1/lead/{id}/',
            auth=(self.api_key, '')
        ).content.decode()

        lead_res = json.loads(lead_response)

        if "opportunities" in lead_res:
            return_lead = {
                "lead_id": id,
                "oppo_id": [opportunity["id"] for opportunity in lead_res["opportunities"]]
            }
        else:
            return_lead = {
                "lead_id": id,
                "oppo_id": []
            }

        return_response.append(return_lead)

        return return_response

    def get_opportunity_info_from_lead(self, lead):
        return_opportunities = []

        if "oppo_id" in lead:
            for opportunity in lead["oppo_id"]:
                opportunity_response = requests.get(
                    f'https://api.close.com/api/v1/opportunity/{opportunity}/',
                    auth=(self.api_key, '')
                ).content.decode()

                opportunity_res = json.loads(opportunity_response)

                if not ("note" in opportunity_res):
                    opportunity_res["note"] = ""

                return_opportunities.append({
                    "lead": lead,
                    "oppo_id": opportunity,
                    "note": opportunity_res["note"]
                })

        return return_opportunities

    def service_titan_job_to_close_oppo(self, service_titan_job, close_lead_id):
        if "note" not in service_titan_job:
            service_titan_job["note"] = ""
        if "value" not in service_titan_job:
            service_titan_job["value"] = 0

        request_body = {
            "note": service_titan_job["note"],
            "confidence": 100,
            "lead_id": close_lead_id,
            "status_id": None,
            "value": int(service_titan_job["value"]),
            "value_period": "monthly"
        }

        return request_body

    def create_opportunity(self, service_titan_job, close_lead_id):
        params = self.service_titan_job_to_close_oppo(service_titan_job, close_lead_id)

        response = requests.post('https://api.close.com/api/v1/opportunity/', json=params,
                                 auth=(self.api_key, ''))

        res = json.loads(response.content.decode())

        if "id" not in service_titan_job:
            service_titan_job["id"] = "UNKNOWN"

        if "lead_name" not in res:
            res["lead_name"] = "UNKNOWN"

        if "lead_id" not in res:
            res["lead_id"] = "UNKNOWN"

        return ["CREATE OPPO", f"{service_titan_job['id']} on {res['lead_name']}: {res['lead_id']}"]

    def patch_opportunity(self, service_titan_job, close_lead_id, opportunity_id):
        params = self.service_titan_job_to_close_oppo(service_titan_job, close_lead_id)
        del params["lead_id"]

        response = requests.put(f'https://api.close.com/api/v1/opportunity/{opportunity_id}', json=params,
                                auth=(self.api_key, ''))

        res = json.loads(response.content.decode())

        if "id" not in service_titan_job:
            service_titan_job["id"] = "UNKNOWN"

        if "lead_name" not in res:
            res["lead_name"] = "UNKNOWN"

        if "lead_id" not in res:
            res["lead_id"] = "UNKNOWN"

        return ["PATCH OPPO", f"{service_titan_job['id']} on {res['lead_name']}: {res['lead_id']}"]

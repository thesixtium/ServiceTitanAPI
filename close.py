import requests
import password


def ping():
    response = requests.get('https://api.close.com/api/v1/me/', auth=(password.get_close_api_key(), ''))

    return response


def connect():
    request_url = 'https://api.close.com/api/v1/me/'

    response = requests.get(request_url, auth=(password.get_close_api_key(), ''))
    print("REQUESTS VALUES")
    print(f"Request URL: {request_url}")
    print()

    return response


def get_by_address(address):
    params = {
        "query": {
            "queries": [
                {
                    "object_type": "contact",
                    "type": "object_type",
                },
                {
                    "type": "field_condition",
                    "field": {
                        "object_type": "contact",
                        "type": "regular_field",
                        "field_name": "title"
                    },
                    "condition": {
                        "type": "text",
                        "mode": "full_words",
                        "value": "CEO"
                    }
                }
            ],
            "type": "and"
        }
    }

    response = requests.get('https://api.close.com/api/v1/data/search/', params=params,
                            auth=(password.get_close_api_key(), ''))

    return response

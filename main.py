import requests
import password
import re


def get_access_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = 'grant_type=client_credentials&client_id=' \
           + password.get_client_id() \
           + '&client_secret=' \
           + password.get_client_secret()

    response = requests.post('https://auth-integration.servicetitan.io/connect/token', headers=headers, data=data)

    return re.search("[t][o][k][e][n][\"][:].?[\"][\S]{130,}[\"]", response.content.decode("utf-8")).group()[8:6139]


def main():

    request_url = 'https://api-integration.servicetitan.io/settings/v2/tenant/985798691/employees'
    access_token = get_access_token()
    app_key = password.get_app_key()

    headers = {
        'Authorization': access_token,
        'ST-App-Key': app_key
    }

    response = requests.get(request_url, headers=headers)

    print("REQUESTS VALUES")
    print(f"Request URL: {request_url}")
    print(f"Headers: {headers}")

    print()

    print("RESPONSE VALUES")
    print(f"Response: {response}")
    print(f"Reason: {response.reason}")
    print(f"Request: {response.request}")
    print(f"Content: {response.content}")
    print(f"URL: {response.url}")
    print(f"Headers: {response.headers}")
    print(f"Status Code: {response.status_code}")


if __name__ == '__main__':
    main()

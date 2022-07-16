import requests
import re
import read_requests
import json


class Bot:
    client_id = ""
    client_secret = ""
    app_key = ""
    tenant_id = ""
    all_customers = []
    debug_mode = False

    def __init__(self, client_id, client_secret, app_key, tenant_id, debug_mode=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_key = app_key
        self.tenant_id = tenant_id
        self.debug_mode = debug_mode

    def toggle_debug(self):
        if self.debug_mode:
            self.debug_mode = False
            print("Debug mode is now off")
        else:
            self.debug_mode = True
            print("Debug mode is now on")

    def get_access_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = 'grant_type=client_credentials&client_id=' \
               + self.client_id \
               + '&client_secret=' \
               + self.client_secret

        response = requests.post('https://auth-integration.servicetitan.io/connect/token', headers=headers, data=data)

        if self.debug_mode:
            print("In 'get_access_token'")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            read_requests.read(response)
            print()

        return re.search("[t][o][k][e][n][\"][:].?[\"][\S]{130,}[\"]", response.content.decode("utf-8")).group()[8:6139]

    def connect(self):
        request_url = 'https://api-integration.servicetitan.io/settings/v2/tenant/' \
                      + self.tenant_id \
                      + '/employees'
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print("In 'connect'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response

    def get_customers_from_page(self, page=1):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/customers?page=' \
                      + str(page)
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_customers_from_page' with 'page={page}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response

    def refresh_customers(self):
        page = 1
        has_more = True
        return_data = []

        if self.debug_mode:
            print("In 'refresh_customers'")

        while has_more:
            if self.debug_mode:
                print(f"On page {page}")

            response = self.get_customers_from_page(page)
            content = response.content.decode()
            ids = re.finditer('[i][d]["][:][^,]*', content)

            for person in ids:
                return_data.append(re.sub('[i][d]["][:]', '', person.group()))
            has_more_var = re.findall('[h][a][s][M][o][r][e]["][:][a-z]*', content)[0][9:]

            if has_more_var == "false":
                has_more = False

            page += 1

        self.all_customers = return_data

        if self.debug_mode:
            print()

    def get_customers(self):
        if self.debug_mode:
            print("In 'get_customers'")
            print(f"Returning {len(self.all_customers)} customers")
            print()
        return self.all_customers

    def get_customer_data(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/Customers/' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_customer_data' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response.content.decode()

    def get_customer_contacts(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/Customers/' \
                      + customer_id \
                      + '/contacts'
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_customer_data' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response.content.decode()

    def get_customer_notes(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/Customers/' \
                      + customer_id \
                      + '/notes'
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_customer_data' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return response.content.decode()

    def get_postal_code_from_customer_id(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/Customers/' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_customer_data' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        return re.findall("[A-Z][0-9][A-Z][.|\s]{0,1}[0-9][A-Z][0-9]", response.content.decode())[0]

    def get_locations_from_customer_id(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/locations?ids&customerId=' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_locations_from_customer_id' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        response = response.content.decode()
        return_responce = []

        response = re.finditer('"street":"[^"]+', response)
        for i in response:
            return_responce.append(re.sub('"street":"', "", i.group()))

        return return_responce

    def get_notes_from_customer_id(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/customers/' \
                      + customer_id \
                      + "/notes"
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_locations_from_customer_id' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        response = response.content.decode()
        responces = []
        response = re.finditer('"text":"[^"]+', response)
        for text in response:
            responces.append(re.sub('"text":"', '', text.group()))

        return responces

    def get_jobs_from_customer_id(self, customer_id):
        request_url = 'https://api-integration.servicetitan.io/jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/jobs?page&customerId=' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        if self.debug_mode:
            print(f"In 'get_locations_from_customer_id' with 'customer_id={customer_id}'")
            print(f"Headers: {headers}")
            print(f"Request URL: {request_url}")
            read_requests.read(response)
            print()

        response = response.content.decode()
        res = json.loads(response)

        print(res)

        return_list = []

        for job in res["data"]:
            job_status = job["jobStatus"]
            completed_on = job["completedOn"]
            summary = job["summary"]
            sold_by = job["customFields"][1]["value"]
            appointments = self.get_appointments_from_job_id(job["id"])
            estimates = self.get_estimates_from_job_id(job["id"])
            return_string = f"https://go.servicetitan.com/#/Job/Index/{job['id']}"

            titles = ["Job ID", "Job Status", "Completed On", "Summary", "Sold By"]
            info = [str(job["id"]), job_status, completed_on, summary, sold_by]

            for i in range(0, len(titles)):
                return_string += titles[i] + ": " + info[i] + "\\n"

            return_string += "Appointments: "
            for appointment in appointments:
                return_string += "\\n\\t- " + appointment

            return_string += "\\nEstimates: "
            for estimate in estimates:
                return_string += "\\n\\t- " + estimate

            return_list.append(return_string)

        return return_list

    def get_appointments_from_job_id(self, job_id):
        request_url = 'https://api-integration.servicetitan.io/jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/appointments?ids&jobId=' \
                      + job_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        append_list = []

        for appointment in res["data"]:
            append_list.append(appointment["id"])

        return append_list

    def get_estimates_from_job_id(self, job_id):
        request_url = 'https://api-integration.servicetitan.io/jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/estimates?ids&jobId=' \
                      + job_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        append_list = []

        for estimate in res["data"]:
            append_list.append(f"https://go.servicetitan.com/#/estimate/{estimate['id']}")

        return append_list

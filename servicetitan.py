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

    def get_access_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = 'grant_type=client_credentials&client_id=' \
               + self.client_id \
               + '&client_secret=' \
               + self.client_secret

        response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
        res = json.loads(response.content.decode())

        return res["access_token"]

    def connect(self):
        request_url = 'https://api.servicetitan.io/settings/v2/tenant/' \
                      + self.tenant_id \
                      + '/employees'
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        return response

    def get_customers_from_page(self, modifiedOnOrAfter, page=1):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/customers?page=' \
                      + str(page) \
                      + '&modifiedOnOrAfter=' \
                      + modifiedOnOrAfter
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        return response

    def refresh_customers(self, modifiedOnOrAfter):
        page = 1
        has_more = True
        return_data = []

        while has_more:

            response = self.get_customers_from_page(modifiedOnOrAfter, page)
            content = response.content.decode()
            ids = re.finditer('[i][d]["][:][^,]*', content)

            for person in ids:
                return_data.append(re.sub('[i][d]["][:]', '', person.group()))
            has_more_var = re.findall('[h][a][s][M][o][r][e]["][:][a-z]*', content)[0][9:]

            if has_more_var == "false":
                has_more = False

            page += 1

        self.all_customers = return_data

    def get_customers(self):

        return self.all_customers

    def get_customer_data(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        return response.content.decode()

    def get_customer_contacts(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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
        res = json.loads(response.content.decode())

        return res["data"]

    def get_customer_notes(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        return response.content.decode()

    def get_postal_code_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        return re.findall("[A-Z][0-9][A-Z][.|\s]{0,1}[0-9][A-Z][0-9]", response.content.decode())[0]

    def get_locations_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        response = response.content.decode()
        return_responce = []

        response = re.finditer('"street":"[^"]+', response)
        for i in response:
            return_responce.append(re.sub('"street":"', "", i.group()))

        return return_responce

    def get_locations_numbers_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        response = response.content.decode()
        return_response = []

        res = json.loads(response)

        for data in res["data"]:
            return_response.append(data["id"])

        return return_response

    def get_notes_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/crm/v2/tenant/' \
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

        response = response.content.decode()
        responces = []
        response = re.finditer('"text":"[^"]+', response)
        for text in response:
            responces.append(re.sub('"text":"', '', text.group()))

        return responces

    def get_jobs_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/jpm/v2/tenant/' \
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

        response = response.content.decode()
        res = json.loads(response)

        return_list = []
        value = 0

        for job in res["data"]:
            completed_on = job["completedOn"]
            summary = job["summary"]
            sold_by = "Unknown"
            if job["customFields"]:
                sold_by = job["customFields"][1]["value"]
            appointments = self.get_appointments_from_job_id(job["id"])
            estimates = self.get_estimates_from_job_id(job["id"])
            invoices = self.get_invoices_from_job_id(job["id"])

            return_string = f"Job URL: https://go.servicetitan.com/#/Job/Index/{job['id']}\n"
            return_string += f'Job ID: {job["id"]}\t|\tSold By: {sold_by}\n'
            return_string += f'Date Completed: {completed_on}\t|\tSummary: {summary}\n'

            return_string += "Appointment ID's: "
            for appointment in appointments:
                return_string += f" {appointment},"

            return_string = return_string[:-1]

            return_string += "\n\nEstimate ID's: "
            for estimate in estimates:
                return_string += f"\n\t- https://go.servicetitan.com/#/estimate/{estimate},"

            return_string = return_string[:-1]

            return_string += "\n\nItems: "
            for item in invoices["items"]:
                return_string += f"\n\t- ${item[1]}: {item[0]} - {item[2]}"

            return_list.append(return_string)
            value += invoices["value"]

        return [return_list, value]

    def get_jobs_from_location_id(self, location_id):
        request_url = f'https://api.servicetitan.io/jpm/v2/tenant/' \
                      f'{self.tenant_id}' \
                      f'/jobs?page&locationId=' \
                      f'{location_id}'

        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)

        response = response.content.decode()
        res = json.loads(response)

        return_list = []
        value = 0

        for job in res["data"]:
            completed_on = job["completedOn"]
            summary = job["summary"]
            sold_by = "Unknown"
            if job["customFields"]:
                sold_by = job["customFields"][1]["value"]
            appointments = self.get_appointments_from_job_id(job["id"])
            estimates = self.get_estimates_from_job_id(job["id"])
            invoices = self.get_invoices_from_job_id(job["id"])

            return_string = f"Job URL: https://go.servicetitan.com/#/Job/Index/{job['id']}\n"
            return_string += f'Job ID: {job["id"]}\t|\tSold By: {sold_by}\n'
            return_string += f'Date Completed: {completed_on}\t|\tSummary: {summary}\n'

            return_string += "Appointment ID's: "
            for appointment in appointments:
                return_string += f" {appointment},"

            return_string = return_string[:-1]

            return_string += "\n\nEstimate ID's: "
            for estimate in estimates:
                return_string += f"\n\t- https://go.servicetitan.com/#/estimate/{estimate},"

            return_string = return_string[:-1]

            return_string += "\n\nItems: "
            for item in invoices["items"]:
                return_string += f"\n\t- ${item[1]}: {item[0]} - {item[2]}"

            return_list.append(return_string)
            value += invoices["value"]

        return [return_list, value]

    def get_invoices_from_job_id(self, job_id):
        request_url = 'https://api.servicetitan.io/accounting/v2/tenant/' \
                      + self.tenant_id \
                      + '/invoices?ids&jobId=' \
                      + str(job_id)
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        return_data = {
            "value": 0,
            "ids": [],
            "items": []
        }

        for invoice in res["data"]:
            return_data["value"] += float(invoice["total"])
            return_data["ids"].append(invoice["id"])
            if invoice["items"]:
                for item in invoice["items"]:
                    if item["serviceDate"]:
                        return_data["items"].append([
                            item["skuName"],
                            item["price"],
                            re.sub("T.*Z", "", item["serviceDate"])
                        ])
                    else:
                        return_data["items"].append([
                            item["skuName"],
                            item["price"],
                            None
                        ])

        return return_data

    def get_appointments_from_job_id(self, job_id):
        request_url = 'https://api.servicetitan.io/jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/appointments?ids&jobId=' \
                      + str(job_id)
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
        request_url = 'https://api.servicetitan.io/sales/v2/tenant/' \
                      + self.tenant_id \
                      + '/estimates?jobId&ids=' \
                      + str(job_id)
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

    def get_projects_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/projects?ids&customerId=' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        return_urls = []

        for project in res["data"]:
            return_urls.append(f"Project: https://go.servicetitan.com/#/project/{project['id']}")

        return return_urls

    def get_invoices_from_customer_id(self, customer_id):
        request_url = 'https://api.servicetitan.io/accounting/v2/tenant/' \
                      + self.tenant_id \
                      + '/invoices?ids&customerId=' \
                      + customer_id
        access_token = self.get_access_token()
        app_key = self.app_key

        headers = {
            'Authorization': access_token,
            'ST-App-Key': app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        return_urls = []

        for invoice in res["data"]:
            return_urls.append(f"Invoice: https://go.servicetitan.com/#/invoice/{invoice['id']}")

        return return_urls

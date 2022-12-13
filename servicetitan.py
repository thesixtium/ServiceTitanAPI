from datetime import datetime
import json
import requests


class ServiceTitan:
    app_key = ""
    tenant_id = ""
    client_id = ""
    access_token = ""
    debug_mode = False
    client_secret = ""
    environment_url = ""

    # Class init
    def __init__(self, client_id, client_secret, app_key, tenant_id, debug_mode=False, production_environment=False):
        if production_environment:
            self.environment_url = "https://api.servicetitan.io/"
        else:
            self.environment_url = "https://api-integration.servicetitan.io/"
        self.client_secret = client_id
        self.client_secret = client_secret
        self.app_key = app_key
        self.tenant_id = tenant_id
        self.debug_mode = debug_mode
        self.access_token = self.get_access_token()

    # Get the access token
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

    # Get all jobs modified within the last _ days
    def get_modified_jobs(self, number_of_days=1):
        request_url = self.environment_url \
                      + 'jpm/v2/tenant/' \
                      + self.tenant_id \
                      + '/jobs'

        headers = {
            'Authorization': self.get_access_token(),
            'ST-App-Key': self.app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        return_jobs = []
        for job in res["data"]:
            modified_on = datetime.strptime(job["modifiedOn"], "%m/%d/%y %H:%M:%S")
            if (modified_on - datetime.now()).days > number_of_days:
                return_jobs.append(self.get_job_invoice_info(job))

        return return_jobs

    # Get the total value of a job and its items based on its invoice
    def get_job_invoice_info(self, job):
        request_url = self.environment_url \
                      + 'accounting/v2/tenant/' \
                      + self.tenant_id \
                      + '/invoices?ids&jobId=' \
                      + str(job["id"])

        headers = {
            'Authorization': self.get_access_token(),
            'ST-App-Key': self.app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        job["total_value"] = 0
        job["items"] = []

        for invoice in res["data"]:
            job["total_value"] += float(invoice["total"])
            if invoice["items"]:
                for item in invoice["items"]:
                    job["items"].append(f"\tItem: {item['skuName']}\n\tPrice: {item['price']}\n")

        return self.get_job_location_info(job)

    def get_job_location_info(self, job):
        request_url = self.environment_url \
                      + 'crm/v2/tenant/' \
                      + self.tenant_id \
                      + '/locations?ids=' \
                      + str(job["locationId"])

        headers = {
            'Authorization': self.get_access_token(),
            'ST-App-Key': self.app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        job["address"] = res['data'][0]['address']

        return job

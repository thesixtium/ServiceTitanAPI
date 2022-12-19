from datetime import datetime
from datetime import timedelta
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

        self.client_id = client_id
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

        if self.environment_url == "https://api.servicetitan.io/":
            response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
        else:
            response = requests.post('https://auth-integration.servicetitan.io/connect/token', headers=headers,
                                     data=data)

        res = json.loads(response.content.decode())

        return res["access_token"]

    # Get all jobs modified within the last _ days
    def get_modified_jobs(self, number_of_days=200, limit_amount=0):
        # 1 index the amount instead of 0 index
        limit_amount -= 1

        # Get the day needed for modifiedOnOrAfter
        today = datetime.now()
        delta = timedelta(days=number_of_days)
        modified_on_or_after = today - delta

        # Initialize needed variables
        page_number = 1
        has_more = True
        return_jobs = []

        # While there are more results to go over
        while has_more:

            # Get response
            request_url = self.environment_url \
                      + 'jpm/v2/tenant/' \
                      + self.tenant_id \
                      + f'/jobs?page={page_number}' \
                        f'&pageSize=8' \
                        f'&modifiedOnOrAfter={modified_on_or_after.isoformat("T")}'

            headers = {
                'Authorization': self.access_token,
                'ST-App-Key': self.app_key
            }

            response = requests.get(request_url, headers=headers)
            response = response.content.decode()
            res = json.loads(response)

            # For every job in the response
            for job in res["data"]:
                # Append to return jobs
                return_jobs.append(self.get_job_invoice_info(job))

                # If limiting amount of jobs, break if over the limit
                if len(return_jobs) > limit_amount > 0:
                    break

            # Increase page number
            page_number += 1

            # Update hasMore variable
            has_more = res["hasMore"]

            # If limiting amount of jobs, break if over the limit
            if len(return_jobs) > limit_amount > 0:
                break

        return return_jobs

    # Get the total value of a job and its items based on its invoice
    def get_job_invoice_info(self, job):
        request_url = self.environment_url \
                      + 'accounting/v2/tenant/' \
                      + self.tenant_id \
                      + '/invoices?ids&jobId=' \
                      + str(job["id"])

        headers = {
            'Authorization': self.access_token,
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
            'Authorization': self.access_token,
            'ST-App-Key': self.app_key
        }

        response = requests.get(request_url, headers=headers)
        response = response.content.decode()
        res = json.loads(response)

        job["address"] = res['data'][0]['address']

        return job

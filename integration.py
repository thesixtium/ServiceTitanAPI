import ServiceTitan
import password

class Integration:
    def servicetitan_jobs_to_close_opportunities(self, jobs):
        modified_jobs = []

        for job in jobs:
            modified_job = {
                "status": job["jobStatus"],
                "estimated_close": job["completedOn"],
                "value": job["total_value"],
                "note": f"Job ID: {job['id']}\n\nJob Items:\n{job['items']}\nST Summary: \n{job['summary']}",
                "address": job["address"]
            }

            modified_jobs.append(modified_job)

        return modified_jobs

    def run(self):
        service_titan_bot = ServiceTitan.ServiceTitan(
            password.get_close_api_key(),
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        jobs = service_titan_bot.get_modified_jobs()
        modified_jobs = self.servicetitan_jobs_to_close_opportunities(jobs)
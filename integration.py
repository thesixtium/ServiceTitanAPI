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

    def test_modified_jobs(self):
        service_titan_bot = ServiceTitan.ServiceTitan(
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        f = open("test_modified_jobs.txt", "w")

        jobs = service_titan_bot.get_modified_jobs(limit_amount=6)
        modified_jobs = self.servicetitan_jobs_to_close_opportunities(jobs)

        f.write("Jobs:\n")
        for job in jobs:
            f.write(f"{job}\n")

        f.write("\n\nModified Jobs:\n")
        for job in modified_jobs:
            f.write(f"{job}\n")

        f.close()

if __name__ == '__main__':
    integration = Integration()
    integration.test_modified_jobs()

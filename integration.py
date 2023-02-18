import CloseIO
import ServiceTitan
import password


class Integration:
    def servicetitan_jobs_to_close_opportunities(self, jobs):
        modified_jobs = []

        for job in jobs:
            modified_job = {
                "id": job['id'],
                "status": job["jobStatus"],
                "estimated_close": job["completedOn"],
                "value": job["total_value"],
                "header": job['id'],
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

    def test_close_get_jobs(self):
        close_io_bot = CloseIO.CloseIO(password.get_close_api_key())
        test_lead = close_io_bot.get_close_leads_by_address_string("64 Springland Way")[0]
        print(f"test_lead: {test_lead}")
        close_io_bot.get_opportunity_info_from_lead(test_lead)

    def run(self):
        # Steps:
        #   0. Set up bots
        service_titan_bot = ServiceTitan.ServiceTitan(
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        close_io_bot = CloseIO.CloseIO(
            password.get_close_api_key()
        )

        #   1. Get all modified jobs from ServiceTitan (clean them with servicetitan_jobs_to_close_opportunities)
        recently_modified_service_titan_jobs = service_titan_bot.get_modified_jobs(limit_amount=6)
        cleaned_modified_service_titan_jobs = self.servicetitan_jobs_to_close_opportunities(
            recently_modified_service_titan_jobs
        )

        #   2. Map each job to a Close location (and for each Close location, get all opportunity notes)
        service_titan_jobs_to_close_locations = []
        for job in cleaned_modified_service_titan_jobs:
            leads = close_io_bot.get_close_leads_by_address_string(job["address"])
            opportunities = []

            for lead in leads:
                lead_opportunities = close_io_bot.get_opportunity_info_from_lead(lead)
                for lead_opportunity in lead_opportunities:
                    opportunities.append(lead_opportunity)

            service_titan_jobs_to_close_locations.append({
                "job": job,
                "opportunities": opportunities
            })

        #   3. See if each ServiceTitan modified job is in Close via Job ID matching
        changes = []
        for match in service_titan_jobs_to_close_locations:
            match_job_id = match["job"]["id"]
            for opportunity in match["opportunities"]:
                if match_job_id not in opportunity["note"]:
                    #   4. If modified job not found, add jobs as new opportunity
                    changes.append(close_io_bot.create_opportunity(match["job"], opportunity["lead_id"]))
                else:
                    #   5. If modified job found, update it
                    changes.append(
                        close_io_bot.patch_opportunity(match["job"], opportunity["lead_id"], opportunity["oppo_id"]))

        #   6. Return update log
        with open("log.txt", "w") as text_file:
            for change in changes:
                print(change)
                text_file.write(change)

    def test(self):
        # Steps:
        #   0. Set up bots
        service_titan_bot = ServiceTitan.ServiceTitan(
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        close_io_bot = CloseIO.CloseIO(
            password.get_close_api_key()
        )

        #   1. Get all modified jobs from ServiceTitan (clean them with servicetitan_jobs_to_close_opportunities)
        recently_modified_service_titan_jobs = [
            service_titan_bot.get_test_job(18955686)[0],
            service_titan_bot.get_test_job(18955723)[0],
            service_titan_bot.get_test_job(18955737)[0],
            service_titan_bot.get_test_job(18955734)[0],
            service_titan_bot.get_test_job(18955731)[0],
            service_titan_bot.get_test_job(18955724)[0]
        ]
        cleaned_modified_service_titan_jobs = self.servicetitan_jobs_to_close_opportunities(
            recently_modified_service_titan_jobs
        )
        print(f"#1. Number of Modified Jobs: {len(cleaned_modified_service_titan_jobs)}")

        #   2. Map each job to a Close location (and for each Close location, get all opportunity notes)
        service_titan_jobs_to_close_locations = []
        for job in cleaned_modified_service_titan_jobs:
            leads = close_io_bot.get_close_leads_by_address_string(job["address"]["street"])

            for lead in leads:
                opportunities = []
                lead_opportunities = close_io_bot.get_opportunity_info_from_lead(lead)
                for lead_opportunity in lead_opportunities:
                    opportunities.append(lead_opportunity)

                service_titan_jobs_to_close_locations.append({
                    "lead_id": lead["lead_id"],
                    "job": job,
                    "opportunities": opportunities
                })
        print(f"#2. Job, Lead, Opportunity Mappings: {len(service_titan_jobs_to_close_locations)}")
        for i in range(len(service_titan_jobs_to_close_locations)):
            print(f"\t\tJob {i+1} with lead ID {service_titan_jobs_to_close_locations[i]['lead_id']} has"
                  f" {len(service_titan_jobs_to_close_locations[i]['opportunities'])} opportunities")

        #   3. See if each ServiceTitan modified job is in Close via Job ID matching
        changes = []

        for match in service_titan_jobs_to_close_locations:
            if "lead_id" not in match:
                continue
            if "job" not in match:
                continue
            if "opportunities" not in match:
                continue

            lead_id = match["lead_id"]
            match_job_id = match["job"]["id"]
            opportunity_found = False
            print(f"\t\t{lead_id}")

            #TODO: What if no location exists / other edge cases
            for opportunity in match["opportunities"]:
                if ("note" not in opportunity or str(match_job_id) in opportunity["note"]) and not opportunity_found:
                    opportunity_found = True
                    #   5. If modified job found, update it
                    changes.append(close_io_bot.patch_opportunity(match["job"], lead_id, opportunity["oppo_id"]))
                    print(f"\t\t\t\tPATCH")
                    print(f"\t\t\t\t{len(changes)}: {changes[-1]} [{match['job']}, "
                          f"{lead_id}, {opportunity['oppo_id']}]")
            if not opportunity_found:
                #   4. If modified job not found, add jobs as new opportunity
                changes.append(close_io_bot.create_opportunity(match["job"], lead_id))
                print(f"\t\t\t\tCREATE")

        print(f"#3. Changes: {len(changes)}")
        for i in range(len(changes)):
            print(f"\t\tChange {i + 1}: {changes[i]}")

        #   6. Return update log
        with open("log.txt", "w") as text_file:
            for change in changes:
                text_file.write(change)
                text_file.write("\n")


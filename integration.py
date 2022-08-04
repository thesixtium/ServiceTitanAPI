import close
import servicetitan
import re
import json

'''
Make sure to map from ST ADDRESS to Close ADDRESS
Make sure opportunities are made, not notes
'''


class Bot:
    close_bot = None
    service_titan_bot = None
    debug_mode = False

    def __init__(self, close_api_key, st_client_id, st_client_secret,
                 st_app_key, st_tenant_id, debug_mode=False):
        self.close_bot = close.Bot(close_api_key)
        self.service_titan_bot = servicetitan.Bot(
            st_client_id,
            st_client_secret,
            st_app_key,
            st_tenant_id
        )

        self.debug_mode = debug_mode

    def map_single_st_customer_to_close_lead(self, customer_number):
        locations = self.service_titan_bot.get_locations_from_customer_id(customer_number)

        close_locations = []

        for location in locations:
            addresses = self.close_bot.get_by_address(location)
            if not addresses:
                addresses = [self.close_bot.create_lead(location)]
            pattern = re.compile(location)
            for address in addresses:
                response = self.close_bot.get_by_lead(address)
                res = json.loads(response)
                if pattern.match(res["display_name"]):
                    close_locations.append([customer_number, address])

        return close_locations

    def check_pair(self, pair_to_check):
        self.check_contact_info(pair_to_check)
        self.check_notes(pair_to_check)
        self.check_jobs(pair_to_check)
        self.check_projects(pair_to_check)
        self.check_invoices(pair_to_check)

    def check_contact_info(self, pair_to_check):
        print("\nChecking Contact Info")
        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        st_contact = self.service_titan_bot.get_customer_contacts(st_customer)
        st_phones = []
        for phone in st_contact:
            st_phones.append(re.sub("[^0-9]", "", phone["phoneSettings"]["phoneNumber"]))

        close_contacts = self.close_bot.get_contacts_from_lead_id(close_lead)

        for close_contact in close_contacts:
            close_phones = []
            for phone in close_contact["phones"]:
                close_phones.append(re.sub("[^0-9]", "", phone["phone"]))

            untouched = True
            for number in st_phones:
                if number not in close_phones:
                    print(f"Need to add {number}")
                    self.close_bot.add_phone(close_lead, number)
                    untouched = False

            if untouched:
                print("No additions needed")

    def check_notes(self, pair_to_check):
        print("\nCheck Notes")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        st_notes = self.service_titan_bot.get_notes_from_customer_id(st_customer)
        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)

        self.check_things(close_lead, close_notes, st_notes)

    def check_jobs(self, pair_to_check):
        print("\nCheck Jobs")

        '''
        Job info by way of Link to https://go.servicetitan.com/#/Job/Index/33027507
        AND info on :  
        •	Job Status
        •	Job SoldBy
        •	Job Completed on
        •	Job Summary
        •	{tenant}/appointments          info
        '''

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_jobs_from_customer_id(st_customer)

        self.check_things(close_lead, close_notes, st_jobs, also_add_opp=True)

    def check_projects(self, pair_to_check):
        print("\nCheck Projects")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_projects_from_customer_id(st_customer)

        self.check_things(close_lead, close_notes, st_jobs)

    def check_invoices(self, pair_to_check):
        print("\nCheck Invoices")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_invoices_from_customer_id(st_customer)

        self.check_things(close_lead, close_notes, st_jobs)

    def get_all_customers(self, modifiedOnOrAfter):
        self.service_titan_bot.refresh_customers(modifiedOnOrAfter)
        return self.service_titan_bot.get_customers()

    def check_things(self, close_lead, close_stuff, st_stuff, also_add_opp=False):
        value = 0
        if also_add_opp:
            value = st_stuff[1]
            st_stuff = st_stuff[0]

        untouched = True
        for note in st_stuff:
            note2 = note.replace("\n", "\\n").replace("\t", "\\t")[:-1]
            note3 = note.replace("\t", "\\t")[:-1]
            note4 = note.replace("\n", "\\n")[:-1]
            note5 = note.replace("\n", "\\n").replace("\t", "\\t")
            note6 = note.replace("\t", "\\t")
            note7 = note.replace("\n", "\\n")
            if note not in close_stuff \
                    and note2 not in close_stuff \
                    and note3 not in close_stuff \
                    and note4 not in close_stuff \
                    and note5 not in close_stuff \
                    and note6 not in close_stuff \
                    and note7 not in close_stuff:
                flag = True
                for item in close_stuff:
                    if note in item or note2 in item:
                        flag = False
                if flag:
                    print("Need to Add A Note")
                    print(f"\t'{note}'")
                    self.close_bot.create_note(close_lead, note)
                    if also_add_opp:
                        self.close_bot.create_opportunity(
                            close_lead,
                            "stat_gRPUDopxzt6p7bLbXtes2xoD2Rv09toRNWcKJN6nDrc",
                            50,
                            int(value),
                            "one_time",
                            note)

                    untouched = False

        if untouched:
            print("No additions needed")

import close
import servicetitan
import re

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
            for address in addresses:
                close_locations.append([customer_number, address])

        return close_locations

    def check_pair(self, pair_to_check):
        '''
        Opportunity info by way of Link to https://go.servicetitan.com/#/Opportunity/33027509

        Project info by way of Link to https://go.servicetitan.com/#/project/33027506  (if exists, most times unlikely)

        Invoice info (from accounting)
        '''
        # self.check_contact_info(pair_to_check)
        # self.check_notes(pair_to_check)
        self.check_jobs(pair_to_check)

    def check_contact_info(self, pair_to_check):
        print("Checking Contact Info")
        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_contacts = self.close_bot.get_contacts_from_lead_id(close_lead)
        for close_contact in close_contacts:
            print(close_contact)
            close_contact_id = str(close_contact[0])
            close_contact = close_contact[1]
            st_contact = str(self.service_titan_bot.get_customer_contacts(st_customer))

            print(close_contact)
            print(st_contact)

            st_numbers = []
            st_numbers_matching_patterns = ['"type":"Phone","value":"', '"phoneNumber":"']

            close_numbers = []
            close_numbers_matching_patterns = ['"phone": "\+1', '"phoneNumber":"']

            for pattern in st_numbers_matching_patterns:
                for match in re.finditer(pattern + '[^"]+', st_contact):
                    number = re.sub(pattern, "", match.group())
                    if number not in st_numbers:
                        st_numbers.append(number)

            for pattern in close_numbers_matching_patterns:
                for match in re.finditer(pattern + '[^"]+', close_contact):
                    number = re.sub(pattern, "", match.group())
                    if number not in close_numbers:
                        close_numbers.append(number)

            untouched = True
            for number in st_numbers:
                if number not in close_numbers:
                    print(f"Need to add {number}")
                    untouched = False

            if untouched:
                print("No additions needed")

        print()

    def check_notes(self, pair_to_check):
        print("Check Notes")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        st_notes = self.service_titan_bot.get_notes_from_customer_id(st_customer)
        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)

        print(st_notes)
        print(close_notes)

        untouched = True
        for note in st_notes:
            if note not in close_notes:
                print(f"Need to add {note}")
                untouched = False

        if untouched:
            print("No additions needed")

        print()

    def check_jobs(self, pair_to_check):
        print("Check Notes")

        '''
        Job info by way of Link to https://go.servicetitan.com/#/Job/Index/33027507
        AND info on :  
        ???	Job Status
        ???	Job SoldBy
        ???	Job Completed on
        ???	Job Summary
        ???	{tenant}/appointments          info
        '''

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_jobs_from_customer_id(st_customer)

        untouched = True
        for note in st_jobs:
            if note not in close_notes:
                print(f"Need to add {note}")
                untouched = False

        if untouched:
            print("No additions needed")
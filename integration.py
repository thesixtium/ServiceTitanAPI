import re
import json
import close
import servicetitan
from integration_logger import log


# Screenshot of oppertunity update to Mike
# Make test run on a small sample of leads


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
        log(f"Mapping ST {customer_number} to Close lead(s)")

        """
        Get array of the addresses within a service titan customer
            For each ST Address, search Close for the ST Address and make an array of the resulting lead ids
            For each lead id, get the information
            If the address matches, append the ST Number and the close id to the array 
        
        Return Array:
            1. close_locations in the format of an array of [customer_number, address]
            2. New mappings
            3. Location duplicates
            4. Any locations that should be mapped but aren't
            5. Error locations
        
        Location plan:
            Switch search_from_url to location things
            Get locations from ST number
        """

        close_locations = []
        new_mappings = []
        location_duplicates = []
        non_mapped_locations = []
        error_locations = []

        log(f"Searching from url {customer_number} for the first time...")
        all_st_location_numbers = self.service_titan_bot.get_locations_numbers_from_customer_id(customer_number)

        for st_location_number in all_st_location_numbers:
            search_from_url = self.close_bot.get_location_by_st_lead_id(
                st_location_number)  # Needs to change to getting locations (search by location, not lead)
            log(f"Search complete, here are the results:\n{search_from_url}")

            log(f"Searching locations from {customer_number}...")
            locations = self.service_titan_bot.get_locations_from_customer_id(customer_number)
            log(f"Search completed, here are the results:{locations}")

            for location in locations:
                log(f"On location {location}")
                log(f"Searching addresses from {location}...")

                # Search for each address string in Close
                addresses = self.close_bot.get_by_address(location)
                log(f"Search completed, here are the results: {addresses}")

                if not addresses:
                    log("No addresses found, making new lead now")
                    addresses = [self.close_bot.create_lead(location)]
                pattern = re.compile(location)

                if addresses != 1:
                    log("Duplicate addresses detected")
                    location_duplicates = addresses

                for address in addresses:
                    log(f"Searching for lead information for {address}...")
                    response = self.close_bot.get_by_lead(address)
                    res = json.loads(response)
                    log(f"Search completed, here are the results:\n{res}")
                    if pattern.match(res["display_name"]):
                        if len(search_from_url) == 0:
                            log(
                                f"Need to map Close {address} to ST {customer_number}'s location {st_location_number}...")  # Make locations
                            new_mappings.append([f"ST Customer: {customer_number}",
                                                 f"ST Location: {st_location_number}",
                                                 f"Close Lead: {address}"])
                        else:
                            if address not in search_from_url:
                                log(
                                    f"Close {address} not mapped to {customer_number}'s location {st_location_number}...")  # Make locations
                                non_mapped_locations.append([f"ST Customer: {customer_number}",
                                                             f"ST Location: {st_location_number}",
                                                             f"Close Lead: {address}"])

                for close_lead in new_mappings:
                    log(f"Mapping {close_lead} to {customer_number}'s location {st_location_number}...")
                    self.close_bot.add_or_update_st_lead_id(
                        re.sub(
                            "Close Lead: ",
                            "",
                            close_lead[2]
                        ),
                        st_location_number
                    )

            log(f"Searching from url {customer_number} for the second time...")
            search_from_url = self.close_bot.get_by_st_lead_id(customer_number)
            log(f"Search complete, here are the results: {search_from_url}")

            if len(search_from_url) == 0:
                error_locations = new_mappings

            for item in search_from_url:
                log(f"Adding {[customer_number, item]} to close_locations array...")
                close_locations.append([st_location_number, item])

        return_array = [close_locations, new_mappings, location_duplicates, non_mapped_locations, error_locations]
        log(f"Returning following array: {return_array}")

        return return_array

    def check_pair(self, pair_to_check):
        changed = False

        '''if self.check_contact_info(pair_to_check):
            changed = True'''
        '''if self.check_notes(pair_to_check):
            changed = True'''
        if self.check_jobs(pair_to_check):
            changed = True
        '''if self.check_projects(pair_to_check):
            changed = True
        if self.check_invoices(pair_to_check):
            changed = True'''

        return changed

    def check_contact_info(self, pair_to_check):
        log(f"Checking Contact Info for {pair_to_check}")
        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        st_contact = self.service_titan_bot.get_customer_contacts(st_customer)
        st_phones = []
        for phone in st_contact:
            if phone['phoneSettings']:
                st_phones.append(re.sub("[^0-9]", "", phone["phoneSettings"]["phoneNumber"]))

        close_contacts = self.close_bot.get_contacts_from_lead_id(close_lead)

        all_untouched = True

        for close_contact in close_contacts:
            close_phones = []
            for phone in close_contact["phones"]:
                close_phones.append(re.sub("[^0-9]", "", phone["phone"]))

            untouched = True
            added_phones = []
            for number in st_phones:
                if number not in close_phones and number not in added_phones:
                    log(f"Need to add {number} for {pair_to_check}")
                    added_phones.append(number)
                    self.close_bot.add_phone(close_lead, number)
                    untouched = False

            if untouched:
                log(f"No additions needed for {pair_to_check}")
            else:
                all_untouched = False

        return not all_untouched

    def check_notes(self, pair_to_check):
        log(f"Check Notes for {pair_to_check}")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        st_notes = self.service_titan_bot.get_notes_from_customer_id(st_customer)
        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)

        return self.check_things(close_lead, close_notes, st_notes)

    def check_jobs(self, pair_to_check):
        log(f"Check Jobs for {pair_to_check}")

        '''
        Job info by way of Link to https://go.servicetitan.com/#/Job/Index/33027507
        AND info on :  
        •	Job Status
        •	Job SoldBy
        •	Job Completed on
        •	Job Summary
        •	{tenant}/appointments          info
        '''

        st_location = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_jobs_from_location_id(st_location)

        return self.check_things(close_lead, close_notes, st_jobs, also_add_opp=True)

    def check_projects(self, pair_to_check):
        log(f"Check Projects for {pair_to_check}")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_projects_from_customer_id(st_customer)

        return self.check_things(close_lead, close_notes, st_jobs)

    def check_invoices(self, pair_to_check):
        log(f"Check Invoices for {pair_to_check}")

        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_notes = self.close_bot.get_notes_from_lead_id(close_lead)
        st_jobs = self.service_titan_bot.get_invoices_from_customer_id(st_customer)

        return self.check_things(close_lead, close_notes, st_jobs)

    def get_all_customers(self, modifiedOnOrAfter):
        self.service_titan_bot.refresh_customers(modifiedOnOrAfter)
        return self.service_titan_bot.get_customers()

    def check_things(self, close_lead, close_stuff, st_stuff, also_add_opp=False):
        value = 0
        if also_add_opp:
            value = st_stuff[1]
            st_stuff = st_stuff[0]

        close_refactored = []

        for i in close_stuff:
            close_refactored.append(re.sub("[^a-zA-Z0-9]", "", str(i)))

        untouched = True
        for note in st_stuff:
            note_refactored = re.sub("[^a-zA-Z0-9]", "", str(note))
            if note_refactored not in close_refactored:
                log(f"Need to Add A Note: '{note}'")
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
            log(f"No additions needed for {close_lead}")

        return not untouched

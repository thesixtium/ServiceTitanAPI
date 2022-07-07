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

    def check_contact_info(self, pair_to_check):
        st_customer = pair_to_check[0]
        close_lead = pair_to_check[1]

        close_contact = self.close_bot.get_contacts_from_lead_id(close_lead)
        st_contact = self.service_titan_bot.get_customer_contacts(st_customer)

        close_contact = self.close_bot.get_contacts_from_lead_id(close_lead)
        st_contact = self.service_titan_bot.get_customer_contacts(st_customer)

        print(close_contact)
        print(st_contact)

        st_numbers = []
        st_numbers_matching_patterns = ['"type":"Phone","value":"', '"phoneNumber":"']

        for pattern in st_numbers_matching_patterns:
            for match in re.finditer(pattern + '[^"]+', st_contact):
                number = re.sub(pattern, "", match.group())
                if number not in st_numbers:
                    st_numbers.append(number)

        print(st_numbers)

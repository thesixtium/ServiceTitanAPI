import close
import servicetitan
import password

def main():
    '''
    # 'Marketing: Digital Lead \\u2013 AC whole home', 'stat_xCZrL25PGU4hpPP4JsoVPAQxcPIlMn6EQVCH9FoVidV'

    me = password.get_me()

    close_bot = close.Bot(password.get_close_api_key())

    lead = close_bot.get_by_lead(me)
    close_bot.get_contacts_from_lead_info(lead)
    '''

    service_titan_bot = servicetitan.Bot(
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    service_titan_bot.refresh_customers()

    print(service_titan_bot.get_customer_data(service_titan_bot.get_customers()[7]))


if __name__ == '__main__':
    main()

'''
Make these modules into full frameworks (like clients that can be used)
'''
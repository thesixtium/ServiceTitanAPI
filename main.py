import integration
import password

def main():
    integration_bot = integration.Bot(
        password.get_close_api_key(),
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    me = password.get_me()

    customer = "17991716"

    pair = integration_bot.map_single_st_customer_to_close_lead(customer)

    integration_bot.check_contact_info(pair[0])


if __name__ == '__main__':
    main()

'''
Make these modules into full frameworks (like clients that can be used)
'''
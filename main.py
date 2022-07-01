import close
import servicetitan
import password

def main():
    # close.get_by_address("64 Springland Way")

    service_titan_bot = servicetitan.Bot(
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    service_titan_bot.toggle_debug()

    service_titan_bot.get_customer_data(service_titan_bot.get_customers()[7])

if __name__ == '__main__':
    main()

'''
Make these modules into full frameworks (like clients that can be used)
'''
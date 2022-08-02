import integration
import password
import datetime

def main():
    integration_bot = integration.Bot(
        password.get_close_api_key(),
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    # When status on job is finished, need to change Close opp to won
    # Notes appointments: Make links instead of just ID's
    # Make sure events (notes) get added chronologically
    # Put custom field in close of ST mapping
    # Currently doesn't check if won or not
    # For opps use the won, invoiced, completed, etc statuses PROPERLY on the opps w/ patch requests
    # SWITCH OVER TO PRODUCTION INVIROMENT, NOT INTEGRATION

    customer = "22965632"
    pair = integration_bot.map_single_st_customer_to_close_lead(customer)
    print(f"Pair: {pair}")
    integration_bot.check_pair(pair[0])

def run(first=False):
    if first:
        integration_bot = integration.Bot(
            password.get_close_api_key(),
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        date = datetime.datetime(2022, 4, 30)

        all_customers = integration_bot.get_all_customers(date)

        for customer in all_customers:
            pair = integration_bot.map_single_st_customer_to_close_lead(customer)
            for p in pair:
                integration_bot.check_pair(p)

    while True:
        now = datetime.datetime.now()
        if now.hour == 12 and now.minute == 0:
            integration_bot = integration.Bot(
                password.get_close_api_key(),
                password.get_client_id(),
                password.get_client_secret(),
                password.get_app_key(),
                password.get_tenant_id()
            )

            today = datetime.datetime.now(datetime.timezone.utc)
            delta = datetime.timedelta(days=14)
            two_weeks_ago = (today - delta).isoformat()

            all_customers = integration_bot.get_all_customers(two_weeks_ago)

            for customer in all_customers:
                pair = integration_bot.map_single_st_customer_to_close_lead(customer)
                for p in pair:
                    print(p)
                    integration_bot.check_pair(p)

if __name__ == '__main__':
    main()
    # run()

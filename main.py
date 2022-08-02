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

    '''
    all_customers = integration_bot.get_all_customers()
    print(len(all_customers))

    for customer in all_customers:
        pair = integration_bot.map_single_st_customer_to_close_lead(customer)
        for p in pair:
            print(p)
            integration_bot.check_pair(p)
    '''

    # When status on job is finished, need to change Close opp to won
    # Notes appointments: Make links instead of just ID's
    # Make sure events (notes) get added chronologically
    # Put custom field in close of ST mapping
    # Currently doesn't check if won or not
    # Make the price of the service items be the title
    # For opps use the won, invoiced, completed, etc statuses PROPERLY on the opps w/ patch requests
    # SWITCH OVER TO PRODUCTION INVIROMENT, NOT INTEGRATION

    customer = "22965632"
    pair = integration_bot.map_single_st_customer_to_close_lead(customer)
    print(pair)
    integration_bot.check_pair(pair[0])


if __name__ == '__main__':
    main()

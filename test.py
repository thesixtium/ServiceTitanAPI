import integration
import password
import datetime
from time import sleep
import analytics
from integration_logger import log


def main():
    while True:
        today = datetime.datetime.now(datetime.timezone.utc)
        delta = datetime.timedelta(days=1)
        yesterday = (today - delta).isoformat()
        if today.hour == (12 + 2) and today.minute == 0:
            test(yesterday)
        else:
            print(f"Not 14:00, currently {today.hour}:{today.minute}")
            sleep(40)


def test(yesterday):
    integration_bot = integration.Bot(
        password.get_close_api_key(),
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    all_customers = integration_bot.get_all_customers(yesterday)
    log(f"All customers are:")
    for customer in all_customers:
        log(f"\t - {customer}")

    all_people = []
    all_analytics = []
    analytics_new_mappings = []
    analytics_location_duplicates = []
    analytics_non_mapped_locations = []
    analytics_error_locations = []
    changes = []

    log("New Run")
    log("Integration start")
    log("Starting to go through all customers")

    for customer in all_customers:
        log(f"Starting on customer {customer}")
        results = integration_bot.map_single_st_customer_to_close_lead(customer)
        pair = results[0]
        log(f"{customer} pair is {pair}")
        analytics_new_mappings.append(results[1])
        analytics_location_duplicates.append(results[2])
        analytics_non_mapped_locations.append(results[3])
        analytics_error_locations.append(results[4])
        for p in pair:
            log(f"Working on customer {customer} and pair {p}")
            if integration_bot.check_pair(p):
                changes.append(p[1])
            all_people.append(p)
            all_analytics.append(p[1])

    changes = [
        changes,
        analytics_new_mappings,
        analytics_location_duplicates,
        analytics_non_mapped_locations,
        analytics_error_locations
    ]

    analytics.run(all_analytics, changes)
    log("")


if __name__ == '__test__':
    main()

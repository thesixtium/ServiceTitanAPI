import integration
import password
import datetime
from time import sleep
import threading
import numpy as np
import analytics
from integration_logger import log


def main(cores, first=False):
    if first:
        date = datetime.datetime(2022, 5, 30)
        go(date, cores)

    while True:
        today = datetime.datetime.now(datetime.timezone.utc)
        delta = datetime.timedelta(days=4)
        two_weeks_ago = (today - delta).isoformat()
        if today.hour == (12 + 2) and today.minute == 0:
            go(two_weeks_ago, cores)
        else:
            print(f"Not 14:00, currently {today.hour}:{today.minute}")
            sleep(40)


thread_analytics = []
thread_changes = []

all_people = []
        all_analytics = []
        analytics_new_mappings = []
        analytics_location_duplicates = []
        analytics_non_mapped_locations = []
        analytics_error_locations = []
        changes = []


def go(date, cores):
    integration_bot = integration.Bot(
        password.get_close_api_key(),
        password.get_client_id(),
        password.get_client_secret(),
        password.get_app_key(),
        password.get_tenant_id()
    )

    all_customers = integration_bot.get_all_customers(date)

    if len(all_customers) < cores:
        cores = 1

    np_customers = np.array(all_customers)
    split_customers = np.array_split(np_customers, cores)

    global thread_analytics
    global thread_changes

    threads = []
    thread_analytics = [[] for _ in range(cores)]
    thread_changes = [[] for _ in range(cores)]

    for i in range(0, cores):
        threads.append(myThread(split_customers[i], integration_bot, i))
        threads[i].name = f"Thread {i}"
        threads[i].start()

    for i in range(0, 10):
        for thread in threads:
            while thread.is_alive():
                pass

    all_people = []
    all_analytics = []
    analytics_new_mappings = []
    analytics_location_duplicates = []
    analytics_non_mapped_locations = []
    analytics_error_locations = []
    changes = []

    for result in thread_analytics:
        for entry in result:
            log(f"Adding analytic: {entry}")
            all_analytics.append(entry)

    for change in thread_changes:
        for entry in change:
            log(f"Adding change: {change}")
            all_changes.append(entry)

    analytics.run(all_analytics, all_changes)


class myThread(threading.Thread):
    def __init__(self, all_customers, integration_bot, i):
        threading.Thread.__init__(self)
        self.integration_bot = integration_bot
        self.all_customers = all_customers
        self.i = i

    def run(self):
        global thread_analytics
        global thread_changes

        for customer in self.all_customers:
            log(f"On customer {customer} for {self.name}")
            pair = self.integration_bot.map_single_st_customer_to_close_lead(customer)
            for p in pair:
                log(f"On pair {pair} for {self.name}")
                thread_analytics[self.i].append(p[1])
                if self.integration_bot.check_pair(p):
                    thread_changes[self.i].append(p[1])


def test():
    for i in range(0, 10):

        integration_bot = integration.Bot(
            password.get_close_api_key(),
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )

        all_customers = [
            "22965632",
            "17992953",
            "17992954",
            "17992955",
            "17992956",
            "17998817"
        ]

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


if __name__ == '__main__':
    # main()
    # run()
    test()

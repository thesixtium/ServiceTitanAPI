import datetime
import password
import analytics
import threading
import integration
import numpy as np
import multiprocessing
from time import sleep
from integration_logger import log

thread_analytics = []
thread_analytics_new_mappings = []
thread_analytics_location_duplicates = []
thread_analytics_non_mapped_locations = []
thread_analytics_error_locations = []
thread_changes = []


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
    global thread_analytics_new_mappings
    global thread_analytics_location_duplicates
    global thread_analytics_non_mapped_locations
    global thread_analytics_error_locations
    global thread_changes

    threads = []
    thread_analytics = [[] for _ in range(cores)]
    thread_analytics_new_mappings = [[] for _ in range(cores)]
    thread_analytics_location_duplicates = [[] for _ in range(cores)]
    thread_analytics_non_mapped_locations = [[] for _ in range(cores)]
    thread_analytics_error_locations = [[] for _ in range(cores)]
    thread_changes = [[] for _ in range(cores)]

    for i in range(0, cores):
        threads.append(IntegrationThread(split_customers[i], i))
        threads[i].name = f"Thread {i}"
        threads[i].start()

    for i in range(0, 10):
        for thread in threads:
            while thread.is_alive():
                pass

    all_analytics = [item for sublist in thread_analytics for item in sublist]
    analytics_new_mappings = [item for sublist in thread_analytics_new_mappings for item in sublist]
    analytics_location_duplicates = [item for sublist in thread_analytics_location_duplicates for item in sublist]
    analytics_non_mapped_locations = [item for sublist in thread_analytics_non_mapped_locations for item in sublist]
    analytics_error_locations = [item for sublist in thread_analytics_error_locations for item in sublist]
    changes = [item for sublist in thread_changes for item in sublist]

    changes = [
        changes,
        analytics_new_mappings,
        analytics_location_duplicates,
        analytics_non_mapped_locations,
        analytics_error_locations
    ]

    analytics.run(all_analytics, changes)


class IntegrationThread(threading.Thread):
    def __init__(self, all_customers, i):
        threading.Thread.__init__(self)
        self.integration_bot = integration.Bot(
            password.get_close_api_key(),
            password.get_client_id(),
            password.get_client_secret(),
            password.get_app_key(),
            password.get_tenant_id()
        )
        self.all_customers = all_customers
        self.i = i

    def run(self):
        global thread_analytics
        global thread_analytics_new_mappings
        global thread_analytics_location_duplicates
        global thread_analytics_non_mapped_locations
        global thread_analytics_error_locations
        global thread_changes

        for customer in self.all_customers:
            log(f"Starting on customer {customer}")
            results = self.integration_bot.map_single_st_customer_to_close_lead(customer)
            pair = results[0]
            log(f"{customer} pair is {pair}")
            thread_analytics_new_mappings[self.i].append(results[1])
            thread_analytics_location_duplicates[self.i].append(results[2])
            thread_analytics_non_mapped_locations[self.i].append(results[3])
            thread_analytics_error_locations[self.i].append(results[4])

            for p in pair:
                log(f"Working on customer {customer} and pair {p}")
                if self.integration_bot.check_pair(p):
                    thread_changes[self.i].append(p[1])
                thread_analytics[self.i].append(p[1])


if __name__ == '__main__':
    main(multiprocessing.cpu_count())

from closeio_api import Client as CloseIO_API, APIError
import os
import requests
import json
import time
import copy
from .format_rs_to_close import format_address_as_string, format_address, format_new_contacts_array, format_opportunity_data, format_note_data, convert_epoch_to_dt
import logging

## Initiate Logger
log_format = "[%(asctime)s] %(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

## Initiate Close API
api = CloseIO_API(os.environ.get('CLOSE_API_KEY'))
org_id = api.get('api_key/' + os.environ.get('CLOSE_API_KEY'))['organization_id']
dev_api = CloseIO_API(os.environ.get('CLOSE_DEV_API_KEY'))

##############################################
# Close Methods
##############################################

## Method to get most recent completed sync time from the Master Lead in the Development Sandbox
## If we cannot get the most recent completed sync time, we default to 5 minutes before the
## current time
def get_sync_time_from_close(current_time):
    if os.environ.get('MASTER_LEAD_ID'):
        try:
            lead = dev_api.get('lead/' + os.environ.get('MASTER_LEAD_ID'), params={ '_fields': 'custom' })
            if lead['custom'].get('last_sync_time'):
                return int(lead['custom']['last_sync_time'])
        except APIError as e:
            logging.error("No Master Lead could be found...")
    return (current_time - 300000)

## Method to set the sync time on the master lead in Close once a RazorSync sync has been completed at a particular time.
def set_sync_time_in_close(last_sync_time):
    if os.environ.get('MASTER_LEAD_ID'):
        try:
            dev_api.put('lead/' + os.environ.get('MASTER_LEAD_ID'), data={ 'custom.last_sync_time': last_sync_time })
        except APIError as e:
            logging.error("Could not update sync time on lead because we could not get the master lead...")

## Method to update an existing address lead in Close with new information if the Customer in RazorSync has been updated.
## We check the differences in lead name, contacts, and billing address, and make updates where appropriate.
def update_lead(lead, addr, cust):
    lead_updates = {}
    name = format_address_as_string(addr)
    contact_names_in_close = { k['display_name'].lower() : k for k in lead['contacts'] }
    if name.strip() != lead['display_name'].strip():
        lead_updates = { 'name': name }
    new_contacts = format_new_contacts_array(cust)
    for contact in new_contacts:
        if contact['name'].lower() in contact_names_in_close:
            close_contact = contact_names_in_close[contact['name'].lower()]
            close_phones_and_emails = [i['email'] for i in close_contact['emails']] + [i['phone'] for i in close_contact['phones']]
            new_contact_phones_and_emails = [i['email'] for i in contact['emails']] + [i['phone'] for i in contact['phones']]
            difference = [i for i in new_contact_phones_and_emails if i not in close_phones_and_emails]
            if difference:
                try:
                    if contact.get('date_created'):
                        del contact['date_created']
                    api.put('contact/' + contact_names_in_close[contact['name'].lower()]['id'], data=contact)
                    logging.info(f"Updated Contact {contact['name']}")
                except APIError as e:
                    logging.error(f"Failed to update contact {contact_names_in_close[contact['name'].lower()]['id']} because {str(e)}...")
        else:
            contact['lead_id'] = lead['id']
            try:
                api.post('contact', data=contact)
                logging.info(f"Posted new contact {contact['name']} on {contact['lead_id']}")
            except APIError as e:
                logging.error(f"Failed to post new contact {contact['name']} to lead because {str(e)}")
    if len(cust['Addresses']) > 1:
        billing_address = [i for i in cust['Addresses'] if i.get('AddressTypeId') and address_types.get(i['AddressTypeId']) == "Billing"]
        if billing_address:
            billing_address = format_address_as_string(billing_address[0])
            if billing_address != lead['custom'].get('RS Billing Address'):
                lead_updates['custom.RS Billing Address'] = billing_address
    if lead_updates != {}:
        try:
            api.put('lead/' + lead['id'], data=lead_updates)
            logging.info(f"Successfully Updated {lead['display_name']}")
        except APIError as e:
            logging.error(f"Failed to PUT updates on lead because {str(e)}")

## Method to create a new lead from a new non-billing address in RazorSync
def post_new_close_lead(post_addr, post_cust):
    lead_data = {}
    addresses = []
    ## Note: Appartment is intentionally misspelled here because they have a typo in their API
    lead_data['name'] = format_address_as_string(post_addr)
    lead_data['custom.RS Address ID'] = post_addr['Id']
    lead_data['contacts'] = format_new_contacts_array(post_cust)
    if lead_data['name']:
        addresses.append(format_address(post_addr))
    if addresses:
        lead_data['addresses'] = addresses

    ## Check if Lead has a billing address
    if len(post_cust['Addresses']) > 1:
        billing_address = [i for i in post_cust['Addresses'] if i.get('AddressTypeId') and address_types.get(i['AddressTypeId']) == "Billing"]
        if billing_address:
            lead_data['custom.RS Billing Address'] = format_address_as_string(billing_address[0])
    if lead_data:
        lead_data['custom.Created via RS Integration'] = 'Yes'
        lead_data['status'] = 'Created via RS Integration'
        try:
            lead = api.post('lead', data=lead_data)
            logging.info(f"Successfully posted {lead['display_name']}")
            return lead
        except APIError as e:
            logging.error(f"Failed to post {lead_data['name']} because {str(e)}")
    return None

## Method to find a close lead using the RS Address ID custom field and searching for an exact match
def find_close_lead_from_rs_address_id(address_id):
    resp = api.get('lead', params={ 'query': f"\"custom.RS Address ID\":\"{address_id}\"", '_fields': 'id,contacts,opportunities,display_name,custom' })
    if resp['data']:
        return resp['data'][0]
    else:
        return None

## Method to find or create a new lead in Close from an RS address and customer record
## First, we try to find a lead using find_close_lead_from_rs_address_id. If no lead is found,
## we post one. If a lead is found, we try to update it.
def find_or_create_close_address_lead_from_customer(addr, cust):
        lead = find_close_lead_from_rs_address_id(addr['Id'])
        if not lead:
            lead = post_new_close_lead(addr, cust)
        else:
            update_lead(lead, addr, cust)
        return lead

## This method takes a service item ID that was deleted in RazorSync, found below, and
## marks the opportunity on the Close lead that reflects that service item as "Removed From Work Order".
def update_deleted_service_item_to_deleted(serv_id, opportunities):
    opp = find_potential_close_opp_from_work_order_service_item_id(opportunities, serv_id)
    if opp and opp['status_label'] != 'Removed From Work Order':
        try:
            api.put('opportunity/' + opp['id'], data={ 'status': 'Removed From Work Order' })
            logging.info(f"Successfully updated {opp['id']} to status Removed From Work Order")
        except APIError as e:
            logging.error(f"Failed to update {opp['id']}'s status to removed from work order' because {str(e)}")
    return None

## Given a Close lead's opportunities and a service item ID as input, this method tries to match
## a Close opoortunity to a service item ID for updating via note parsing for the given ID.
def find_potential_close_opp_from_work_order_service_item_id(opportunities, serv_item_id):

    potential_opps = [i for i in opportunities if f"Work Order Service Item ID: {serv_item_id}" in i['note'] ]
    if potential_opps:
        return potential_opps[0]
    return None

## This method finds all service items in Close given a lead and a Work Order ID.
def get_list_of_service_items_in_close(lead, work_order_id):
    service_item_ids = []
    for opp in lead['opportunities']:
        try:
            ## Check to see if there's a service item ID in the opp note. This is the identifier for RS opportunities. Also check to make sure the Work Order ID itself
            ## matches because a lead can have multiple work orders attached.
            if 'Work Order Service Item ID: ' in opp['note'] and opp['note'].split('Work Order Service Item ID: ')[1].split('\n')[0].strip() and f"Work Order ID: {work_order_id}" in opp['note']:
                service_item_ids.append(opp['note'].split('Work Order Service Item ID: ')[1].split('\n')[0].strip())
        except IndexError as e:
            logging.error(f"Failed to find service item ID on {opp['id']} - {lead['id']}")
    return service_item_ids

## This method tries to update a Close opportunity when a work order service item is updated.
## We try to find a potential opportunity by service item ID, and if we find one we format the opp_data
## array like the opps are formatted in Close. If no potential opp is found, we post a new opportunity to the lead.
## If an opp is found, we try to update it if the notes or value don't match.
def create_or_update_close_opportunity_from_service_item(serv_item, w_o, lead_data):
    potential_opp = find_potential_close_opp_from_work_order_service_item_id(lead_data['opportunities'], serv_item['Id'])
    opp_data = format_opportunity_data(serv_item, w_o)
    if not potential_opp:
        opp_data['lead_id'] = lead_data['id']
        try:
            opp = api.post('opportunity', data=opp_data)
            logging.info(f"Successfully created new opportunity for Service Item {serv_item['Id']} - {w_o['Id']} - {opp['id']}")
        except APIError as e:
            logging.error(f"Failed to create new opportunity for Service Item {serv_item['Id']} - {w_o['Id']} because {str(e)}")

    else:
        opp = potential_opp
        if opp['note'].strip() != opp_data['note'].strip() or opp.get('value') != opp_data.get('value'):
            try:
                if opp_data.get('date_created'):
                    del opp_data['date_created']
                api.put('opportunity/' + opp['id'], data=opp_data)
                logging.info(f"Successfully updated opportunity for Service Item {serv_item['Id']} - {opp['id']}")
            except APIError as e:
                logging.error(f"Failed to update opportunity for Service Item {serv_item['Id']} - {opp['id']} because {str(e)}")

## Method to find a note in Close via a work_order_id so we can properly update work order notes and
## not create duplicates. If the note is meant to be a completed note, we look for was completed on.
## Otherwise, we look for the pattern "Work Order ID: IDHERE" in the note.
def find_note_for_work_order_by_id(lead_id, work_order_id, was_completed=False):
    try:
        notes = []
        has_more = True
        offset = 0
        while has_more:
            resp = api.get('activity/note', params={ 'lead_id': lead_id, '_skip': offset })
            for note in resp['data']:
                if was_completed:
                    if f"Work Order ID: {work_order_id} was completed on:" in note['note']:
                        return note
                else:
                    try:
                        if f"Work Order ID: {work_order_id}" in note['note'] and not f"Work Order ID: {work_order_id} was completed on:" in note['note']:
                            return note
                    except IndexError as e:
                        logging.error(f"Failed to parse Work Order note on {lead_id} - {work_order_id} - {note['id']}")
            offset += len(resp['data'])
            has_more = resp['has_more']
    except APIError as e:
        logging.error(f"Failed to get notes for {lead_id} because {str(e)}")
    return None

## This method creates or updates work order notes on a lead for a synced work order
def create_or_update_close_work_order_notes(serv_items, w_o, lead_data):
    ## Create "was completed" note on the lead.
    if w_o['StatusName'] == 'Complete' and not find_note_for_work_order_by_id(lead_id=lead_data['id'], work_order_id=w_o['Id'], was_completed=True):
        note_data = format_note_data(work_order=w_o, was_completed=True)
        note_data['lead_id'] = lead_data['id']
        api.post('activity/note', data=note_data)

    ## For any Work Order update, try to find the work order not that was previously created. If not, create one.

    potential_note = find_note_for_work_order_by_id(lead_id=lead_data['id'], work_order_id=w_o['Id'])
    note_data = format_note_data(work_order=w_o, was_completed=False, service_items=serv_items)
    if not potential_note:
        note_data['lead_id'] = lead_data['id']
        try:
            api.post('activity/note', data=note_data)
        except APIError as e:
            logging.error(f"Failed to post note to {note_data['lead_id']} because {str(e)}")
    else:
        if potential_note['note'].strip() != note_data['note'].strip():
            try:
                if note_data.get('date_created'):
                    del note_data['date_created']
                api.put('activity/note/' + potential_note['id'], data=note_data)
            except APIError as e:
                logging.error(f"Failed to update note {potential_note['id']} because {str(e)}")

## Method to sync RS Work Order statuses to statuses in Close based on a list of RS statuses defined below
def find_work_order_statuses_in_close(work_order_statuses):
    try:
        opportunity_statuses = api.get(f"organization/{org_id}", params={ '_fields': 'opportunity_statuses'})['opportunity_statuses']
        status_names_in_close = [i['label'] for i in opportunity_statuses]
        if 'Removed From Work Order' not in status_names_in_close:
            try:
                api.post('status/opportunity', data={ 'label': 'Removed From Work Order', 'type': 'lost' })
            except APIError as e:
                logging.error(f'Failed to Create Removed From Work Order Status because {str(e)}')

        for work_order_status in work_order_statuses:
            if work_order_status['Name'] not in status_names_in_close:
                status_data = { 'label': work_order_status['Name']}
                status_data['type'] = 'active'
                if 'Complete' in status_data['label']:
                    status_data['type'] = 'won'
                elif 'No ' in status_data['label'] or 'cancelled' in status_data['label'].lower():
                    status_data['type'] = 'lost'
                try:
                    api.post('status/opportunity', data=status_data)
                except APIError as e:
                    logging.error(f"Failed to post status to Close {status_data['label']} because {str(e)}")
    except Exception as e:
        logging.error(f"Failed to sync Work Order Statuses to Close because {str(e)}")

##############################################
# RazorSync Methods
##############################################
address_types = {}
work_order_statuses = {}
service_item_dictionary = {}
rs_users_dictionary = {}

# Initiate RazorSync Request Headers
razorsync_headers = {
    "Host": f"{os.environ.get('RAZORSYNC_SERVERNAME').lower()}.0.razorsync.com",
    "Token": f"{os.environ.get('RAZORSYNC_TOKEN')}",
    "Content-type": 'application/json',
    "ServerName": f"{os.environ.get('RAZORSYNC_SERVERNAME')}"
}

# Method to make request to RazorSync API
def make_rs_request(method, url_path, params={}, data=None):
    url = f"https://{os.environ.get('RAZORSYNC_SERVERNAME').lower()}.0.razorsync.com/ApiService.svc/{url_path}"
    if method.lower() == 'post':
        r = requests.post(url, headers=razorsync_headers, data=json.dumps(data))
        if r.status_code >= 400:
            logging.error(f"Failed to complete POST for RS Path {url_path}")
            return [] if 'List' in url_path else []
        try:
            r.json()
            return r.json()
        except Exception as e:
            logging.error(f"Failed post request to {url_path} because {str(e)}")
            logging.error(f"Url: {url}\nHeaders: {razorsync_headers}\nData: {data}")
            return None


    if method.lower() == 'get':
        r = requests.get(url, headers=razorsync_headers, params=params)
        if r.status_code >= 400:
            logging.error(f"Failed to complete GET for RS Path {url_path}")
            return [] if 'List' in url_path else {}
        try:
            r.json()
            return r.json()
        except Exception as e:
            logging.error(f"Failed get request to {url_path} because {str(e)}")
            logging.error(f"{r.text}")
            return None

# This method gets the address types and work order statuses of the RazorSync organization
# It also makes sure all work order statuses are correctly reflected in Close
def get_settings_models():
    try:
        settings_resp = make_rs_request(method="GET", url_path='Settings')
        for k in settings_resp['AddressTypeModels']:
            address_types[k['Id']] = k['Name']

        for k in settings_resp['Users']:
            rs_users_dictionary[k['Id']] = f"{k.get('FirstName') or ''} {k.get('LastName') or ''}".strip()

        ## Make sure all work order statuses are in Close
        find_work_order_statuses_in_close(settings_resp['WorkOrderCustomStatuses'])
        for k in settings_resp['WorkOrderCustomStatuses']:
            work_order_statuses[k['Id']] =  k['Name']
    except Exception as e:
        logging.error(f"Could not get RS Settings Models because {str(e)}")

# This method gets all the possible service items in the RazorSync organization
def get_service_item_dictionary():
    service_items = make_rs_request(method='GET', url_path='ServiceItem/List')
    for k in service_items:
        service_item_dictionary[k['Id']] = k

## This method gets every service item for a work_order_id
def get_service_items_for_work_order_id(work_order_id):
    work_order_service_items = make_rs_request(method='GET', url_path=f'WorkOrderServiceItem/List/{work_order_id}')
    for work_order_service_item in work_order_service_items:
        if work_order_service_item['ServiceItemId'] not in service_item_dictionary:
            get_service_item_dictionary()
        if work_order_service_item['ServiceItemId'] in service_item_dictionary:
            work_order_service_item['specifics'] = service_item_dictionary[work_order_service_item['ServiceItemId']]
    return work_order_service_items

## This method finds an address_id based on a service_request_id from a work_order
def find_address_id_using_service_request_id(service_request_id):
    if service_request_id:
        service_request = make_rs_request(method="GET", url_path=f"ServiceRequest/{service_request_id}")
        return service_request['AddressId']
    return None

## This method processes work order updates where applicable.
def process_work_order_updates(work_order, recently_found_leads):
    if (work_order['StatusId'] not in work_order_statuses) or (work_order.get('FieldWorkerId') and work_order['FieldWorkerId'] not in rs_users_dictionary):
        get_settings_models()
    work_order['StatusName'] = work_order_statuses.get(work_order['StatusId'])
    work_order['WorkerName'] = rs_users_dictionary.get(work_order['FieldWorkerId'], "") if work_order.get('FieldWorkerId') else "No Technician Yet"
    address_id = find_address_id_using_service_request_id(work_order['ServiceRequestId'])
    if not address_id:
        return None
    if recently_found_leads.get(address_id):
        lead = recently_found_leads[address_id]
    else:
        lead = find_close_lead_from_rs_address_id(address_id)
    ## Implement SMS if address doesn't exist for work order
    if not lead:
        return None
    service_items = get_service_items_for_work_order_id(work_order['Id'])
    close_service_item_ids = get_list_of_service_items_in_close(lead, work_order['Id'])
    current_work_order_service_item_ids = [str(i.get('Id')) for i in service_items]
    removed_service_items = [i for i in close_service_item_ids if str(i) not in current_work_order_service_item_ids]
    for service_item in service_items:
        create_or_update_close_opportunity_from_service_item(service_item, work_order, lead)
    create_or_update_close_work_order_notes(service_items, work_order, lead)
    for serv_id in removed_service_items:
        update_deleted_service_item_to_deleted(serv_id, lead['opportunities'])

# Start Timezone Capped Search of RS. This is a job that runs on AP Scheduler
def search_in_rs():
    leads_found_this_search = {}
    current_time = int(time.time()*1000)
    last_sync_time = get_sync_time_from_close(current_time)
    mod_dates = { "FromModifiedDate": f"/Date({last_sync_time})/", "ToModifiedDate": f"/Date({current_time})/" }
    customer_list = make_rs_request(method='POST', url_path="Customer/List", data=mod_dates)
    if customer_list:
        for customer in customer_list:
            for address in customer['Addresses']:
                if address_types.get(address['AddressTypeId'], "No Type") != "Billing":
                    lead = find_or_create_close_address_lead_from_customer(address, customer)
                    leads_found_this_search[address['Id']] = lead
            logging.info(f"Found, created, or updated leads for {customer_list.index(customer) + 1} of {len(customer_list)}")
        
    work_orders  = make_rs_request(method='POST', url_path="WorkOrder/List", data=mod_dates)
    for order in work_orders:
        process_work_order_updates(order, leads_found_this_search)
        logging.info(f"Proccessed Work Order {work_orders.index(order) + 1} of {len(work_orders)}: {order['Id']}")
    leads_found_this_search = {}
    set_sync_time_in_close(current_time)
    logging.info(f"Ran sync between {convert_epoch_to_dt(last_sync_time, '%x %I:%M:%S %p')} - {convert_epoch_to_dt(current_time, '%x %I:%M:%S %p')}")

get_settings_models()
get_service_item_dictionary()

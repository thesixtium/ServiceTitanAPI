from datetime import datetime

## Coverts an epoch time in milliseconds to a specified datetime format. 
def convert_epoch_to_dt(epoch_string, fmt):
    try:
        epoch_dt = epoch_string.split('(')[1].split(')')[0].split('+')[0].split('-')[0]
    except:
        epoch_dt = epoch_string
    dt = datetime.fromtimestamp(float(epoch_dt)/1000)
    return dt.strftime(fmt)

## Formats Razor Sync Address as a string for lead names
def format_address_as_string(addr):
    try:
    ## Note: Appartment is intentionally misspelled here because they have a typo in their API
        display_name = f"{addr.get('AddressName') or ''} {addr.get('AddressLine1') or ''}  {addr.get('AppartmentNumber') or ''}  {addr.get('AddressLine2') or ''}"
    except:
        pass
    return ' '.join(display_name.split())

## Formats an address into a Close format by adding it to a dictionary with "address_1".
## we do this because RS doesn't separate city, state, and zip.
def format_address(addr):
    address_1_string = format_address_as_string(addr)
    if address_1_string:
        return { 'address_1': address_1_string }

## Formats a new contacts array from an RS contacts list to Close Lead Contacts list
def format_new_contacts_array(customer, lead_id=None):
    contacts = []
    for contact in customer['Contacts']:
        contact_data = {}
        phones = []
        contact_data['name'] = "%s %s" % (contact.get('FirstName', ''), contact.get('LastName', ''))
        contact_data['name'] = ' '.join(contact_data['name'].split())
        contact_data['emails'] = [{ 'email': contact['Email'] }] if contact.get('Email') else []
        if contact.get('Phone'):
            phones.append({ 'phone': f"1{contact['Phone']}", 'type': 'direct' })
        if contact.get('MobilePhone'):
            phones.append({ 'phone': f"1{contact['MobilePhone']}", 'type': 'mobile' })
        if contact.get('Fax'):
            phones.append({ 'phone': f"1{contact['Fax']}", 'type': 'fax'})
        for phone in phones:
            phone_formatted = ''.join([i for i in phone['phone'] if i.isdigit()])
            phone['phone'] = f"+{phone_formatted}"
        contact_data['phones'] = phones
        contacts.append(contact_data)
    return contacts

## Formats an opportunity note in Close with RS information from both the service item
## and the work order.
def format_opportunity_note(service_item, work_order):
    opportunity_note = ""
    opp_note_dict = {
        "Work Order Service Item ID": service_item['Id'],
        "Work Order Service Item Count": service_item['Count'],
        "Service Item Info": "\n",
        "Service Item ID": service_item['ServiceItemId'],
        "Service Item Name": service_item['specifics'].get('Name', ""),
        "Service Item Description": service_item['specifics'].get('Description', "No Description Provided"),
        "Service Item Category": service_item['specifics'].get('Category'),
        "Work Order Info": "\n",
        'Work Order ID': work_order['Id'],
        "Work Order Status": f"{work_order['StatusName'] if 'StatusName' in work_order else work_order['StatusId'] }",
        'Work Order Technician': f"{work_order['WorkerName']}",
        "Work Order Description": f"{work_order.get('Description') or 'No Description Provided'}",
        "Work Order Start Date": convert_epoch_to_dt(work_order['StartDate'], '%x %I:%M:%S %p'),
        "Work Order End Date": convert_epoch_to_dt(work_order['EndDate'], '%x %I:%M:%S %p'),
    }
    opp_note_keys = ['Work Order Service Item ID', 'Work Order Service Item Count', 'Service Item Info', 'Service Item ID', 'Service Item Name', 'Service Item Description',
        'Service Item Category', 'Work Order Info', 'Work Order ID', 'Work Order Status', 'Work Order Technician', 'Work Order Description', 'Work Order Start Date', 'Work Order End Date']
    for key in opp_note_keys:
        if key in ['Work Order Info', 'Service Item Info']:
            opportunity_note += '\n'
        opportunity_note += f"{key}: {opp_note_dict[key]}\n"
    return opportunity_note

## Format an opportunity cost in cents for Close opps.
def format_opportunity_cost(cost):
    return int(float(cost) * 100)

## Formats opportunity dictionary from RS data into a Close format.
def format_opportunity_data(service_item, work_order):
    opportunity_data = {
        'note': format_opportunity_note(service_item, work_order),
        'value': format_opportunity_cost(service_item['CalculatedPrice']),
        'value_period': 'one_time',
        'date_created': convert_epoch_to_dt(work_order['CreateDate'], '%Y-%m-%dT%H:%M:%S'),
        'date_won': convert_epoch_to_dt(work_order['EndDate'], '%Y-%m-%d'),
        'status': work_order.get('StatusName', 'Incomplete')
    }
    return opportunity_data

## Formats the note['note'] field for any Close notes based on RS information
def format_note_note(work_order, service_items):
    note_note = ""
    note_note_dict = {
        'Work Order ID': work_order['Id'],
        "Work Order Status": f"{work_order['StatusName'] if 'StatusName' in work_order else work_order['StatusId'] }",
        "Work Order Start Date": convert_epoch_to_dt(work_order['StartDate'], '%x %I:%M:%S %p'),
        "Work Order Technician": work_order['WorkerName'],
        "Work Order Description": f"{work_order.get('Description') or 'No Description Provided'}",
        "Work Order End Date": f"{convert_epoch_to_dt(work_order['EndDate'], '%x %I:%M:%S %p')}\n",
        "Service Items": "\n"
    }

    note_note_keys = ['Work Order ID', 'Work Order Status', 'Work Order Technician', 'Work Order Description', 'Work Order Start Date', 'Work Order End Date', 'Service Items']
    for key in note_note_keys:
        note_note += f"{key}: {note_note_dict[key]}\n"

    if service_items:
        for service_item in service_items:
            note_note += f"Name: {service_item['specifics'].get('Name')}\nCategory: {service_item['specifics'].get('Category')}\nCost: {service_item['CalculatedPrice']}\n\n"
    else:
        note_note += "There are no service items for this Work Order ID"
    return note_note

## Formats a note dictionary based on RS data for posting/putting into Close
def format_note_data(work_order, was_completed=False, service_items=None):
    if was_completed:
        note_data = {
            'date_created': convert_epoch_to_dt(work_order['EndDate'], '%Y-%m-%dT%H:%M:%S'),
            'note': f"Work Order ID: {work_order['Id']} was completed on: {convert_epoch_to_dt(work_order['EndDate'], '%x %I:%M:%S %p')}"
        }
    else:
        note_data = {
            'note': format_note_note(work_order=work_order, service_items=service_items),
            'date_created': convert_epoch_to_dt(work_order['CreateDate'], '%Y-%m-%dT%H:%M:%S')
        }
    return note_data

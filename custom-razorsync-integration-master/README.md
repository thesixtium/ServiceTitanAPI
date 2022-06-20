# Custom RazorSync sync with Close
[RazorSync](https://www.razorsync.com/) (RS) is a field management software that `Alberta Indoor Clean Air` uses to sync to Close (1-way sync).

## Setup

### Heroku
#### Environment variables
- `CLOSE_API_KEY` - Close API key of main organization that is used for syncing
- `CLOSE_DEV_API_KEY` - used in conjunction with `MASTER_LEAD_ID` to set/get `last_sync_time` custom field that is used to pull only newest updates from RazorSync API; hardcoded API key is from `Z - Alberta Indoor Clean Air -- DEV` organization
- `MASTER_LEAD_ID` - used in conjunction with `CLOSE_DEV_API_KEY` where this lead serves as storage for `last_sync_time` value; hardcoded to [RAZORSYNC SYNCING LEAD -- Do Not Delete](https://app.close.com/lead/lead_ZjSBiGlAJLoSiNLT6y4QizimovIGbUvcfPlpHYfgqh3/) in `Z - Alberta Indoor Clean Air -- DEV` organization.
- `RAZORSYNC_SERVERNAME` - RazorSync credentials (ie. username)
- `RAZORSYNC_TOKEN` - RazorSync credentials (ie. password)
- `seconds` - interval to run the scheduler; set to `300`

## RazorSync API documentation
Documentation is available at https://razorsync.atlassian.net/wiki/spaces/RC/pages/12451842/External+API+Documentation

Postman collection is available for import at [RazorSync.postman_collection.json](RazorSync.postman_collection.json)

Endpoints used:
- `POST` `/Customer/List` - get customers
- `POST` `/WorkOrder/List` - get work orders
- `GET` `/ServiceItem/List` - get all service items
- `GET` `/Settings` - get settings (address types, users, work order custom statuses)
- `GET` `/WorkOrderServiceItem/List/{workOrderId}` - get work order service items list
- `GET` `/ServiceRequest/{id}` - get service request

# msp-customer-POS-report
## Synopsis

This is an easy sample-code used by a Service Provider to create a monthly POS/Sell-Out Report if all customers are maintained in a single Organization. They order Meraki components in bulk and make them part of the Organization inventory. As soon as a device is part of a network it means it has been sold to a customer and will be part of the report. The data is written into a csv-file containing the Customer name, the SP-owned customer ID and the physical address where the devices have been sold to.

## Prerequisites

To make this script work properly it's important that the network name is built based on the following template --> "Postal/Zip-Code_Customer-Name_Customer-ID"

## Motivation

When ordering in bulk it's essential that the endcustomer data is reported back to Cisco Meraki. This script can help to automize this process.

## Additional Info

An additional script could be added to compare the new report with last months report to only report the delta (not part of this sample code)

## API Reference

dashboard API calls used are:
GET ORG-List
GET Network-List
GET ORG-Inventory
GET Network-device-list

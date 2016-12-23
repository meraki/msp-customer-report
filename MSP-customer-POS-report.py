#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 
#
# getPOSReport.py - A simple Python script that writes all devices of an organization into a csv, including the Customer name and the address of implementation. It's used by a Service Provider to create monthly POS/Sell-Out reports 
# a prerequisite is that the networks are named the based on the following template "Post/Zip-Code_Customer-Name_ Customer-ID". Inventory that is not yet part of a network is not shown in the report.
# 06/06/2016

import argparse
import csv
import pprint
import requests
import signal
import sys
import json
import re
import codecs

netadds=[]
netids=[]
custname=""
paramslist = []
api_key = 'fa9f8a69dd338eca88f83560220cab4436c7cc48' # <--- add your API key here
baseurl = 'https://dashboard.meraki.com/api/v0/'
orgurl = 'https://dashboard.meraki.com/api/v0/organizations/'
headers = {'X-Cisco-Meraki-API-Key': api_key,'Content-Type': 'application/json'}

#use argparse to handle command line arguments
parser = argparse.ArgumentParser(description="a script to get the full inventory and compare it with an existing report to get the delta")

#get the organization-name where the networks have to be updated as an argument
parser.add_argument("ORGName",help='name of the ORG where you would like the CSV applied to')
args = parser.parse_args()
org=args.ORGName

#exit cleanly for SIGINT/Ctrl+C
def signal_handler(signal, frame):
    print("\n***Interrupt!*** ---> Exiting ...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#write dictionary to csv
def dicttocsv(dictname,filename):
    keys = dictname[0].keys()
    wr = csv.DictWriter(filename, keys)
    wr.writeheader()
    for i in dictname:
        i['Network-Name']=i['Network-Name'].encode('ascii','replace')
        i['Custname']=i['Custname'].encode('ascii','replace')
        i['Address']=i['Address'].encode('ascii','replace')
    wr.writerows(dictname)           
    

#create new CSV file into the csvReader object
myfile = codecs.open('filename.csv','wb','utf-8')


#get all of the orgs this API key has access to
orgsjson = requests.get(orgurl, headers=headers).text
output = json.loads(orgsjson)

#check whether the requested organization exists under the administered organization
if any(d['name'] == org for d in output):
    for row in output:
        orgname = row['name']

#get the ID of the ORG to create the networks and inventory URL
        if org == orgname:
            orgid = row['id']
            inventoryurl = (str(orgurl) + str(orgid) + '/inventory')
            networkurl = (str(orgurl) + str(orgid) + '/networks')
            break

#get the list of inventory and networks of the ORG
    inventoryjson = requests.get(inventoryurl, headers=headers).text
    output = json.loads(inventoryjson)
    networkjson = requests.get(networkurl, headers=headers).text
    netoutput = json.loads(networkjson)
    
#check every device in the ORG-Inventory
    for row in output:
        netid = row["networkId"]
        row.pop("networkId",None)
        row.pop("claimedAt",None)
        row.pop("mac",None)
#for devices that are part of a network, check the physical address
        if netid is not None:
            if netid not in netids:
                deviceurl=networkurl +'/' + str(netid) + '/devices'
                devicejson = requests.get(deviceurl, headers=headers).text
                deviceoutput = json.loads(devicejson)
                netaddress = {"id": netid,"address": deviceoutput[0]["address"]}
                row["address"]=deviceoutput[0]["address"]
                netadds.append(netaddress)
                netids.append(netid)
            else:
                for i in netadds:
                    if i["id"]==netid:
                        row["address"]=i['address']
            for nrow in netoutput:
                if nrow["id"]==netid:
                    params={ "Network-Name": nrow["name"],
                             "Address": row["address"],
                             "Model": row["model"],
                             "Serial": row["serial"] }
                    
                    custinfo=re.split("_",nrow["name"])
                    if len(custinfo) > 2:
                        if custinfo[len(custinfo)-1].isdigit():
                            infolength=len(custinfo)-1                           
                        else:
                            infolength=len(custinfo)-2
                        for i in range(1,infolength):
                            custname=custname + " " + custinfo[i]
                        params["PLZ"]=custinfo[0]
                        params["Custname"]=custname
                        params["Cust-ID"]=custinfo[infolength]                                              
                    elif len(custinfo) == 2:
                        params["PLZ"]=custinfo[0]
                        params["Custname"]=custinfo[1]
                    else:
                        params["PLZ"]="n.a"
                        params["Custname"]=custinfo[0]
                        params["Cust-ID"]="n.a"
                    paramslist.append(params)
                    custname=""
                    print params
                    break
    dicttocsv(paramslist,myfile)
        

else:
    print "This ORG does not exist for your admin account"

myfile.close();

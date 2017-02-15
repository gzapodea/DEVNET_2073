# developed by Gabi Zapodeanu, Cisco Systems, TSA, GPO

# !/usr/bin/env python3

# We will use the APIC EM Sandbox for this lab https://sandboxapic.cisco.com/

# network devices IP addresses to use
# '10.2.2.1'
# '10.2.2.2'
# '10.255.1.5'


import requests
import json
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config_data_2073 import APIC_EM_URL, APIC_EM_USER, APIC_EM_PASSW

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_service_ticket():
    """
    This function will generate the Auth ticket required to access APIC-EM
    API call to /ticket is used to create a new user ticket
    :return: APIC-EM ticket
    """

    payload = {'username': APIC_EM_USER, 'password': APIC_EM_PASSW}
    url = APIC_EM_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print('Created APIC-EM ticket: ', ticket)
        return ticket


def get_device_hostname(ip_address):
    """
    Find out the hostname of the network device with the {ip_address}
    Call to:    APIC-EM - network-device/ip-address/{ip_address}
    :param ip_address: network device ip address
    :return: network device hostname
    """

    url = APIC_EM_URL + '/network-device/ip-address/' + ip_address
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    print('Network device information:')
    pprint(device_json)
    hostname = device_json['response']['hostname']
    return hostname


def main():
    """
    This lab will use the APIC EM Sandbox: https://sandboxapic.cisco.com/
    We will find out the name of a network device using the IP address
    Information about the network device will be printed.
    We will print the name of the network device.
    """

    # create an auth ticket for APIC-EM

    global APIC_EM_TICKET    # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()

    # find the hostname for a network device which by using the IP address

    device_ip_address = '10.255.1.5'
    device_hostname = get_device_hostname(device_ip_address)
    print('Network Device Hostname is: ', device_hostname, ' , IP address: ', device_ip_address)


if __name__ == '__main__':
    main()


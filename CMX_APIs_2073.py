
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems

# !/usr/bin/env python3

# We will use the Cisco CMX Sandbox for this lab https://msesandbox.cisco.com:8081
# API docs: https://cmxlocationsandbox.cisco.com/apidocs/

# clients mac addresses to use
# '00:00:2a:01:00:0f'
# '00:00:2a:01:00:13'
# '00:00:2a:01:00:04'
# '00:00:2a:01:00:05'
# '00:00:2a:01:00:15'


import json
import requests
import requests.packages.urllib3

from requests.auth import HTTPBasicAuth  # for Basic Auth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config_data_2073 import CMX_URL, CMX_USER, CMX_PASSW

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

CMX_AUTH = HTTPBasicAuth(CMX_USER, CMX_PASSW)  # http basic auth


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_cmx_client_count():
    """
    This function will find out number of active clients
    Call to CMX - /api/location/v2/clients/count
    :return: number of clients
    """
    url = CMX_URL + 'api/location/v2/clients/count'
    print('\nThe API url: ', url)
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    print('\nThe API response status code: ', response)
    client_json = response.json()
    print('\nThe API response JSON body :')
    pprint(client_json)
    client_count = client_json['count']
    return client_count


def all_active_client_mac():
    """
    This function will find out the MAC addresses for all active clients
    REST API call to CMX - /api/location/v2/clients/active
    :return: none, we will print the mac address list
    """

    url = CMX_URL + 'api/location/v2/clients/active'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    mac_response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    mac_active_clients_json = mac_response.json()
    print('\nMAC addresses of all active clients: \n')
    pprint(mac_active_clients_json)


def check_cmx_client(username):
    """
    This function will find out the WLC controller IP address for a client authenticated with the {username}
    Call to CMX - /api/location/v2/clients/?username={username}
    :param username: username of the client
    :return: WLC IP address
    """

    url = CMX_URL + 'api/location/v2/clients/?username=' + username
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    client_json = response.json()
    if not client_json:
        controller_ip_address = None
    else:
        controller_ip_address = client_json[0]['detectingControllers']
    return controller_ip_address


def check_mac_cmx_client(mac_address):
    """
    This function will find out the WLC controller IP address for a client with the {mac_address}
    Call to CMX - /api/location/v2/clients/?username={username}
    :param: mac_address: client MAC address
    :return: WLC IP address
    """

    url = CMX_URL + 'api/location/v2/clients/?macAddress=' + mac_address
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    client_json = response.json()
    pprint(client_json)  # pretty print the client detail info
    if not client_json:
        controller_ip_address = None
    else:
        controller_ip_address = client_json[0]['detectingControllers']
    return controller_ip_address


def main():
    """
    This lab will use the Cisco CMX Sandbox https://msesandbox.cisco.com:8081
    API docs: https://msesandbox.cisco.com:8081/apidocs/
    We will find out the number of active clients.
    We will print the MAC addresses for all active clients
    Information about a client with a MAC address will be retrieved.
    Not all provided functions will be used.
    """

    # we will get the number of all active clients in CMX

    cmx_client_count = get_cmx_client_count()
    print('CMX number of active clients: ', cmx_client_count)

    # print the mac addresses for all active clients

    all_active_client_mac()

    # find information about an active client

    client_mac_address = '00:00:2a:01:00:04'  # select a mac address from the provided list
    print('\nCMX information for the client with the MAC Address: ', client_mac_address, '\n')
    wlc_ip_address = check_mac_cmx_client(client_mac_address)
    print('\nWLC IP address: ', wlc_ip_address)

    print('\nEnd of Application Run')


if __name__ == '__main__':
    main()



# coding: utf8

# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3


import requests
import json
import time
import requests.packages.urllib3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth

# import all account info from SparkConnect_init.py file. Update the file with lab account info

from SparkConnect_init import SPARK_URL, SPARK_AUTH, ROOM_NAME
from SparkConnect_init import EM_URL, EM_USER, EM_PASSW
from SparkConnect_init import PI_URL, PI_USER, PI_PASSW, WLAN_DEPLOY, WLAN_DISABLE
from SparkConnect_init import CMX_URL, CMX_USER, CMX_PASSW

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

PI_AUTH = HTTPBasicAuth(PI_USER, PI_PASSW)

CMX_AUTH = HTTPBasicAuth(CMX_USER, CMX_PASSW)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_em_service_ticket():
    """
    This function will generate the Auth ticket required to access APIC-EM
    API call to /ticket is used to create a new user ticket
    :return: APIC-EM ticket
    """

    payload = {'username': EM_USER, 'password': EM_PASSW}
    url = EM_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if ticket_response is None:
        print('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print('APIC-EM ticket: ', ticket)
        return ticket


def create_spark_room(room_name):
    """
    This function will create a Spark room with the title {room_name}
    API call to /rooms
    :param room_name: the room name that is to be created
    :return: room_number: the Spark room id
    """

    payload = {'title': room_name}
    url = SPARK_URL + '/rooms'
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    room_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    room_json = room_response.json()
    room_number = room_json['id']
    print('Created Room with the name :  ', ROOM_NAME)
    return room_number


def find_spark_room_id(room_name):
    """
    This function will find the Spark room id based on the {room_name}
    API call to /rooms
    :param room_name: the room name for which to find the Spark room id
    :return: room_number: the Spark room id
    """

    payload = {'title': room_name}
    room_number = None
    url = SPARK_URL + '/rooms'
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    room_response = requests.get(url, data=json.dumps(payload), headers=header, verify=False)
    room_list_json = room_response.json()
    room_list = room_list_json['items']
    for rooms in room_list:
        if rooms['title'] == room_name:
            room_number = rooms['id']
    return room_number


def add_spark_room_membership(room_id, email_invite):
    """
    This function will add membership to the Spark room with the {room_id}
    API call to /memberships
    :param room_id: the Spark room id
    :param email_invite: email of Spark account to invite to the room
    :return: none
    """

    payload = {'roomId': room_id, 'personEmail': email_invite, 'isModerator': 'true'}
    url = SPARK_URL + '/memberships'
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    print("Invitation sent to :  ", email_invite)


def last_spark_room_message(room_id):
    """
    This function will find the last message from the Spark room with the {room_id}
    API call to /messages?roomId={room_id}
    :param room_id: the Spark room id
    :return: {last_message} - the text of the last message posted in the room
             {last_person_email} - the author of the last message in the room
    """

    url = SPARK_URL + '/messages?roomId=' + room_id
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    response = requests.get(url, headers=header, verify=False)
    list_messages_json = response.json()
    list_messages = list_messages_json['items']
    last_message = list_messages[0]['text']
    last_person_email = list_messages[0]['personEmail']
    print('Last room message :  ', last_message)
    print('Last Person Email', last_person_email)
    return [last_message, last_person_email]


def post_spark_room_message(room_id, message):
    """
    This function will post the {message} to the Spark room with the {room_id}
    API call to /messages
    :param room_id: the Spark room id
    :param message: the text of the message to be posted in the room
    :return: none
    """

    payload = {'roomId': room_id, 'text': message}
    url = SPARK_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    print("Message posted :  ", message)


def delete_spark_room(room_id):
    """
    This function will delete the Spark room with the room Id
    API call to /rooms
    :param room_id: the Spark room id
    :return:
    """

    url = SPARK_URL + '/rooms/' + room_id
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    requests.delete(url, headers=header, verify=False)
    print("Deleted Spark Room :  ", ROOM_NAME)


def check_cmx_client(username):
    """
    This function will find out the WLC controller IP address for a client authenticated with the {username}
    Call to CMX - /api/location/v2/clients/?username={username}
    :param username: username of the client
    :return: WLC IP address
    """

    url = CMX_URL + 'api/location/v2/clients/?username=' + username
    print('\nCMX client info API: ', url, '\n')
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    client_json = response.json()
    pprint(client_json)
    if not client_json:
        controller_ip_address = None
    else:
        controller_ip_address = client_json[0]['detectingControllers']
    return controller_ip_address


def get_controller_hostname(ip_address, ticket):
    """
    Find out the wireless LAN controller hostname of the network device with the {ip_address}
    Call to:    APIC-EM - network-device/ip-address/{ip_address}
    :param ip_address: network device ip address
    :param ticket: APIC-EM ticket
    :return: network device hostname
    """

    url = EM_URL + '/network-device/ip-address/' + ip_address
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    hostname = device_json['response']['hostname']
    return hostname


def get_pi_device_id(device_name):
    """
    The function will find out the PI device Id using the device hostname
    Call to:    Prime Infrastructure - /webacs/api/v1/data/Devices, filtered using the Device Hostname
    :param device_name: network device hostname
    :return: PI device id
    """

    url = PI_URL + '/webacs/api/v1/data/Devices?deviceName=' + device_name
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    device_id_json = response.json()
    device_id = device_id_json['queryResponse']['entityId'][0]['$']
    return device_id


def deploy_pi_wlan_template(controller_name, template_name):
    """
    This function will deploy a WLAN template to a wireless controller through job
    Call to:    Prime Infrastructure - /webacs/api/v1/op/wlanProvisioning/deployTemplate
    :param controller_name: WLC Prime Infrastructure id
    :param template_name: WLAN template name
           global variable - PI_Auth, HTTP basic auth
    :return: job number
    """

    param = {
        "deployWlanTemplateDTO": {
            "controllerName": controller_name,
            "templateName": template_name
        }
    }
    print(param)
    url = PI_URL + '/webacs/api/v1/op/wlanProvisioning/deployTemplate'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.put(url, json.dumps(param), headers=header, verify=False, auth=PI_AUTH)
    job_json = response.json()
    job_name = job_json['mgmtResponse']['jobInformation']['jobName']
    print('job name: ', job_name)
    return job_name


def get_pi_job_status(job_name):
    """
    This function will get PI job status
    Call to:    PI - /webacs/api/v1/data/JobSummary, filtered by the job name, will provide the job id
                A second call to /webacs/api/v1/data/JobSummary using the job id
    :param job_name: Infrastructure job name
           global variable - PI_Auth, HTTP basic auth
    :return: job status
    """

    #  find out the PI job id using the job name

    url = PI_URL + '/webacs/api/v1/data/JobSummary?jobName=' + job_name
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    job_id_json = response.json()
    job_id = job_id_json['queryResponse']['entityId'][0]['$']

    #  find out the job status using the job id

    url = PI_URL + '/webacs/api/v1/data/JobSummary/' + job_id
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    job_status_json = response.json()
    #  print(json.dumps(job_status_json, indent=4, separators=(' , ', ' : ')))    # pretty print
    job_status = job_status_json['queryResponse']['entity'][0]['jobSummaryDTO']['resultStatus']
    return job_status


def main():
    """
    This program will dynamically enable a Wi-Fi Hotspot based on the user request, and his/her presence in the
    Enterprise Network.
    LAN switches, WLAN Controllers and AP's, CMX and Cisco Spark are required for this application.
    """

    # verify if Spark Room exists, if not create Spark Room, and add membership (optional)

    spark_room_id = find_spark_room_id(ROOM_NAME)
    if spark_room_id is None:
        spark_room_id = create_spark_room(ROOM_NAME)
        # add_spark_room_membership(spark_room_id, IT_ENG_EMAIL)
        print('- ', ROOM_NAME, ' -  Spark room created')
        post_spark_room_message(spark_room_id, 'To start HotSpot {Spark:Connect} enter  :  /E')
        post_spark_room_message(spark_room_id, 'Ready for input!')
        print('Instructions posted in the room')
    else:
        print('- ', ROOM_NAME, ' -  Existing Spark room found')
        post_spark_room_message(spark_room_id, 'To start HotSpot {Spark:Connect} enter  :  /E')
        post_spark_room_message(spark_room_id, 'Ready for input!')
    print('- ', ROOM_NAME, ' -  Spark room id: ', spark_room_id)

    # check for messages to identify the last message posted and the user's email who posted the message

    last_message = last_spark_room_message(spark_room_id)[0]

    while last_message == 'Ready for input!':
        time.sleep(5)
        last_message = last_spark_room_message(spark_room_id)[0]
        if last_message == '/E':
            last_person_email = last_spark_room_message(spark_room_id)[1]
            post_spark_room_message(spark_room_id, 'How long time do you need the HotSpot for? (in minutes) : ')
            time.sleep(10)
            if last_spark_room_message(spark_room_id)[0] == 'How long time do you need the HotSpot for? (in minutes) :':
                timer = 30 * 60
            else:
                timer = int(last_spark_room_message(spark_room_id)[0]) * 60
        elif last_message != 'Ready for input!':
            post_spark_room_message(spark_room_id, 'I do not understand you')
            post_spark_room_message(spark_room_id, 'To start HotSpot {Spark:Connect} enter  :  /E')
            post_spark_room_message(spark_room_id, 'Ready for input!')
            last_message = 'Ready for input!'

    # CMX will use the email address to provide the wireless controller IP address
    # managing the AP the user is connected to.

    controller_ip_address = check_cmx_client(last_person_email)

    # if controller IP address not found, ask user to connect to WiFi

    if controller_ip_address is None:
        post_spark_room_message(spark_room_id, 'You are not connected to WiFi, please connect and try again!')
        controller_ip_address = '172.16.1.26'
    else:
        print('We found a WLC at your site, IP address: ', controller_ip_address)

    # create an APIC EM auth ticket

    em_ticket = get_em_service_ticket()

    # find the wireless controller hostname based on the management IP address provided by CMX

    controller_hostname = get_controller_hostname(controller_ip_address, em_ticket)
    print('We found a WLC at your site, hostname: ', controller_hostname)

    # find the controller PI device Id using the WLC hostname

    pi_controller_device_id = get_pi_device_id(controller_hostname)
    print('Controller PI device Id :  ', pi_controller_device_id)

    # deploy WLAN template to controller to enable the SparkConnect SSID, and get job status

    job_name_wlan = deploy_pi_wlan_template(controller_hostname, WLAN_DEPLOY)
    time.sleep(20)    # required to give time to PI to deploy the template
    job_status = get_pi_job_status(job_name_wlan)

    # post status update in Spark, an emoji, and the length of time the HotSpot network will be available

    post_spark_room_message(spark_room_id, 'HotSpot {Spark:Connect} ' + job_status)
    post_spark_room_message(spark_room_id, 'The HotSpot will be available for ' + str(int(timer / 60)) + ' minute')
    post_spark_room_message(spark_room_id,  '  ' + '\U0001F44D')

    # timer required to maintain the HotSpot enabled, user provided

    time.sleep(timer)

    # disable WLAN via WLAN template, to be deployed to controller

    job_disable_wlan = deploy_pi_wlan_template(controller_hostname, WLAN_DISABLE)

    post_spark_room_message(spark_room_id, 'HotSpot {Spark:Connect} has been disabled')
    post_spark_room_message(spark_room_id, 'Thank you for using our service')

    # delete Room - optional step, not required

    if input('Do you want to delete the {Spark:Connect} Spark Room ?  (y/n)  ') == 'y':
        delete_spark_room(spark_room_id)

    print('\nEnd of Application Run!')

if __name__ == '__main__':
    main()

# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3

# Spark Accounts are required for this demo
# Attendees will need to register to ciscospark.com if they do not have an account already
# A Spark token will be required


import requests
import json
import time
import requests.packages.urllib3

from random import *
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config_data_2073 import SPARK_URL, SPARK_AUTH, ROOM_NAME  # the file includes all config data required for the lab

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def create_spark_room(room_name):
    """
    This function will create a Spark room with the title {room_name}
    API call to /rooms
    :param room_name: the room name that is to be created
    :return: room_number: the Spark room id
    """

    payload = {'title': room_name}
    url = SPARK_URL + '/rooms'
    print(url)
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    room_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    room_json = room_response.json()
    room_number = room_json['id']
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


def main():
    """
    Spark Accounts are required for this demo.
    Attendees will need to register to ciscospark.com if they do not have an account already.
    This lab module will ask users to post a message in a Spark room.
    After a random time between 10 and 30 seconds the code will retrieve the last message and the author.

    Only some functions will be used. The other functions are provided as a reference.
    """

    # create a new Spark Room?

    new_room = input('Do you want to create a new Spark Room ? (y/n): ')
    if new_room is 'y':
        create_spark_room(ROOM_NAME)

    # find the Spark room id for the room with the name {DEVNET-2073-lab}

    devnet_room_id = find_spark_room_id(ROOM_NAME)
    print('The Spark room id for the room with the name ', ROOM_NAME, ' is: ', devnet_room_id)

    # ask user to input a message

    spark_message = input('Please input a message in the room  ')
    print('This message will be posted in the room with the name ', ROOM_NAME, ' : ', spark_message)

    # post a message in the room
    post_spark_room_message(devnet_room_id, spark_message)

    # wait a random time between 10 and 30 seconds and find out the last message posted on the room
    timer = randint(10, 30)
    print('We will wait for ', timer, ' seconds and check for the last message in the room')
    time.sleep(timer)

    last_message = last_spark_room_message(devnet_room_id)[0]
    last_email = last_spark_room_message(devnet_room_id)[1]
    print('The last message : ', last_message, ', was posted by : ', last_email)


if __name__ == '__main__':
    main()

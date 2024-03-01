#!/usr/bin/env python3

# https://docs.checkmk.com/latest/en/notifications.html#scripts
# https://symbl.cc/en/unicode/table/

# Copyright 2019, Stanislav N. aka pztrn
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os
import uuid
import requests
from datetime import datetime

DEFAULT_MATRIX_HOST = "https://matrix-client.matrix.org"

# Only for test purposes
# Overwrites the environment variables
MATRIX_HOST_MANUAL = ""
MATRIX_TOKEN_MANUAL = ""
MATRIX_ROOM_MANUAL = ""

# Environment variables 
# nano /omd/sites/SITENAME/etc/nagios/conf.d/check_mk_templates.cfg
def initialize_data():
    data = {
        # Notification parameters
        "MATRIX_HOST": os.environ.get("NOTIFY_PARAMETER_1", ""),
        "MATRIX_TOKEN": os.environ.get("NOTIFY_PARAMETER_2", ""),
        "MATRIX_ROOM": os.environ.get("NOTIFY_PARAMETER_3", ""),
        "SITE": os.environ.get("NOTIFY_PARAMETER_4", ""),
        "ADDITIONAL_INFO": os.environ.get("NOTIFY_PARAMETER_5", ""),

        # General information
        "NOTIFICATION_TYPE": os.environ.get("NOTIFY_NOTIFICATIONTYPE", "notification_type"),
        "TYPE": os.environ.get("NOTIFY_WHAT", "SERVICE"),
        "DATETIME": os.environ.get("NOTIFY_SHORTDATETIME", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),

        # Host related information
        "HOST_ALIAS": os.environ.get("NOTIFY_HOSTALIAS", "host_alias"),
        "HOST_NAME": os.environ.get("NOTIFY_HOSTNAME", "host_name"),
        "HOST_ADDRESS": os.environ.get("NOTIFY_HOSTADDRESS", "host_address"),
        "HOST_PREVIOUS_STATE": os.environ.get("NOTIFY_LASTHOSTSTATE", "host_previous_state"),
        "HOST_CURRENT_STATE": os.environ.get("NOTIFY_HOSTSTATE", "host_current_state"),
        "HOST_OUTPUT": os.environ.get("NOTIFY_HOSTOUTPUT", "host_output"),

        # Service related information
        "SERVICE_NAME": os.environ.get("NOTIFY_SERVICEDESC", "service_name"),
        "SERVICE_PREVIOUS_STATE": os.environ.get("NOTIFY_LASTSERVICESTATE", "service_previous_state"),
        "SERVICE_CURRENT_STATE": os.environ.get("NOTIFY_SERVICESTATE", "service_current_state"),
        "SERVICE_OUTPUT": os.environ.get("NOTIFY_SERVICEOUTPUT", "service_output")
    }

    # If necessary, replace with default values or manual values
    if not data["MATRIX_HOST"]:
        if MATRIX_HOST_MANUAL:
            if MATRIX_HOST_MANUAL.upper() == "DEFAULT":
                data["MATRIX_HOST"] = DEFAULT_MATRIX_HOST
            else:
                data["MATRIX_HOST"] = MATRIX_HOST_MANUAL

    if (data["MATRIX_HOST"]).upper() == "DEFAULT":
            data["MATRIX_HOST"] = DEFAULT_MATRIX_HOST

    if (not data["MATRIX_TOKEN"]) and MATRIX_TOKEN_MANUAL:
        data["MATRIX_TOKEN"] = MATRIX_TOKEN_MANUAL

    if (not data["MATRIX_ROOM"]) and MATRIX_ROOM_MANUAL:
        data["MATRIX_ROOM"] = MATRIX_ROOM_MANUAL

    return data

def get_notification_type_icon(notification_type):
    if notification_type == "PROBLEM":
        return "\U0001F198" # SOS icon
    elif notification_type == "RECOVERY":
        return "\U00002705" # green check icon
    else:
        return "\U00002139" # info icon

def get_notification_type_information(data):
    notification_type = data["NOTIFICATION_TYPE"]
    return f"{get_notification_type_icon(notification_type)} {notification_type}"

def get_host_information(data):
    host_alias = data["HOST_ALIAS"]
    host_name = data["HOST_NAME"]
    host_address = data["HOST_ADDRESS"]

    host_parts = []

    if host_alias:
        host_parts.append(host_alias)

    if host_name == host_address:
        host_parts.append(host_name)
    else:
        host_parts.extend([host_name, host_address])

    host_information = " | ".join(host_parts)
    return f"[ {host_information} ]"

def get_state_icon(state):
    if state == "OK" or state == "UP":
        return "\U0001F7E2" # green
    elif state == "WARNING":
        return "\U0001F7E1" # yellow
    elif state == "UNKNOWN" or state == "UNREACHABLE":
        return "\U0001F7E4" # brown
    elif state == "CRITICAL" or state == "DOWN":
        return "\U0001F534" # red
    else:
        return "\U0001F535" # blue

def get_state_information(previous_state, current_state):
    if previous_state == current_state:
        return f"[ {get_state_icon(current_state)} {current_state} ]"
    else:
        return f"[ {get_state_icon(previous_state)} {previous_state} ] → [ {get_state_icon(current_state)} {current_state} ]"

def create_messages_with_information(data, previous_state, current_state, name, output):
    type = data["TYPE"]
    datetime = data["DATETIME"]
    site = data["SITE"]
    additional_info = data["ADDITIONAL_INFO"]

    message = (
        f"{get_notification_type_information(data)} - {type} - {get_host_information(data)}\n\n"
        f"{get_state_information(previous_state, current_state)} - {name}\n"
        f"{output}\n\n"
        f"{datetime}"
    )

    message_html = (
        f"{get_notification_type_information(data)} - <b>{type}</b> - {get_host_information(data)}<br><br>"
        f"{get_state_information(previous_state, current_state)} - <b>{name}</b><br>"
        f"{output}<br><br>"
        f"{datetime}"
    )

    if site:
        message += f"\n\n{site}"
        message_html += f"<br><br>{site}"

    if additional_info:
        message += f"\n\n{additional_info}"
        message_html += f"<br><br>{additional_info}"

    return message, message_html

def create_messages(data):
    if data["TYPE"] == "SERVICE":
        return create_messages_with_information(data, data["SERVICE_PREVIOUS_STATE"], data["SERVICE_CURRENT_STATE"], data["SERVICE_NAME"], data["SERVICE_OUTPUT"])
    else:
        return create_messages_with_information(data, data["HOST_PREVIOUS_STATE"], data["HOST_CURRENT_STATE"], data["HOST_NAME"], data["HOST_OUTPUT"])

def send(data, message, message_html):
    matrix_host = data["MATRIX_HOST"]
    matrix_token = data["MATRIX_TOKEN"]
    matrix_room = data["MATRIX_ROOM"]

    # Data send to Matrix
    matrix_data_dict = {
        "msgtype": "m.text",
        "body": message,
        "format": "org.matrix.custom.html",
        "formatted_body": message_html,
    }
    matrix_data = json.dumps(matrix_data_dict).encode("utf-8")

    # Authorization headers
    matrix_headers = {"Authorization": "Bearer " + matrix_token, "Content-Type": "application/json", "Content-Length": str(len(matrix_data))}

    # Request
    request = requests.put(url=f"{matrix_host}/_matrix/client/r0/rooms/{matrix_room}/send/m.room.message/{str(uuid.uuid4())}", data=matrix_data, headers=matrix_headers)

    if request.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {request.status_code}")

# Run
try:
    data = initialize_data()
    message, message_html = create_messages(data)
    send(data, message, message_html)
except Exception as e:
    print(f"An error occurred: {e}")
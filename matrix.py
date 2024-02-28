#!/usr/bin/env python3

# https://docs.checkmk.com/latest/en/notifications.html#scripts

# Copyright 2019, Stanislav N. aka pztrn
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os
import random
import string
import sys
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
        "TYPE": os.environ.get("NOTIFY_WHAT", "default_type"),
        "NOTIFICATION_TYPE": os.environ.get("NOTIFY_NOTIFICATIONTYPE", "default_notification_type"),
        "DATETIME": os.environ.get("NOTIFY_SHORTDATETIME", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),

        # Host related information
        "HOST_NAME": os.environ.get("NOTIFY_HOSTNAME", "default_host_name"),
        "HOST_ALIAS": os.environ.get("NOTIFY_HOSTALIAS", "default_host_alias"),
        "HOST_ADDRESS": os.environ.get("NOTIFY_HOSTADDRESS", "default_host_address"),
        "HOST_STATE": os.environ.get("NOTIFY_HOSTSTATE", "default_host_state"),
        "HOST_STATE_PREVIOUS": os.environ.get("NOTIFY_LASTHOSTSTATE", "default_last_host_state"),
        "HOST_OUTPUT": os.environ.get("NOTIFY_HOSTOUTPUT", "default_host_output"),

        # Service related information
        "SERVICE_NAME": os.environ.get("NOTIFY_SERVICEDESC", "default_service_name"),
        "SERVICE_STATE": os.environ.get("NOTIFY_SERVICESTATE", "default_service_state"),
        "SERVICE_STATE_PREVIOUS": os.environ.get("NOTIFY_LASTSERVICESTATE", "default_last_service_state"),
        "SERVICE_OUTPUT": os.environ.get("NOTIFY_SERVICEOUTPUT", "default_service_output")
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

def get_state_icon(state):
    if state == "OK" or state == "UP":
        return "\U0001F7E2" # green
    elif state == "WARNING":
        return "\U0001F7E1" # yellow
    elif state == "UNKNOWN" or state == "UNREACHABLE":
        return "\U0001F7E0" # orange
    elif state == "CRITICAL" or state == "DOWN":
        return "\U0001F534" # red
    else:
        return "\U0001F535" # blue

def get_host_header(data):
    host_alias = data["HOST_ALIAS"]
    host_address = data["HOST_ADDRESS"]
    host_name = data["HOST_NAME"]

    header_parts = []

    if host_alias:
        header_parts.append(host_alias)

    if host_address == host_name:
        header_parts.append(host_address)
    else:
        header_parts.extend([host_name, host_address])

    return " | ".join(header_parts)

def generate_messages(data, previous_status, current_status, name, output):
    notification_type = data["NOTIFICATION_TYPE"]
    notification_type_icon = "\U00002139" # info icon
    type = data["TYPE"]
    datetime = data["DATETIME"]
    site = data["SITE"]
    additional_info = data["ADDITIONAL_INFO"]

    if notification_type == "PROBLEM":
        notification_type_icon = "\U0001F198"  # SOS icon
    elif notification_type == "RECOVERY":
        notification_type_icon = "\U00002705"  # green check icon

    status = f"[ {get_state_icon(previous_status)} {previous_status} ] → [ {get_state_icon(current_status)} {current_status} ]"

    message = f"{notification_type_icon} {notification_type} - {type}\n{get_host_header(data)}\n\n{name}\n{status}\n{output}\n\n{datetime}"
    message_html = f"{notification_type_icon} <b>{notification_type}</b> - {type}<br><b>{get_host_header(data)}</b><br><br><b>{name}</b><br>{status}<br>{output}<br><br>{datetime}"

    if site:
        message += f"\n\n{site}"
        message_html += f"<br><br>{site}"

    if additional_info:
        message += f"\n\n{additional_info}"
        message_html += f"<br><br>{additional_info}"

    return message, message_html


def generate_messages_for_type(data):
    if data["TYPE"] == "SERVICE":
        return generate_messages(data, data["SERVICE_STATE_PREVIOUS"], data["SERVICE_STATE"], data["SERVICE_NAME"], data["SERVICE_OUTPUT"])
    else:
        return generate_messages(data, data["HOST_STATE_PREVIOUS"], data["HOST_STATE"], data["HOST_NAME"], data["HOST_OUTPUT"])

def send_matrix_message(data, message, message_html):
    matrix_host = data["MATRIX_HOST"]
    matrix_token = data["MATRIX_TOKEN"]
    matrix_room = data["MATRIX_ROOM"]

    # Data send to Matrix Home Server
    matrix_data_dict = {
        "msgtype": "m.text",
        "body": message,
        "format": "org.matrix.custom.html",
        "formatted_body": message_html,
    }
    matrix_data = json.dumps(matrix_data_dict)
    matrix_data = matrix_data.encode("utf-8")

    # Random transaction ID for Matrix Home Server
    txn_id = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

    # Authorization headers
    matrix_headers = {"Authorization": "Bearer " + matrix_token, "Content-Type": "application/json", "Content-Length": str(len(matrix_data))}

    # Request
    req = requests.put(url=f"{matrix_host}/_matrix/client/r0/rooms/{matrix_room}/send/m.room.message/{txn_id}", data=matrix_data, headers=matrix_headers)

    if req.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {req.status_code}")

# Run
try:
    data = initialize_data()
    message, message_html = generate_messages_for_type(data)
    send_matrix_message(data, message, message_html)
except Exception as e:
    print(f"An error occurred: {e}")
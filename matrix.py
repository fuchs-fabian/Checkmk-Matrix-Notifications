#!/usr/bin/env python3

# https://docs.checkmk.com/latest/en/notifications.html#scripts
# https://symbl.cc/en/unicode/table/

# Copyright 2019, Stanislav N. aka pztrn
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import json
import uuid
import requests
import subprocess
from datetime import datetime

DEFAULT_MATRIX_HOMESERVER_URL = "https://matrix-client.matrix.org"
DEFAULT_USE_E2E = "False"
CHECKMK_NOTIFICATION_DIRECTORY = "/local/share/check_mk/notifications/"

# Only for test purposes - overwrites the environment variables
CHECKMK_USES_THE_SCRIPT = True
MATRIX_HOMESERVER_URL = ""
MATRIX_ACCESS_TOKEN = ""
MATRIX_ROOM_ID = ""

# Environment variables 
# nano /omd/sites/SITENAME/etc/nagios/conf.d/check_mk_templates.cfg
def initialize_data():
    data = {
        # Notification parameters
        "HOMESERVER_URL": os.environ.get("NOTIFY_PARAMETER_1", ""),
        "ACCESS_TOKEN": os.environ.get("NOTIFY_PARAMETER_2", ""),
        "ROOM_ID": os.environ.get("NOTIFY_PARAMETER_3", ""),
        "USE_E2E": os.environ.get("NOTIFY_PARAMETER_4", DEFAULT_USE_E2E),
        "SITE": os.environ.get("NOTIFY_PARAMETER_5", ""),
        "ADDITIONAL_INFO": os.environ.get("NOTIFY_PARAMETER_6", ""),

        # General information
        "ROOT": os.environ.get("OMD_ROOT", ""),
        "SITENAME": os.environ.get("OMD_SITE", ""),
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

    # If necessary, replace with default values
    if not data["HOMESERVER_URL"]:
        if MATRIX_HOMESERVER_URL:
            if MATRIX_HOMESERVER_URL.upper() == "DEFAULT":
                data["HOMESERVER_URL"] = DEFAULT_MATRIX_HOMESERVER_URL
            else:
                data["HOMESERVER_URL"] = MATRIX_HOMESERVER_URL

    if (data["HOMESERVER_URL"]).upper() == "DEFAULT":
            data["HOMESERVER_URL"] = DEFAULT_MATRIX_HOMESERVER_URL

    if (not data["ACCESS_TOKEN"]) and MATRIX_ACCESS_TOKEN:
        data["ACCESS_TOKEN"] = MATRIX_ACCESS_TOKEN

    if (not data["ROOM_ID"]) and MATRIX_ROOM_ID:
        data["ROOM_ID"] = MATRIX_ROOM_ID

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

def get_path_for_matrix_commander(root_directory):
    command = "matrix-commander"
    if CHECKMK_USES_THE_SCRIPT:
        return f"{root_directory}/.local/bin/{command}"
    else:
        return command

def get_path_for_credentials_file(root_directory):
    filename = "credentials.json"
    if CHECKMK_USES_THE_SCRIPT:
        return f"{root_directory}{CHECKMK_NOTIFICATION_DIRECTORY}{filename}"
    else:
        return "credentials.json"

def get_path_for_store_directory(root_directory):
    directory = "store/"
    if CHECKMK_USES_THE_SCRIPT:
        return f"{root_directory}{CHECKMK_NOTIFICATION_DIRECTORY}{directory}"
    else:
        return f"./{directory}"

def send_with_e2e(path_for_matrix_commander, path_for_credentials_file, path_for_store_directory, message_html, room_id):
    command = [
        path_for_matrix_commander,
        "-c", path_for_credentials_file,
        "-s", path_for_store_directory,
        "-m", message_html,
        "--room", room_id,
        "--html",
    ]

    try:
        subprocess.run(command, check=True)
        print("Message sent successfully (with E2E).")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send message (with E2E). Error: {e}")

def send_without_e2e(message, message_html, homeserver_url, access_token, room_id):
    message_data = {
        "msgtype": "m.text",
        "body": message,
        "format": "org.matrix.custom.html",
        "formatted_body": message_html,
    }
    message_data_json = json.dumps(message_data).encode("utf-8")
    authorization_headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json", "Content-Length": str(len(message_data_json))}

    request = requests.put(url=f"{homeserver_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message/{str(uuid.uuid4())}", data=message_data_json, headers=authorization_headers)

    if request.status_code == 200:
        print("Message sent successfully (without E2E).")
    else:
        print(f"Failed to send message (without E2E). Status code: {request.status_code}")

try:
    data = initialize_data()
    message, message_html = create_messages(data)
    if str(data["USE_E2E"]).lower() in ["true", "yes", "e2e"]:
        root_directory = data["ROOT"]
        send_with_e2e(get_path_for_matrix_commander(root_directory), get_path_for_credentials_file(root_directory), get_path_for_store_directory(root_directory), message_html, data["ROOM_ID"])
    else:
        send_without_e2e(message, message_html, data["HOMESERVER_URL"], data["ACCESS_TOKEN"], data["ROOM_ID"])
except Exception as e:
    print(f"An error occurred: {e}")
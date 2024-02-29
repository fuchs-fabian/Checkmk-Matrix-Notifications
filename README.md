# Checkmk Matrix notifications

This script enables the integration of [Matrix](https://matrix.org) notifications in [Checkmk](https://checkmk.com/).

Notifications are usually sent via a Matrix group / room.

> A nice representation of the messages with optional parameters has been highlighted here.

## Examples

![Examples](/images/examples.png)

## Structure

![Structure](/images/structure.png)

If the previous state and the current state are identical, only the current state is output.

## Requirements

In order for Checkmk to send notifications to the Matrix messenger, we need:

- a Home Server URL, e.g., for a standard Matrix user `https://matrix-client.matrix.org`

  > It's available in account settings.

- a Matrix (Bot) User and its user token

  > Create a special user! Don't use your main account!  
  > It's available in account settings.  
  > To get it in [Element](https://element.io/), log in as the created (Bot) User, tap on the profile picture on the top left, and go to `all settings → Help and Info`.
  > There should be a dropdown menu on the bottom (Access token).

- a Room ID

  > **You have to join** with this special (Bot) account to **this room** before!  
  > It's available in room settings.

> With this script it is also possible to send messages to an _encrypted_ room. However, the message sent by the script itself is not encrypted.
>
> ![Unencrypted](/images/unencrypted.png)

There are many good instructions for this on the Internet, so this is not part of this documentation.

## Installation

On the Checkmk server:

```bash
apt install python3-pip
```

Change to your Checkmk site user, eg. `monitoring`:

```bash
su - SITENAME
```

Example:

```bash
su - monitoring
```

Install the `requests` package:

```bash
pip install requests
```

Change to the notification directory:

```bash
cd ~/local/share/check_mk/notifications/
```

Download the script from Git repository:

```bash
wget https://raw.githubusercontent.com/fuchs-fabian/Checkmk-Matrix-Notifications/master/matrix.py
```

OR: Copy [`matrix.py`](https://github.com/fuchs-fabian/Checkmk-Matrix-Notifications/blob/master/matrix.py) file contents into the clipboard, create, paste and save the file:

```bash
nano ./matrix.py
```

Give the script execution permissions:

```bash
chmod +x ./matrix.py
```

### Activate changes

1. Activate on selected sites
2. Restart host or
   ```bash
   su - SITENAME
   ```
   ```bash
   omd stop
   ```
   ```bash
   omd start
   ```
   or
   ```bash
   omd restart
   ```

### Dependencies

This script has no dependencies except Python 3 and the `requests` package.

> It was written specifically to be very compact and understandable.

## Configuration

Create your own notification rule in Checkmk.

`Setup → Events → Notifications`

| parameter      | description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| 1              | Home Server URL (with http or https)                                         |
| 2              | Bot User's Access Token                                                      |
| 3              | Room ID                                                                      |
| 4 (_optional_) | Website e.g. the Checkmk instance                                            |
| 5 (_optional_) | Additional information e.g. note to the person who is to rectify the problem |

> _Addition to "parameter 1"_: If you enter `default` here, `https://matrix-client.matrix.org` is used.

### Basic configuration

![Basic configuration](/images/basic_configuration.png)

### Extended configuration

![Extended configuration](/images/extended_configuration.png)

## Troubleshooting

- [Checkmk Docs](https://docs.checkmk.com/latest/en/notifications.html#H1:Real)
- Checkmk notification logfile
  ```bash
  nano/omd/sites/SITENAME/var/log/notify.log
  ```

### HTTP error codes

| error code         | possible problem        |
| ------------------ | ----------------------- |
| 401 (Unauthorized) | Invalid (user) token    |
| 403 (Forbidden)    | Invalid Home Server URL |

### Incorrect timezone

To retrieve the current date on the host, use the following command:

```bash
date
```

Current output: `Wed Feb 28 20:58:22 UTC 2024`

To adjust the timezone:

```bash
timedatectl set-timezone Europe/Berlin
```

Expected result: `Wed Feb 28 21:58:33 CET 2024`

Restart the host or:

```bash
su - SITENAME
```

```bash
omd restart
```

## Testing

A big difference to other Checkmk notification scripts is that you can test the functionality of whether the message is really sent to Matrix in advance in another operating system. All you have to do is adapt the following lines in the Python script:

```python
MATRIX_HOST_MANUAL = ""
MATRIX_TOKEN_MANUAL = ""
MATRIX_ROOM_MANUAL = ""
```

> Remove these entries again after the test!

## Contributions

- Inspiration and partly quoted for the `README` - [Hagbear](https://github.com/Hagbear/checkmk-matrix-notify) - [LICENSE](https://github.com/Hagbear/checkmk-matrix-notify/blob/main/LICENSE)
- Initial repository - [Stanislav N. aka pztrn](https://gitlab.com/pztrn/check_mk_matrix_notifications)
- First fork (Replaced `urllib.request` by `requests`) - [bashclub / Thorsten Spille aka thorstenspille](https://github.com/bashclub/check_mk_matrix_notifications)
- Second fork (Prettify output) - [rwjack](https://github.com/rwjack/check_mk_matrix_notifications)

# Checkmk Matrix Notifications

This script enables the integration of [Matrix](https://matrix.org) notifications in [Checkmk](https://checkmk.com/), optionally with **E2E**.

Notifications are usually sent via a Matrix group / room.

> **E2E** is disabled by default as it requires additional steps to set up. However, you will find instructions below.  
> Great importance was also attached to an appealing display of messages with optional parameters.

As I do not use Checkmk as a [Docker](https://www.docker.com/) container, I cannot guarantee that it will work. If you have any suggestions, improvements, etc., please open an issue or create a fork and don't hesitate to open a PR.

## Examples

![Examples](/images/examples.png)

## Structure

![Structure](/images/structure.png)

If the previous state and the current state are identical, only the current state is output.

## Requirements

> You can find detailed information about what you need and what is required in the **template [`matrix-notify-py-template`](https://github.com/fuchs-fabian/matrix-notify-py-template?tab=readme-ov-file#requirements)**.

Further details can be found in the [Configuration](https://github.com/fuchs-fabian/Checkmk-Matrix-Notifications?tab=readme-ov-file#configuration) section.

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

Install the packages:

```bash
pip install requests matrix-commander
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

> If you decide to send messages end-to-end encrypted, you must continue here! However, if you don't need it, you can skip this part.

```bash
/omd/sites/SITENAME/.local/bin/matrix-commander --login PASSWORD --device 'REPLACE-ME' --user-login 'REPLACE-ME' --password 'REPLACE-ME' --homeserver 'REPLACE-ME' --room-default 'REPLACE-ME'
```

> You have to replace all `REPLACE-ME` with your own credentials!

So that you can verify the session directly without waiting for Checkmk to send a message, you can use the following command.  
You will of course need to customise it.

```bash
/omd/sites/SITENAME/.local/bin/matrix-commander --room 'REPLACE-ME' --message 'First encrypted message :)'
```

Verify a session (See also: [`matrix-notify-py-template`](https://github.com/fuchs-fabian/matrix-notify-py-template?tab=readme-ov-file#installation)):

```bash
/omd/sites/SITENAME/.local/bin/matrix-commander --verify emoji
```

### Activate changes

1. (Activate on selected sites)
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

This script has no dependencies except Python 3.10+, the `requests` and `matrix-commander` package.

> It was written specifically to be very "compact" and understandable.

## Configuration

Create your own notification rule in Checkmk.

`Setup → Events → Notifications`

| parameter      | description                                                                                | Further explanations                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| 1              | Homeserver URL (with http or https) → _is ignored if you use E2E, but should not be empty_ | If you enter `default` (upper and lower case is ignored) here, `https://matrix-client.matrix.org` is used                   |
| 2              | Access Token → _is ignored if you use E2E, but should not be empty_                        |                                                                                                                             |
| 3              | Room ID                                                                                    |                                                                                                                             |
| 4              | Activate end-to-end encryption, `False` by default                                         | E2E is only possible if the following is entered here (upper and lower case is ignored): `true`, `yes`, `e2e`               |
| 5 (_optional_) | Website e.g. the Checkmk instance                                                          | Parameter 4 must have a value! It is intended for the situation described, but you can also write other things in it        |
| 6 (_optional_) | Additional information e.g. note to the person who is to rectify the problem               | Parameters 4 and 5 must have a value! It is intended for the situation described, but you can also write other things in it |

### Basic configuration

![Basic configuration](/images/basic_configuration.png)

### Configurations with all parameters

#### Without E2E

| parameter      |                               |
| -------------- | ----------------------------- |
| 1              | `default`                     |
| 2              | USERTOKEN                     |
| 3              | ROOMID                        |
| 4              | `False`                       |
| 5 (_optional_) | `https://checkmk.hello.world` |
| 6 (_optional_) | `Hello World`                 |

#### With E2E

| parameter      |                               |
| -------------- | ----------------------------- |
| 1              | `I do not care`               |
| 2              | `I do not care`               |
| 3              | ROOMID                        |
| 4              | `True`                        |
| 5 (_optional_) | `https://checkmk.hello.world` |
| 6 (_optional_) | `Hello World`                 |

## Troubleshooting

- [Checkmk Docs](https://docs.checkmk.com/latest/en/notifications.html#H1:Real)
- Checkmk notification logfile
  ```bash
  nano /omd/sites/SITENAME/var/log/notify.log
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
CHECKMK_USES_THE_SCRIPT = False
MATRIX_HOMESERVER_URL = ""
MATRIX_ACCESS_TOKEN = ""
MATRIX_ROOM_ID = ""
```

> Remove these entries again after the test!

[More information](https://github.com/fuchs-fabian/matrix-notify-py?tab=readme-ov-file#test-and-try-with-conda)

## Contributions

- Inspiration and partly quoted for the `README` - [Hagbear](https://github.com/Hagbear/checkmk-matrix-notify) - [LICENSE](https://github.com/Hagbear/checkmk-matrix-notify/blob/main/LICENSE)
- Initial repository - [Stanislav N. aka pztrn](https://gitlab.com/pztrn/check_mk_matrix_notifications)
- First fork (Replaced `urllib.request` by `requests`) - [bashclub / Thorsten Spille aka thorstenspille](https://github.com/bashclub/check_mk_matrix_notifications)
- Second fork (Prettify output) - [rwjack](https://github.com/rwjack/check_mk_matrix_notifications)

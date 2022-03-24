# CheckMK notifications in Matrix

This scripts provides [Matrix](https://matrix.org) notification integration in CheckMK.

It's basically a fork of a fork
- Initial repo - [Stanislav N. aka pztrn](https://gitlab.com/pztrn/check_mk_matrix_notifications)
- First fork - [bashclub](https://github.com/cysea/check_mk_matrix_notifications)

I just made the output look a bit prettier :)

## Installation steps

1. Copy matrix.py file contents into the clipboard.
2. On the CheckMK server, execute ``omd su SITENAME``, where ``SITENAME`` is a site name for OMD. If CheckMK is installed from source - skip this step.
3. Open ``~/local/share/check_mk/notifications/matrix.py`` for editing and paste the ``matrix.py`` file contents into it. Make it executable (``chmod +x ~/local/share/check_mk/notifications/matrix.py``). If CheckMK was installed from source, it's files can be placed elsewhere depending on the installation configuration.

### Dependencies

This script has no dependencies except Python 3. It was written specifically to be very compact and understandable.

## Configuration

This script will send notifications as a user, so a dedicated user should be created for these purposes. Consult the homeserver documentation for  instructions.

The following parameters are required:

* Homeserver URL - this is what you're specifying in Riot and other clients.
* Notification bot user's token. To get it in Element, log in as created user tap on the Profile picture on the top left and go to All settings > Help & About, and there should be a dropdown menu on teh bottom.
* Room ID. It's available in room settings.

After obtaining all of the parameters, the fields in CheckMK should be populated like this:

![Check_mk notifications configuration](/check_mk_notifications_configuration.png)

Where the 1st parameter is a homeserver URL (with http or https), the second parameter is a bot user's access token and the third parameter is a room ID.

## How it will look like?

![Check_mk notifications example](/notifications_in_matrix.png)

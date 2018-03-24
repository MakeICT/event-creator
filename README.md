# Event Creator

This is an automation tool that will create an event in multiple services/calendars on your behalf. It was created for the volunteers at [MakeICT](http://makeict.org) to make their lives a little easier and their calendars more consistent.

## Installation

###Pre-compiled
Extract files to any location and run main.py.

### From Source
apt-get install python3 python3-pip python3-pyside python3-html2text python3-selenium python3-googleapi python3-dateutil pyside-tools

pip3 install smartwaiver-sdk meetup-api


## Usage

1. Configure options `File > Options...`
2. Enter event details
3. Check the boxes for the processors you want the app to use
4. Click publish

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

### Build dependencies
* Python 3
* PySide
* meetup-api
* google-api-python-client
* Selenium
* html2text
* PyInstaller (optional)

### GUI
The UI layout is done with Qt4 Designer. To convert the `*.ui` files to `*.py` necessary to execute, enter the `ui` folder and run `./build`.

### Plugins
To add support for a new calendar or service, you should create a plugin. Plugins are loaded dynamically during runtime from the plugins folder. The best way to start is to probably copy an existing plugin.

## History
### v2.1
* Error messages on publishing errors
* Simple form validation
* Proper logging
* Presistent Google apps credentials
* Improved Google apps authentication workflow

### v2.0
* Ground-up rewrite
* Desktop GUI
* Drop Google Apps Script web integration
* WildApricot API
* Plugin system
* Templates

### v1.0
* Shh bby is ok

## Credits
* Software: Dominic Canare [<dom@greenlightgo.org>]
* Testing: Tom McGuire

## License

Event Creator is free software, and is released under the terms of the GNU General Public License version 3. For details, see LICENSE.

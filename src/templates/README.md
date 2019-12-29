# Event Creator

This is an automation tool that will create an event in multiple services/calendars on your behalf. It was created for the volunteers at [MakeICT](http://makeict.org) to make their lives a little easier and their calendars more consistent.

## Installation

Download and run the install script included in this repository

## Usage

1. Log in
2. Navigate to 'Create Event' page
3. Choose a template and enter event details
4. Choose platforms to post to
5. Submit event
6. Sync event

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

### Build dependencies
* Python 3.7
* flask
* python-dotenv
* flask-oauth
* dateparser
* flask-wtf
* attrdict
* flask-sqlalchemy
* flask-migrate
* flask-navbar
* google-api-python-client
* oauth2client
* google-auth-oauthlib
* google
* flask-login
* pydiscourse

### Plugins
To add support for a new calendar or service, you should create a plugin. Plugins are loaded dynamically during runtime from the plugins folder. The best way to start is to probably copy an existing plugin.

## History
### v3.0
* Converted into a Flask web app
* Authenticates users against WildApricot
* Shared templates
* Built-in calendar and upcoming events pages

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

### Development Resources
####SQLAlchemy
* https://stackoverflow.com/questions/10698852/generic-associations-in-sqlalchemy-with-multiple-parents
* https://docs.sqlalchemy.org/en/13/_modules/examples/generic_associations/table_per_association.html
* https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html#mixing-in-relationships

## Credits
* Software: Dominic Canare [<dom@greenlightgo.org>], Christian Kindel, Steve Owens
* Testing: Tom McGuire, MakeICT Events Team

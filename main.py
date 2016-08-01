print('')
print('Loading system modules...')

import time, sys, datetime

print('Loading selenium webdriver modules...')
from selenium import webdriver

print('Loading other selenium modules...')
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener

print('Loading local modules...')
from seleniumTools import *
from siteDrivers import *

print('Done loading modules')
def regroup(data, key, value=None):
	results = {}
	for obj in data:
		if value is not None:
			results[obj[key]] = obj[value]
		else:
			results[obj[key]] = obj
	return results


login = None

print('Loading main UI')
driver.get('https://script.google.com/a/macros/makeict.org/s/AKfycbwDKez6qRJStKDg1ep5ejZ_AJyxHuxn-w3i9NjZZfjoJEijxPk/exec')
mainWindow = driver.current_window_handle

if login is not None:
	print('Attempting auto login...')
	setValue(waitForID('Email'), login[0])
	click(waitForID('next'))
	setValue(waitForID('Passwd'), login[1])
	click(waitForID('signIn'))
else:
	print('Please login...')

driver.switch_to.frame(waitForID('sandboxFrame'))
driver.switch_to.frame(waitForID('userHtmlFrame'))

while True:
	time.sleep(1)
	try:
		driver.execute_script('hijackCreateButton()')
		driver.execute_script('addCrossPostSystem(arguments[0], arguments[1], arguments[2])', 'wildapricot', 'WildApricot', True)
		driver.execute_script('addCrossPostSystem(arguments[0], arguments[1], arguments[2])', 'facebook', 'Facebook', True)
		break
	except Exception as exc:
		pass

while True:
	switchToMain()

	print('\nEnter your event details, then hit "Create" :)')
	eventDetails = None
	while eventDetails is None:
		time.sleep(1)
		try:
			eventDetails = driver.execute_script('return getEventDetails()')
		except Exception as exc:
			pass
		
	try:
		ticketURL = ''

		eventDetails['startDate'] = datetime.datetime.strptime(eventDetails['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
		eventDetails['startDate'] = eventDetails['startDate'].replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
		eventDetails['endDate'] = datetime.datetime.strptime(eventDetails['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
		eventDetails['endDate'] = eventDetails['endDate'].replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

		crossPosts = regroup(eventDetails['crossPostSystems'], 'id', 'enabled')
		if not crossPosts['wildapricot']:
			if 'rsvpURL' in eventDetails:
				ticketURL = eventDetails['rsvpURL']
			else:
				ticketURL = None
		else:
			createNewTab()
			ticketURL = createWildApricotEvent(eventDetails)
			switchToMain()
			driver.execute_script('setRegistrationURL(arguments[0])', ticketURL)
			driver.execute_script('addResultLink(arguments[0], arguments[1])', ticketURL, 'WildApricot')
		
		if crossPosts['facebook']:
			createNewTab()
			fbURL = createFacebookEvent(eventDetails, ticketURL)
			switchToMain()
			driver.execute_script('addResultLink(arguments[0], arguments[1])', fbURL, 'Facebook')

		driver.execute_script('createEvent()')
			
	except Exception as exc:
		print('\nAn error has occurred :(')
		if 'chrome not reachable' in str(exc):
			sys.exit()
		else:
			print(exc)
			print('\n')

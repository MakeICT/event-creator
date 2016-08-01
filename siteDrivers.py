import time
import html2text

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from seleniumTools import *

def createWildApricotEvent(eventDetails):
	login = None
	
	driver.get('http://makeict.wildapricot.org/Sys/Login/SwitchToAdmin')
	if login is not None:
		print('Attempting auto login...')
		setValue(waitForID('ctl00_ContentArea_loginViewControl_loginControl_userName'), login[0])
		setValue(waitForID('ctl00_ContentArea_loginViewControl_loginControl_Password'), login[1])
		click(waitForID('ctl00_ContentArea_loginViewControl_loginControl_Login'))
	else:
		print('Please login...')

	eventsPageLink = None
	while eventsPageLink is None:
		eventsPageLink = waitForID('Events_dropDown0', 3)
		if eventsPageLink is None:
			dashboardLink = waitForID('Dashboard_Text', 3)
			if dashboardLink is not None:
				click(dashboardLink)
	click(eventsPageLink)

	print('Adding event')
	click(waitForID('WaAdminPanel_AdminMenu_AdminMenuEventsEventListEventListModule_addEventBtn_buttonName'))
	contentFrame = waitForID('contentFrame')
	driver.switch_to.frame(contentFrame)

	print('Setting title')
	setValue(waitForID('eventDetailsMain_editTitle'), eventDetails['eventName'])
	print('Setting location')
	setValue(waitForID('eventDetailsMain_editLocation'), eventDetails['location'])
	
	print('Setting date/time')
	setValue(waitForID('eventDetailsMain_editDate'), eventDetails['startDate'].strftime('%d %b %Y'))
	setValue(waitForID('eventDetailsMain_editTime'), eventDetails['startDate'].strftime('%I:%M %p'))
	setValue(waitForID('eventDetailsMain_editEndDate'), eventDetails['endDate'].strftime('%d %b %Y'))
	setValue(waitForID('eventDetailsMain_editEndTime'), eventDetails['endDate'].strftime('%I:%M %p'))

	checkWhenReady('eventDetailsMain_editAttendeesSettings_showRegistrantsList')
	checkWhenReady('eventDetailsMain_editGuestRegistrationSettings_withEmail')

	print('Setting description')
	driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="tdDescription"]/div[1]/iframe'))
	el = driver.find_element_by_tag_name('p')
	setInnerHTML(el, eventDetails['description'])

	driver.switch_to_default_content()
	driver.switch_to.frame(contentFrame)

	print('Setting registration limit')
	click(waitForID('eventRegistrationTypesShowLink'))

	if 'rsvpLimit' in eventDetails and eventDetails['rsvpLimit'] != '':
		checkWhenReady('ctl07_limitsBox_editIsLimited')
		setValue(waitForID('ctl07_limitsBox_editTotalAllowed'), eventDetails['rsvpLimit'])

	uncheckWhenReady('ctl07_waitlistEnableCheckBox')

	print('Saving...')
	driver.switch_to_default_content()
	click(waitForID('toolbarButtons_button_publishButton_buttonName'))

	print('Adding registration types...')

	for rsvpType in eventDetails['rsvpTypes']:
		print('Adding registration type for %s...' % rsvpType['name'])
		driver.switch_to.frame(contentFrame)
		click(waitForID('ctl07_addRegTypeBtn'))
		time.sleep(.5)
		driver.switch_to_default_content()
		time.sleep(.5)

		setValue(waitForID('idNameTB'), rsvpType['name'])
		setValue(waitForID('idBasePrice'), rsvpType['price'])
		if rsvpType['membersOnly']:
			checkWhenReady('idAvailabilityMembersOnlyItem')
			click(waitForID('idMembershipLevelsCBListselectButton'))
			uncheckWhenReady('idMembershipLevelItem710428')
			uncheckWhenReady('idMembershipLevelItem710427')
			uncheckWhenReady('idMembershipLevelItem334036')
		
		click(waitForID('idSave_buttonName'))
		click(waitForID('idBackLink'))

	time.sleep(1)
	print('Setting reminders')
	driver.switch_to.frame(contentFrame)
	click(waitForID('eventEmailsShowLink'))

	click(waitForID('eventEmails_reminder1_btnSchedule'))
	driver.switch_to_default_content()
	setValue(waitForID('WaAdminPanel_AdminMenu_AdminMenuEventsEventList_EventDetails_EventDetailsViewMode_eventEmails_scheduleReminderDialog_EventReminderScheduleSettingsControl_263_daysBeforeNumberTextBox'), '7')
	time.sleep(0.5)
	click(waitForID('WaAdminPanel_AdminMenu_AdminMenuEventsEventList_EventDetails_EventDetailsViewMode_eventEmails_scheduleReminderDialog_applyButton_buttonName'))

	driver.switch_to.frame(contentFrame)
	time.sleep(1)
	click(waitForID('eventEmails_reminder2_btnSchedule'))
	driver.switch_to_default_content()
	setValue(waitForID('WaAdminPanel_AdminMenu_AdminMenuEventsEventList_EventDetails_EventDetailsViewMode_eventEmails_scheduleReminderDialog_EventReminderScheduleSettingsControl_264_daysBeforeNumberTextBox'), '2')
	time.sleep(1)
	click(waitForID('WaAdminPanel_AdminMenu_AdminMenuEventsEventList_EventDetails_EventDetailsViewMode_eventEmails_scheduleReminderDialog_applyButton_buttonName'))

	time.sleep(1)
	print('Enabling registration')
	driver.switch_to.frame(contentFrame)
	click(waitForID('accessControlLink'))
	driver.switch_to_default_content()
	time.sleep(1)
	checkWhenReady('idEvents_accessPermission_pageAccessLevelPublicItem')
	time.sleep(1)
	click(waitForID('idButtonSave_idEvents_accessPermission_buttonName'))

	driver.switch_to.frame(contentFrame)
	click(waitForID('eventDetailsShowLink'))
	driver.switch_to_default_content()
	click(waitForID('toolbarButtons_button_editButton_buttonName'))

	driver.switch_to.frame(contentFrame)
	checkWhenReady('eventDetailsHeader_editIsRegistrationEnabledCheckbox')
	print('Saving...')
	driver.switch_to_default_content()
	click(waitForID('toolbarButtons_button_publishButton_buttonName'))


	driver.switch_to.frame(contentFrame)
	eventURL = waitForID('eventDetailsMain_viewUrl').get_attribute('innerHTML')
	eventID = eventURL[(1+eventURL.rfind('-')):]
	eventURL = 'http://members.makeict.org/event-%s' % eventID
	driver.switch_to_default_content()
	#click(waitForID('accountTopButton_dropDown6'))
    #
	#driver.get(eventURL)
	return eventURL

def createFacebookEvent(eventDetails, ticketURL):
	login = None
	
	description = eventDetails['description']
	isFree = True
	priceDescription = 'The price for this event is';
	for i, rsvpType in enumerate(eventDetails['rsvpTypes']):
		if i > 0 and i == len(eventDetails['rsvpTypes'])-1:
			priceDescription += ' and'
		  
		if rsvpType['price'] > 0:
			isFree = False
			priceDescription += ' $%0.2f for %s' % (rsvpType['price'], rsvpType['name'])
		else:
			priceDescription += ' FREE for ' + rsvpType['name']
	  
		if len(eventDetails['rsvpTypes']) > 2 and i < len(eventDetails['rsvpTypes'])-1:
			priceDescription += ','
	
	if not isFree:
		description += '<br/>\n' + priceDescription + '.'
	
	textConverter = html2text.HTML2Text()
	textConverter.ignore_links = True
	description = textConverter.handle(description)
	description = re.sub(re.compile("^( *)\\*", re.MULTILINE), '\\1•', description).strip()

	driver.get('https://facebook.com/MakeICT/events')
	if login is not None:
		print('Attempting auto login...')
		setValue(waitForID('email'), login[0])
		setValue(waitForID('pass'), login[1])
		click(waitForID('u_0_1'))
	else:
		print('Please login...')
		
	print('Adding event')
	click(waitForXPath('//*[@data-testid="event-create-button"]'))

	print('Setting title')
	setValue(waitForXPath('//*[@placeholder="Add a short, clear name"]'), eventDetails['eventName'])
	
	print('Setting location')
	if '1500 E Douglas' not in eventDetails['location']:
		setValue(waitForXPath('//*[@placeholder="Include a place or address"]'), eventDetails['location'])
	
	print('Setting start time')
	setValue(waitForXPath('//input[@placeholder="mm/dd/yyyy"]'), eventDetails['startDate'].strftime('%m/%d/%Y'))
	setValue(waitForXPath('//span[@aria-label="hours"]/preceding-sibling::input'), eventDetails['startDate'].strftime('%I'))
	setValue(waitForXPath('//span[@aria-label="minutes"]/preceding-sibling::input'), eventDetails['startDate'].strftime('%M'))
	setValue(waitForXPath('//span[@aria-label="meridiem"]/preceding-sibling::input'), eventDetails['startDate'].strftime('%p'))
	
	print('Adding end time')
	click(waitForXPath('//*[@data-tooltip-content="Time zone set by the location"]/following-sibling::a'))
	
	print('Setting end time')
	setValue(waitForXPath('(//input[@placeholder="mm/dd/yyyy"])[2]'), eventDetails['endDate'].strftime('%m/%d/%Y'))
	setValue(waitForXPath('(//span[@aria-label="hours"])[2]/preceding-sibling::input'), eventDetails['endDate'].strftime('%I'))
	setValue(waitForXPath('(//span[@aria-label="minutes"])[2]/preceding-sibling::input'), eventDetails['endDate'].strftime('%M'))
	setValue(waitForXPath('(//span[@aria-label="meridiem"])[2]/preceding-sibling::input'), eventDetails['endDate'].strftime('%p'))
	
	print('Set category')
	click(waitForXPath('//div/a[contains(.,"Select Category")]'))
	click(waitForXPath('//*[@data-section="Learning"]/a'))
	if 'class' in eventDetails['eventName'].lower():
		click(waitForXPath('//*[@data-parent="Learning" and contains(., "Class")]'))
	else:
		click(waitForXPath('//*[@data-parent="Learning" and contains(., "Workshop")]'))

	print('Setting description')
	setValue(waitForXPath('//th[contains(.,"Description")]/following-sibling::td//div[@contenteditable="true"]'), description)
	time.sleep(2)

	if ticketURL is not None:
		print('Set ticket URL')
		setValue(waitForXPath('//*[@placeholder="Add a website link"]'), ticketURL)

	print('Saving...')
	# Publish now
	#click(waitForXPath('//button[contains("Publish")]'))
	# Draft only
	click(waitForXPath('//button[contains(.,"Publish")]/following-sibling::div/a'))
	click(waitForXPath('//a[contains(.,"Save Draft")]')) 

	time.sleep(2)
	return driver.current_url

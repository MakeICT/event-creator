# -*- coding: utf-8 -*-

import time
import html2text

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from seleniumTools import *

from ..Plugin import Plugin
import ui

class FacebookPlugin(Plugin):
	def __init__(self):
		super().__init__('Facebook')

		self.options = [
			{
				'name': 'Email',
				'type': 'text',
			},{
				'name': 'Password',
				'type': 'password',
			}
		]

		ui.addTarget('Facebook', self.createEvent)
		
	def createEvent(self, event):
		driver = startSelenium()
		description = event['description']
		priceDescription = 'The price for this event is';
		isFree = True
		for rsvpType in event['prices']:
			if i > 0 and i == len(event['prices'])-1:
				priceDescription += ' and'
			  
			if rsvpType['price'] > 0:
				isFree = False
				priceDescription += ' $%0.2f for %s' % (rsvpType['price'], rsvpType['name'])
			else:
				priceDescription += ' FREE for ' + rsvpType['name']
		  
			if len(event['rsvpTypes']) > 2 and i < len(event['rsvpTypes'])-1:
				priceDescription += ','
		
		if not isFree:
			description += '<br/>\n' + priceDescription + '.'
		
		textConverter = html2text.HTML2Text()
		textConverter.ignore_links = True
		description = textConverter.handle(description)
		description = re.sub(re.compile("^( *)\\*", re.MULTILINE), '\\1•', description).strip()

		driver.get('https://facebook.com/MakeICT/events')
		if self.getSetting('Email') is not None and self.getSetting('Password') is not None:
			print('Attempting auto login...')
			setValue(waitForID('email'), self.getSetting('Email'))
			setValue(waitForID('pass'), self.getSetting('Password'))
			click(waitForID('u_0_1'))
		else:
			print('Please login...')
			
		print('Adding event')
		click(waitForXPath('//*[@data-testid="event-create-button"]'))

		print('Setting title')
		setValue(waitForXPath('//*[@placeholder="Add a short, clear name"]'), event['title'])
		
		print('Setting location')
		if '1500 E Douglas' not in event['location']:
			setValue(waitForXPath('//*[@placeholder="Include a place or address"]'), event['location'])
		
		print('Setting start time')
		print(event['startTime'])
		setValue(waitForXPath('//input[@placeholder="mm/dd/yyyy"]'), event['startTime'].toString('M/d/yyyy'))
		setValue(waitForXPath('//span[@aria-label="hours"]/preceding-sibling::input'), event['startTime'].toString('h a').split(' ')[0]) # have to add the am/pm for a 12-hour clock
		setValue(waitForXPath('//span[@aria-label="minutes"]/preceding-sibling::input'), event['startTime'].toString('mm'))
		setValue(waitForXPath('//span[@aria-label="meridiem"]/preceding-sibling::input'), event['startTime'].toString('a'))
		
		print('Adding end time')
		click(waitForXPath('//*[@data-tooltip-content="Time zone set by the location"]/following-sibling::a'))
		
		print('Setting end time')
		setValue(waitForXPath('(//input[@placeholder="mm/dd/yyyy"])[2]'), event['stopTime'].toString('M/d/yyyy'))
		setValue(waitForXPath('(//span[@aria-label="hours"])[2]/preceding-sibling::input'), event['stopTime'].toString('h a').split(' ')[0])
		setValue(waitForXPath('(//span[@aria-label="minutes"])[2]/preceding-sibling::input'), event['stopTime'].toString('mm'))
		setValue(waitForXPath('(//span[@aria-label="meridiem"])[2]/preceding-sibling::input'), event['stopTime'].toString('a'))
		
		print('Set category')
		click(waitForXPath('//div/a[contains(.,"Select Category")]'))
		click(waitForXPath('//*[@data-section="Learning"]/a'))
		if 'class' in event['title'].lower():
			click(waitForXPath('//*[@data-parent="Learning" and contains(., "Class")]'))
		else:
			click(waitForXPath('//*[@data-parent="Learning" and contains(., "Workshop")]'))

		print('Setting description')
		setValue(waitForXPath('//div[@contenteditable="true"]'), description)
		time.sleep(2)

		if event['registrationURL'] is not None:
			print('Set ticket URL')
			setValue(waitForXPath('//*[@placeholder="Add a link to your ticketing website"]'), event['registrationURL'])

		print('Saving...')
		if self.getSetting('Publish immediately'):
			click(waitForXPath('//button[contains("Publish")]'))
		else:
			click(waitForXPath('//button[contains(.,"Publish")]/following-sibling::div/a'))
			click(waitForXPath('//a[contains(.,"Save Draft")]')) 

		time.sleep(2)
		return driver.current_url


def load():
	return FacebookPlugin()

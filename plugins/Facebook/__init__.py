# -*- coding: utf-8 -*-

import time
import html2text
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from plugins import Plugin
from plugins import Selenium

import ui

class FacebookPlugin(Selenium.SeleniumPlugin):
	def __init__(self):
		super().__init__('Facebook')

		self.options = [
			{
				'name': 'Email',
				'type': 'text',
			},{
				'name': 'Password',
				'type': 'password',
			},{
				'name': 'Events page URL',
				'type': 'text',
			}
			#@TODO: Allow option for publishing FB events immediately
			#@TODO: Allow option for FB plugin to overwrite the registration URL
			#@TODO: Check to see if already logged in to FB
		]

		ui.addTarget(self.name, self, self.createEvent)
		
	def setValue(self, obj, value):
		self.checkForInterruption()
		Selenium.setValue(obj, value)
		
	def click(self, obj):
		self.checkForInterruption()
		Selenium.click(obj)

	def createEvent(self, event):
		driver = Selenium.start()
		description = event['description'] + '<br/><br/>' + event['priceDescription']
		description = re.sub('\r\n|\r|\n', '<br/>', description)
		
		textConverter = html2text.HTML2Text()
		textConverter.ignore_links = True
		description = textConverter.handle(description)
		description = re.sub(re.compile("^( *)\\*", re.MULTILINE), '\\1•', description).strip()

		Selenium.goto(self.getSetting('Events page URL', 'https://facebook.com/events'))
		if self.getSetting('Email') is not None and self.getSetting('Password') is not None:
			print('Attempting auto login...')
			self.setValue(Selenium.waitForID('email'), self.getSetting('Email'))
			self.setValue(Selenium.waitForID('pass'), self.getSetting('Password'))
			self.click(Selenium.waitForID('u_0_1'))
		else:
			print('Please login...')
			
		print('Adding event')
		self.click(Selenium.waitForXPath('//*[@data-testid="event-create-button"]'))

		print('Setting title')
		self.setValue(Selenium.waitForXPath('//*[@placeholder="Add a short, clear name"]'), event['title'])
		
		print('Setting location')
		if '1500 E Douglas' not in event['location']:
			self.setValue(Selenium.waitForXPath('//*[@placeholder="Include a place or address"]'), event['location'])
		
		print('Setting start time')
		print(event['startTime'])
		self.setValue(Selenium.waitForXPath('//input[@placeholder="mm/dd/yyyy"]'), event['startTime'].toString('M/d/yyyy'))
		self.setValue(Selenium.waitForXPath('//span[@aria-label="hours"]/preceding-sibling::input'), event['startTime'].toString('h a').split(' ')[0]) # have to add the am/pm for a 12-hour clock
		self.setValue(Selenium.waitForXPath('//span[@aria-label="minutes"]/preceding-sibling::input'), event['startTime'].toString('mm'))
		self.setValue(Selenium.waitForXPath('//span[@aria-label="meridiem"]/preceding-sibling::input'), event['startTime'].toString('a'))
		
		print('Adding end time')
		self.click(Selenium.waitForXPath('//*[@data-tooltip-content="Time zone set by the location"]/following-sibling::a'))
		
		print('Setting end time')
		self.setValue(Selenium.waitForXPath('(//input[@placeholder="mm/dd/yyyy"])[2]'), event['stopTime'].toString('M/d/yyyy'))
		self.setValue(Selenium.waitForXPath('(//span[@aria-label="hours"])[2]/preceding-sibling::input'), event['stopTime'].toString('h a').split(' ')[0])
		self.setValue(Selenium.waitForXPath('(//span[@aria-label="minutes"])[2]/preceding-sibling::input'), event['stopTime'].toString('mm'))
		self.setValue(Selenium.waitForXPath('(//span[@aria-label="meridiem"])[2]/preceding-sibling::input'), event['stopTime'].toString('a'))
		
		print('Set category')
		self.click(Selenium.waitForXPath('//div/a[contains(.,"Select Category")]'))
		self.click(Selenium.waitForXPath('//*[@data-section="Learning"]/a'))
		if 'class' in event['title'].lower():
			self.click(Selenium.waitForXPath('//*[@data-parent="Learning" and contains(., "Class")]'))
		else:
			self.click(Selenium.waitForXPath('//*[@data-parent="Learning" and contains(., "Workshop")]'))

		print('Setting description')
		self.setValue(Selenium.waitForXPath('//div[@contenteditable="true"]'), description)
		time.sleep(2)

		if event['registrationURL'] is not None:
			print('Set ticket URL')
			self.setValue(Selenium.waitForXPath('//*[@placeholder="Add a link to your ticketing website"]'), event['registrationURL'])

		print('Saving...')
		if self.getSetting('Publish immediately'):
			self.click(Selenium.waitForXPath('//button[contains("Publish")]'))
		else:
			self.click(Selenium.waitForXPath('//button[contains(.,"Publish")]/following-sibling::div/a'))
			self.click(Selenium.waitForXPath('//a[contains(.,"Save Draft")]')) 

		time.sleep(2)
		return driver.current_url

def load():
	return FacebookPlugin()

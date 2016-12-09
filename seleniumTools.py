import time, re, os, sys, platform

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.common.exceptions import *

driver = None

try:
	basePath = sys._MEIPASS
except:
	basePath = os.path.abspath('.')

def startSelenium():
	global driver
	if driver is None:
		try:
			if platform.system() == 'Linux':
				driver = webdriver.Chrome('%s/chromedriver' % basePath)
			else:
				driver = webdriver.Chrome('%s/chromedriver.exe' % basePath)
		except:
			print('Chrome driver failed. Trying Firefox... this is untested')
			driver = webdriver.Firefox()
			
	return driver

def waitForID(id, timeout=9999):
	try:
		print('\tfind %s' % id)
		return WebDriverWait(driver, timeout).until(
			EC.presence_of_element_located((By.ID, id))
		)
	except TimeoutException:
		return None
	
def waitForXPath(xpath, timeout=9999):
	try:
		print('\tfind %s' % xpath)
		return WebDriverWait(driver, timeout).until(
			EC.presence_of_element_located((By.XPATH, xpath))
		)
	except TimeoutException:
		return None
	
def checkWhenReady(id, timeout=9999):
	try:
		print('\tfind %s' % id)
		obj = waitForID(id, timeout)
		if not obj.is_selected():
			click(obj)
	except TimeoutException:
		return None
		
def uncheckWhenReady(id, timeout=9999):
	try:
		print('\tfind %s' % id)
		obj = waitForID(id, timeout)
		if obj.is_selected():
			click(obj)
	except TimeoutException:
		return None
		
def setInnerHTML(element, content):
	content = content.replace('\r', '')
	content = re.sub("\n+", '&#10;', content)
	driver.execute_script("arguments[0].innerHTML = arguments[1]", element, content)

def click(element):
	try:
		element.click()
	except:
		driver.execute_script("arguments[0].click()", element)

def setValue(element, value):
	try:
		element.send_keys(Keys.CONTROL, 'a')
		element.send_keys(value)
		time.sleep(0.75)
	except:
		driver.execute_script("arguments[0].value = '%s'" % value, element)

def createNewTab(url=None):
	driver.switch_to.window(driver.window_handles[0])
	driver.switch_to_default_content()
	driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
	time.sleep(1)
	driver.switch_to.window(driver.window_handles[-1])
	time.sleep(1)
	if url is not None:
		driver.get(url)
		
def switchToMain():
	print('Switch to main tab')
	driver.switch_to.window(driver.window_handles[0])
	driver.switch_to_default_content()
	driver.switch_to.frame(waitForID('sandboxFrame'))
	driver.switch_to.frame(waitForID('userHtmlFrame'))

# -*- coding: utf-8 -*-

import logging

__all__ = ["MainWindow","OptionsWindow", "NewPrice", "PriceSummaryWidget", "About"]

from functools import partial
import time
import json
import os
import traceback

from PySide import QtCore, QtGui
from . import MainWindow
from . import OptionsWindow
from . import NewPrice
from . import PriceSummaryWidget
from . import About

from plugins import Interruption

mainWindow = None
mainWindowUI = None
optionsDialog = None
optionsDialogUI = None

publishThread = None

targets = []
tagGroups = []
actions = {}
loadedPlugins = {}

populationTypes = ['Everybody']
lastTemplateFile = None

from config import settings

def getMainWindow():
	global mainWindow, mainWindowUI
	mainWindow = QtGui.QMainWindow()
	
	mainWindowUI = MainWindow.Ui_MainWindow()
	mainWindowUI.setupUi(mainWindow)
	mainWindowUI.actionOptions.triggered.connect(showOptionsDialog)
	mainWindowUI.actionAbout.triggered.connect(showAboutDialog)

	if len(targets) == 0:
		mainWindowUI.postToGrid.addWidget(QtGui.QLabel('No targets :('))
		
	#@TODO: sort targets according to priority when adding them to UI
	for target in targets:
		index = mainWindowUI.postToGrid.count()
		
		checkbox = QtGui.QCheckBox(mainWindowUI.centralwidget)
		checkbox.setText(target['name'])
		target['checkbox'] = checkbox
		
		mainWindowUI.postToGrid.addWidget(checkbox, index / 2, index % 2, 1, 1)
		
	for group,actionList in actions.items():
		menu = QtGui.QMenu(group, mainWindowUI.menuActions)
		mainWindowUI.menuActions.addMenu(menu)
		for action in actionList:
			menuAction = QtGui.QAction(mainWindow)
			menuAction.triggered.connect(action['callback'])
			menuAction.setText(action['name'])
			menu.addAction(menuAction)		
		
	mainWindowUI.publishButton.clicked.connect(_publishClicked)
	mainWindowUI.actionSave_template.triggered.connect(_saveTemplate)
	mainWindowUI.actionLoad_template.triggered.connect(_loadTemplate)
	
	for tagGroup in tagGroups:
		_layoutTagGroup(tagGroup)
		
	mainWindowUI.registrationURLLaunchButton.clicked.connect(_testRegistrationURL)
	mainWindowUI.addPriceButton.clicked.connect(_showNewPriceWindow)
	
	if os.path.exists('default.js'):
		_loadTemplate('default.js')
	
	return mainWindow
	
#@TODO: allow plugins to add locations to dropdown

def setPlugins(plugins):
	global loadedPlugins
	loadedPlugins = plugins

def showAboutDialog():
	dialog = QtGui.QDialog(mainWindow)
	
	dialogUI = About.Ui_Dialog()
	dialogUI.setupUi(dialog)
	
	dialog.show()


def showOptionsDialog():
	global optionsDialogUI, mainWindow, loadedPlugins
	dialog = QtGui.QDialog(mainWindow)
	
	optionsDialogUI = OptionsWindow.Ui_Dialog()
	optionsDialogUI.setupUi(dialog)
	
	optionsDialogUI.timezone.setCurrentIndex(optionsDialogUI.timezone.findText(settings.value('timezone')))
	optionsDialogUI.timezone.currentIndexChanged[str].connect(partial(settings.setValue, 'timezone'))
	
	optionsDialogUI.logLevel.setCurrentIndex(optionsDialogUI.logLevel.findText(settings.value('logLevel', 'Debug')))
	optionsDialogUI.logLevel.currentIndexChanged[str].connect(partial(settings.setValue, 'logLevel'))
	
	for pluginName, plugin in loadedPlugins.items():
		tab = QtGui.QWidget()
		layout = QtGui.QFormLayout(tab)
		layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)

		for counter,option in enumerate(plugin.options):
			label = QtGui.QLabel(option['name'], tab)
			lineEdit = QtGui.QLineEdit(tab)
			#@TODO: respect option['type'] setting to create different controls in settings dialog
			
			layout.setWidget(counter, QtGui.QFormLayout.LabelRole, label)
			layout.setWidget(counter, QtGui.QFormLayout.FieldRole, lineEdit)
			
			settingName = 'plugin-%s/%s' % (pluginName, option['name'])
			lineEdit.setText(settings.value(settingName))
			
			lineEdit.textEdited.connect(partial(settings.setValue, settingName))
			
		optionsDialogUI.tabWidget.addTab(tab, pluginName)
		
	if settings.value('Plugin priority') is not None:
		savedPriorities = settings.value('Plugin priority').split(',')
		for p in savedPriorities:
			if p in loadedPlugins:
				optionsDialogUI.pluginPriorityList.addItem(p)
				del loadedPlugins[p]
		
	for p in loadedPlugins:
		optionsDialogUI.pluginPriorityList.addItem(p)
		
	def savePriorities():
		priorityList = ''
		for index in range(optionsDialogUI.pluginPriorityList.count()):
			priorityList += optionsDialogUI.pluginPriorityList.item(index).text() + ','
			
		settings.setValue('Plugin priority', priorityList[:-1])
		
	def increasePriority():
		row = optionsDialogUI.pluginPriorityList.currentRow()
		if row > 0:
			item = optionsDialogUI.pluginPriorityList.takeItem(row)
			optionsDialogUI.pluginPriorityList.insertItem(row-1, item)
			optionsDialogUI.pluginPriorityList.setCurrentRow(row-1)
			savePriorities()
		
	def decreasePriority():
		row = optionsDialogUI.pluginPriorityList.currentRow()
		if row < optionsDialogUI.pluginPriorityList.count():
			item = optionsDialogUI.pluginPriorityList.takeItem(row)
			optionsDialogUI.pluginPriorityList.insertItem(row+1, item)
			optionsDialogUI.pluginPriorityList.setCurrentRow(row+1)
			savePriorities()
		
	optionsDialogUI.pluginPriorityUp.clicked.connect(increasePriority)
	optionsDialogUI.pluginPriorityDown.clicked.connect(decreasePriority)
	
	dialog.show()

def addAction(group, name, callback):
	logging.debug('Adding action: %s' % name)
	if group not in actions:
		actions[group] = []
		
	actions[group].append({'name': name, 'callback': callback})

def addTarget(name, plugin, callback):
	logging.debug('Adding target: %s (%s)' % (name, plugin))
	targets.append({'name': name, 'plugin': plugin, 'callback': callback})

def addPopulationType(name):
	logging.debug('Adding population type: %s' % name)
	populationTypes.append(name)
	
def addTagGroup(name, tags):
	logging.debug('Adding tag group: %s' % name)
	group = {'name': name, 'tags': tags}
	tagGroups.append(group)
	if mainWindowUI is not None:
		_layoutTagGroup(group)
	
def _layoutTagGroup(tagGroup):
	tagGroup['checkboxes'] = []
	tagGrid = QtGui.QGridLayout()
	for tag in tagGroup['tags']:
		index = tagGrid.count()
		
		checkbox = QtGui.QCheckBox(mainWindowUI.centralwidget)
		checkbox.setText(tag)
		tagGroup['checkboxes'].append(checkbox)
		
		tagGrid.addWidget(checkbox, index / 2, index % 2, 1, 1)

	mainWindowUI.tagForm.addRow(tagGroup['name'], tagGrid)
		
def removeTagGroup(name):
	logging.debug('Removing tag group: %s' % name)
	for group in tagGroups:
		if group['name'] == name:
			tagGroups.remove(group)
			break
			
	if mainWindowUI is not None:
		for i in range(mainWindowUI.tagForm.rowCount()):
			labelItem = mainWindowUI.tagForm.itemAt(i, QtGui.QFormLayout.LabelRole)
			gridItem = mainWindowUI.tagForm.itemAt(i, QtGui.QFormLayout.FieldRole)
			if labelItem is not None and name == labelItem.widget().text():
				mainWindowUI.tagForm.takeAt(i).widget().deleteLater()
				while gridItem.count() > 0:
					gridItem.takeAt(0).widget().deleteLater()
					
				break

def setDetails(event):
	def setLocation(location):
		for i in range(mainWindowUI.locationInput.count()):
			if location == mainWindowUI.locationInput.itemText(i):
				mainWindowUI.locationInput.setCurrentIndex(i)
				return

		mainWindowUI.locationInput.addItem(location)
		
	def setDateAndTime(dateTime):
		if isinstance(dateTime, str):
			date = QtCore.QDate.fromString(dateTime[:10], 'yyyy-MM-dd')
			mainWindowUI.dateInput.setSelectedDate(date)
			mainWindowUI.startTimeInput.setTime(QtCore.QTime.fromString(dateTime[11:], 'hh:mm:ss'))
		
	def setStopTime(dateTime):
		if isinstance(dateTime, str):
			mainWindowUI.stopTimeInput.setTime(QtCore.QTime.fromString(dateTime[11:], 'hh:mm:ss'))
		
	def setPrices(prices):
		while mainWindowUI.priceList.count() > 0:
			w = mainWindowUI.priceList.takeAt(0).widget()
			w.deleteLater()
			
		for p in prices:
			widget = PriceSummaryListWidget()
			widget.updateDetails(p['name'], p['price'], p['description'], p['availability'])
			mainWindowUI.priceList.addWidget(widget)
			widget.ui.editButton.clicked.connect(partial(_showNewPriceWindow, widget))
		
	def setTags(tags):
		for groupName,group in tags.items():
			for tagGroup in tagGroups:
				if tagGroup['name'] == groupName:
					for b in tagGroup['checkboxes']:
						if b.text() in group:
							b.setChecked(True)
						else:
							b.setChecked(False)
					break

	widgetLookup = {
		'title': mainWindowUI.titleInput.setText,
		'location': setLocation,
		'startTime': setDateAndTime,
		'stopTime': setStopTime,
		'description': mainWindowUI.descriptionInput.setText,
		'registrationURL': mainWindowUI.registrationURLInput.setText,
		'registrationLimit': mainWindowUI.registrationLimitInput.setValue,
		'prices': setPrices,
		'tags': setTags,
	}
	for k,v in event.items():
		if k in widgetLookup:
			logging.debug('Updating %s: %s' % (k, v))
			widgetLookup[k](v)

def _loadTemplate(filename=None):
	global lastTemplateFile
	
	if filename is None:
		filename = QtGui.QFileDialog.getOpenFileName(mainWindow, 'Open template...', lastTemplateFile, 'Event Creater Templates (*.js)')[0]
		
	if filename != '':
		logging.debug('Loading template: ' + filename)
		lastTemplateFile = filename
		with open(filename) as infile:
			data = infile.read()
		
		loadedEvent = json.loads(data)
		today = QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd')
		loadedEvent['startTime'] = today + 'T' + loadedEvent['startTime'][11:]
		loadedEvent['stopTime'] = today + 'T' + loadedEvent['stopTime'][11:]
		
		setDetails(loadedEvent)
	
def _saveTemplate():
	global lastTemplateFile
	
	filename = QtGui.QFileDialog.getSaveFileName(mainWindow, 'Save template as...', lastTemplateFile, 'Event Creater Templates (*.js)')[0]
	if filename != '':
		if '.' not in filename:
			filename += '.js'
			
		logging.debug('Saving template: ' + filename)
		
		event = collectEventDetails()
		del event['priceDescription']
		del event['isFree']

		event['startTime'] = event['startTime'].toString(QtCore.Qt.ISODate)
		event['stopTime'] = event['stopTime'].toString(QtCore.Qt.ISODate)
		
		lastTemplateFile = filename
		with open(filename, 'w') as outfile:
			json.dump(event, outfile, sort_keys=True, indent=4, ensure_ascii=False)
	
def _testRegistrationURL():
	global mainWindowUI
	QtGui.QDesktopServices.openUrl(mainWindowUI.registrationURLInput.text())

def _showNewPriceWindow(summaryWidget=None):
	global mainWindow
	dialog = QtGui.QDialog(mainWindow)
	
	newPriceUI = NewPrice.Ui_Dialog()
	newPriceUI.setupUi(dialog)
	
	for group in populationTypes:
		newPriceUI.restrictionList.addItem(group)
		
	def _addNewPrice(valuesUI, reset):
		if summaryWidget == None:
			widget = PriceSummaryListWidget(None, valuesUI)
			mainWindowUI.priceList.addWidget(widget)
			widget.ui.editButton.clicked.connect(partial(_showNewPriceWindow, widget))
		else:
			summaryWidget.setValuesFromValuesUI(valuesUI)
			dialog.close()
			
		if reset:
			newPriceUI.nameInput.setText('')
			newPriceUI.priceInput.setText('')
			newPriceUI.descriptionInput.setText('')
			for item in newPriceUI.restrictionList.selectedItems():
				newPriceUI.restrictionList.setCurrentItem(item, QtGui.QItemSelectionModel.Clear)
		
	if summaryWidget is not None:
		# we're editing
		newPriceUI.saveButton.clicked.connect(partial(_addNewPrice, newPriceUI, False))
		newPriceUI.saveAndClearButton.deleteLater()
		newPriceUI.closeButton.setText('Cancel')
			
		newPriceUI.nameInput.setText(summaryWidget.name)
		newPriceUI.priceInput.setText('%0.2f' % summaryWidget.price)
		newPriceUI.descriptionInput.setText(summaryWidget.description)

		for populationType in summaryWidget.availability:
			widget = newPriceUI.restrictionList.findItems(populationType, QtCore.Qt.MatchExactly)[0]
			newPriceUI.restrictionList.setCurrentItem(widget)
			
	else:
		newPriceUI.saveButton.clicked.connect(partial(_addNewPrice, newPriceUI, False))
		newPriceUI.saveAndClearButton.clicked.connect(partial(_addNewPrice, newPriceUI, True))
		newPriceUI.saveButton.setText('Add')
		newPriceUI.saveAndClearButton.setText('Add and clear')
		
	newPriceUI.closeButton.clicked.connect(dialog.close)
	dialog.show()

def _getChildren(parent):
	for i in range(parent.count()):
		yield parent.itemAt(i).widget()
		
def _publishClicked():
	global publishThread
	
	if publishThread is None or not publishThread.isRunning():
		if settings.value('Plugin priority') is None or settings.value('Plugin priority') == '':
			QtGui.QMessageBox.warning(None, 'Options not configured', 'Plugin priority must be configured. Please see general options.')
			return
			
		enabledTargets = getEnabledTargets()

		publishThread = PublishThread(enabledTargets)
		publishThread.progressChanged.connect(mainWindowUI.progressBar.setValue)
		publishThread.eventUpdated.connect(setDetails)

		publishThread.started.connect(partial(mainWindowUI.progressBar.setValue, 0))
		publishThread.started.connect(partial(mainWindowUI.progressBar.setEnabled, True))
		publishThread.started.connect(partial(mainWindowUI.publishButton.setText, 'CANCEL'))
		
		publishThread.finished.connect(partial(mainWindowUI.publishButton.setText, 'Publish'))
		publishThread.finished.connect(partial(mainWindowUI.progressBar.setEnabled, False))

		targetsToPrep = list(enabledTargets)
		def prepareNextTarget(*args):
			if len(targetsToPrep) > 0:
				target = targetsToPrep.pop()
				logging.debug('Preparing plugin: %s' % target['name'])
				target['plugin'].prepare(prepareNextTarget)
			else:
				logging.debug('Initiating publish request')
				publishThread.start()
				logging.debug('Thread started?')
				
		prepareNextTarget()
	else:
		logging.debug('Cancelling publish request')
		mainWindowUI.publishButton.setText('Cancelling...')
		publishThread.requestInterruption()
		
def getEnabledTargets():
	enabledTargets = []
	
	for plugin in settings.value('Plugin priority').split(','):
		for target in targets:
			if plugin == target['name']:
				if target['checkbox'].isChecked():
					enabledTargets.append(target)
				break
	return enabledTargets

def collectEventDetails():
	date = mainWindowUI.dateInput.selectedDate()
	startTime = mainWindowUI.startTimeInput.time()
	stopTime = mainWindowUI.stopTimeInput.time()
	
	event = {
		'title': mainWindowUI.titleInput.text(),
		'location': mainWindowUI.locationInput.currentText(),
		'startTime': QtCore.QDateTime(date, startTime),
		'stopTime': QtCore.QDateTime(date, stopTime),
		'description': mainWindowUI.descriptionInput.toPlainText(),
		'registrationURL': mainWindowUI.registrationURLInput.text(),
		'registrationLimit': mainWindowUI.registrationLimitInput.value(),
		'prices': [],
		'tags': {},
		'isFree': True,
		'priceDescription': '',
	}

	for rsvpType in _getChildren(mainWindowUI.priceList):
		event['prices'].append({
			'name': rsvpType.name,
			'price': rsvpType.price,
			'description': rsvpType.description,
			'availability': rsvpType.availability,
		})
		
	priceDescription = 'The price for this event is'
	for i, priceGroup in enumerate(event['prices']):
		if priceGroup['price'] > 0:
			event['isFree'] = False
			priceDescription += ' $%0.2f for %s' % (priceGroup['price'], priceGroup['name'])
		else:
			priceDescription += ' FREE for ' + priceGroup['name']
			
		if len(event['prices']) > 2:
			if i < len(event['prices'])-1:
				priceDescription += ','
		if len(event['prices']) > 1 and i == len(event['prices'])-2:
			priceDescription += ' and'

	if event['isFree']:
		event['priceDescription'] = 'This event is FREE!'
	else:
		event['priceDescription'] = priceDescription + '.'

	for tagGroup in tagGroups:
		event['tags'][tagGroup['name']] = []
		for checkbox in tagGroup['checkboxes']:
			if checkbox.isChecked():
				event['tags'][tagGroup['name']].append(checkbox.text())
				
	return event
	
class PublishThread(QtCore.QThread):
	progressChanged = QtCore.Signal(object)
	eventUpdated = QtCore.Signal(object)
	
	def __init__(self, targets):
		super().__init__(None)
		self.targets = targets
		self.interruptRequested = False
	
	def isInterruptionRequested(self):
		return self.interruptRequested
	
	def requestInterruption(self):
		self.interruptRequested = True
	
	def run(self):
		logging.debug('Publish thread started')
		event = collectEventDetails()
		
		for i,target in enumerate(self.targets):
			if self.isInterruptionRequested():
				break
			
			logging.debug('Sending event to plugin: ' + target['name'])
			try:
				url = target['callback'](event)
				if url is not None:
					logging.info('Received URL from plugin: ' + url)
					QtGui.QDesktopServices.openUrl(url)
					
				self.eventUpdated.emit(event)
				self.progressChanged.emit(100 * float(i+1)/len(self.targets))
			except Interruption as exc:
				logging.debug('Plugin interrupted')
			except Exception as exc:
				#@TODO: Add option to plugins which allows it to halt processing of following plugins if current one fails
				logging.critical(traceback.format_exc())
				

class PriceSummaryListWidget(QtGui.QWidget):
	def __init__(self, parent=None, valuesUI=None):
		super().__init__(parent)
		self.ui = PriceSummaryWidget.Ui_Form()
		self.ui.setupUi(self)
		self.ui.deleteButton.clicked.connect(self.removeMe)
		
		if valuesUI is not None:
			self.setValuesFromValuesUI(valuesUI)
		
	def setValuesFromValuesUI(self, valuesUI):
		availability = []
		for listItemWidget in valuesUI.restrictionList.selectedItems():
			populationType = listItemWidget.text()
			if populationType != 'Everybody':
				availability.append(populationType)

		if valuesUI.priceInput.text() == '':
			price = 0
		else:
			price = float(valuesUI.priceInput.text())
			
		self.updateDetails(
			valuesUI.nameInput.text(),
			price,
			valuesUI.descriptionInput.toPlainText(),
			availability
		)
					
	def updateDetails(self, name, price, description, availability):
		self.name = name
		self.price = price
		self.description = description
		self.availability = availability
		
		self.ui.nameLabel.setText(self.name)
		self.ui.priceLabel.setText('$%0.2f' % self.price)
		
		if len(self.availability) > 0:
			self.ui.iconLabel.setText('®')
		else:
			self.ui.iconLabel.setText(' ')
			
	def removeMe(self):
		self.deleteLater()

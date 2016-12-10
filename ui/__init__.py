# -*- coding: utf-8 -*-

__all__ = ["MainWindow","OptionsWindow", "NewPrice", "PriceSummaryWidget"]

from functools import partial

from PySide import QtCore, QtGui
from . import *

import plugins

mainWindow = None
mainWindowUI = None
optionsDialog = None
optionsDialogUI = None

targets = []
resources = []
tagGroups = []

populationTypes = ['Everybody']

from config import settings

def getMainWindow():
	global mainWindow, mainWindowUI
	mainWindow = QtGui.QMainWindow()
	
	mainWindowUI = MainWindow.Ui_MainWindow()
	mainWindowUI.setupUi(mainWindow)
	mainWindowUI.actionOptions.triggered.connect(showOptionsDialog)

	if len(targets) == 0:
		mainWindowUI.postToGrid.addWidget(QtGui.QLabel('No targets :('))
		
	#@TODO: sort targets according to priority when adding them to UI
	for target in targets:
		index = mainWindowUI.postToGrid.count()
		
		checkbox = QtGui.QCheckBox(mainWindowUI.centralwidget)
		checkbox.setText(target['name'])
		target['checkbox'] = checkbox
		
		mainWindowUI.postToGrid.addWidget(checkbox, index / 2, index % 2, 1, 1)
		mainWindowUI.progressBar.hide()
		
	mainWindowUI.publishButton.clicked.connect(_publishClicked)
	
	if len(resources) == 0:
		mainWindowUI.resourceGrid.addWidget(QtGui.QLabel('No resources :('))
	for resource in resources:
		pass
		#index = mainWindowUI.resourceGrid.count()
		
	for tagGroup in tagGroups:
		tagGroup['checkboxes'] = []
		tagGrid = QtGui.QGridLayout()
		for tag in tagGroup['tags']:
			index = tagGrid.count()
			
			checkbox = QtGui.QCheckBox(mainWindowUI.centralwidget)
			checkbox.setText(tag)
			tagGroup['checkboxes'].append(checkbox)
			
			tagGrid.addWidget(checkbox, index / 2, index % 2, 1, 1)

		mainWindowUI.formLayout.addRow(tagGroup['name'], tagGrid)
		
	mainWindowUI.registrationURLLaunchButton.clicked.connect(_testRegistrationURL)
	mainWindowUI.addPriceButton.clicked.connect(_showNewPriceWindow)
	
	return mainWindow
	
#@TODO: allow plugins to add locations to dropdown

def showOptionsDialog():
	global optionsDialogUI, mainWindow
	dialog = QtGui.QDialog(mainWindow)
	
	optionsDialogUI = OptionsWindow.Ui_Dialog()
	optionsDialogUI.setupUi(dialog)
	
	optionsDialogUI.timezone.setCurrentIndex(optionsDialogUI.timezone.findText(settings.value('timezone')))
	optionsDialogUI.timezone.currentIndexChanged[str].connect(partial(settings.setValue, 'timezone'))
	
	loadedPlugins = []
	for pluginName,plugin in plugins.loaded.items():
		loadedPlugins.append(pluginName)
		
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
			optionsDialogUI.pluginPriorityList.addItem(p)
			loadedPlugins.remove(p)
		
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

def addTarget(name, callback):
	targets.append({'name': name, 'callback': callback})

def addResource(name, callback):
	pass
	
def addPopulationType(name):
	populationTypes.append(name)
	
def addTagGroup(name, tags):
	tagGroups.append({'name': name, 'tags': tags})

def setDetails(event):
	def setDateAndTime(dateTime):
		mainWindowUI.dateInput.setDate(dateTime)
		mainWindowUI.startTimeInput.setTime(dateTime)
		
	widgetLookup = {
		'title': mainWindowUI.titleInput.setText,
#		'location': mainWindowUI.locationInput.setText,
#		'startTime': setDateAndTime,
#		'stopTime': mainWindowUI.stopTimeInput.setTime,
		'description': mainWindowUI.descriptionInput.setText,
		'registrationURL': mainWindowUI.registrationURLInput.setText,
		'registrationLimit': mainWindowUI.registrationLimitInput.setValue,
	}
	for k,v in event.items():
		if k in widgetLookup:
			widgetLookup[k](v)

def _testRegistrationURL():
	global mainWindowUI
	QtGui.QDesktopServices.openUrl(mainWindowUI.registrationURLInput.text())

def _showNewPriceWindow():
	global mainWindow
	dialog = QtGui.QDialog(mainWindow)
	
	newPriceUI = NewPrice.Ui_Dialog()
	newPriceUI.setupUi(dialog)
	
	for group in populationTypes:
		newPriceUI.restrictionList.addItem(group)
		
	newPriceUI.buttonBox.accepted.connect(partial(_addNewPrice, newPriceUI))
	newPriceUI.buttonBox.rejected.connect(dialog.close)
	
	dialog.show()

def _addNewPrice(valuesUI):
	global mainWindowUI
	
	widget = PriceSummaryListWidget(None, valuesUI)
	mainWindowUI.priceList.addWidget(widget)

def _getChildren(parent):
	for i in range(parent.count()):
		yield parent.itemAt(i).widget()

def _publishClicked():
	if mainWindowUI.publishButton.text() == 'CANCEL':
		print('Do cancel...')
		mainWindowUI.publishButton.setText('Publish')
	else:
		#@TODO: Move processing off UI thread
		#@TODO: Show and update progress bar while processing
		#@TODO: Make cancel button work in UI
		if settings.value('Plugin priority') is None or settings.value('Plugin priority') == '':
			QtGui.QMessageBox.warning(None, 'Options not configured', 'Plugin priority must be configured. Please see general options.')
			return

		print('Do publish...')
		mainWindowUI.publishButton.setText('CANCEL')

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
			'resources': [],
			'prices': [],
		}

		for checkbox in _getChildren(mainWindowUI.resourceGrid):
			if type(checkbox) == QtGui.QCheckBox:
				if checkbox.isChecked():
					event['resources'].append(checkbox.text())
		
		for rsvpType in _getChildren(mainWindowUI.priceList):
			event['prices'].append({
				'name': rsvpType.name,
				'price': rsvpType.price,
				'description': rsvpType.description,
				'availability': rsvpType.availability,
			})
			
		event['tags'] = {}
		for tagGroup in tagGroups:
			event['tags'][tagGroup['name']] = []
			for checkbox in tagGroup['checkboxes']:
				if checkbox.isChecked():
					event['tags'][tagGroup['name']].append(checkbox.text())
			
		for plugin in settings.value('Plugin priority').split(','):
			for target in targets:
				if plugin == target['name']:
					if target['checkbox'].isChecked():
						target['callback'](event)
						setDetails(event)
					break

class PriceSummaryListWidget(QtGui.QWidget):
	def __init__(self, parent=None, valuesUI=None):
		super().__init__(parent)
	
		if valuesUI is not None:
			self.name = valuesUI.nameInput.text()
			self.price = float(valuesUI.priceInput.text())
			self.description = valuesUI.descriptionInput.toPlainText()
			self.availability = []
			
			for listItemWidget in valuesUI.restrictionList.selectedItems():
				populationType = listItemWidget.text()
				if populationType != 'Everybody':
					self.availability.append(populationType)
					
		widgetUI = PriceSummaryWidget.Ui_Form()
		widgetUI.setupUi(self)
		
		widgetUI.nameLabel.setText(self.name)
		widgetUI.priceLabel.setText('${:1,.2f}'.format(self.price))
		if len(self.availability) > 0:
			widgetUI.iconLabel.setText('®')
		else:
			widgetUI.iconLabel.setText(' ')

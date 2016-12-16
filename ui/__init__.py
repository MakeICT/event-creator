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
tagGroups = []
actions = {}

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
		
	for group,actionList in actions.items():
		menu = QtGui.QMenu(group, mainWindowUI.menuActions)
		mainWindowUI.menuActions.addMenu(menu)
		for action in actionList:
			menuAction = QtGui.QAction(mainWindow)
			menuAction.triggered.connect(action['callback'])
			menuAction.setText(action['name'])
			menu.addAction(menuAction)		
		
	mainWindowUI.publishButton.clicked.connect(_publishClicked)
	
	for tagGroup in tagGroups:
		_layoutTagGroup(tagGroup)
		
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

def addAction(group, name, callback):
	if group not in actions:
		actions[group] = []
		
	actions[group].append({'name': name, 'callback': callback})

def addTarget(name, callback):
	targets.append({'name': name, 'callback': callback})

def addPopulationType(name):
	populationTypes.append(name)
	
def addTagGroup(name, tags):
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
			
		for populationType in summaryWidget.availability:
			widget = newPriceUI.restrictionList.findItems(populationType, QtCore.Qt.MatchExactly)[0]
			newPriceUI.restrictionList.setCurrentItem(widget)
			
			newPriceUI.nameInput.setText(summaryWidget.name)
			newPriceUI.priceInput.setText('%0.2f' % summaryWidget.price)
			newPriceUI.descriptionInput.setText(summaryWidget.description)
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

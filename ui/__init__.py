# -*- coding: utf-8 -*-

__all__ = ["MainWindow","OptionsWindow",]

from PySide import QtCore, QtGui
from . import *
import plugins

mainWindow = None
mainWindowUI = None
optionsDialog = None
optionsDialogUI = None

targets = []
resources = []

def getMainWindow():
	global mainWindow, mainWindowUI
	mainWindow = QtGui.QMainWindow()
	
	mainWindowUI = MainWindow.Ui_MainWindow()
	mainWindowUI.setupUi(mainWindow)
	mainWindowUI.actionOptions.triggered.connect(showOptionsDialog)

	if len(targets) == 0:
		mainWindowUI.postToGrid.addWidget(QtGui.QLabel('No targets :('))
	for target in targets:
		index = mainWindowUI.postToGrid.count()
		
		checkBox = QtGui.QCheckBox(mainWindowUI.centralwidget)
		checkBox.setText(target['name'])
		mainWindowUI.postToGrid.addWidget(checkBox, index / 2, index % 2, 1, 1)
		
	if len(resources) == 0:
		mainWindowUI.resourceGrid.addWidget(QtGui.QLabel('No resources :('))
	for resource in resources:
		pass
		#index = mainWindowUI.resourceGrid.count()

	
	return mainWindow

def showOptionsDialog():
	global optionsDialogUI
	dialog = QtGui.QDialog(mainWindow)
	
	optionsDialogUI = OptionsWindow.Ui_Dialog()
	optionsDialogUI.setupUi(dialog)
	
	for pluginName,plugin in plugins.loaded.items():
		tab = QtGui.QWidget()
		layout = QtGui.QFormLayout(tab)
		layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)

		for counter,option in enumerate(plugin.options):
			label = QtGui.QLabel(option['name'], tab)
			lineEdit = QtGui.QLineEdit(tab)
			layout.setWidget(counter, QtGui.QFormLayout.LabelRole, label)
			layout.setWidget(counter, QtGui.QFormLayout.FieldRole, lineEdit)
		optionsDialogUI.tabWidget.addTab(tab, pluginName)
	
	dialog.show()

def addTarget(name, callback):
	targets.append({'name': name, 'callback': callback})

def addResource(name, callback):
	pass
	

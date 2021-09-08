#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2021 ryanbuckner
#
# Based on neilk Solcast plugin

################################################################################
# Imports
################################################################################
import indigo
from life360 import life360
import datetime
from geopy.geocoders import Nominatim
from config import authorization_token, password, username


################################################################################
# Globals
################################################################################



################################################################################
class Plugin(indigo.PluginBase):
	########################################
	# Class properties
	########################################

	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)
		self.deviceList = []

	########################################
	def deviceStartComm(self, device):
		self.debugLog("Starting device: " + device.name)
		device.stateListOrDisplayStateIdChanged()

		if device.id not in self.deviceList:
			self.update(device)
			self.deviceList.append(device.id)

	########################################
	def deviceStopComm(self, device):
		self.debugLog("Stopping device: " + device.name)
		if device.id in self.deviceList:
			self.deviceList.remove(device.id)

	########################################
	def runConcurrentThread(self):
		self.debugLog("Starting concurrent thread")
		try:
			pollingFreq = int(self.pluginPrefs['refresh_frequency'])
		except:
			pollingFreq = 5

		try:
			while True:

				self.sleep(1 * pollingFreq)
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
		except self.StopThread:
			pass



	########################################
	def update(self, device):
		# # device.stateListOrDisplayStateIdChanged()
		local_day = datetime.datetime.now().date()
		#
		if str(local_day) != device.states["last_api_update"]:
			device.setErrorStateOnServer('Error')

		return

	########################################
	# UI Validate, Device Config
	########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, device):

		return (True, valuesDict)



	########################################
	# UI Validate, Plugin Preferences
	########################################
	def validatePrefsConfigUi(self, valuesDict):

		return(True,valuesDict)


	def get_member_list(self, filter="", valuesDict=None, typeId="", targetId=0):
		retList = []
		api = life360(authorization_token=authorization_token, username=username, password=password)
		if api.authenticate():
			circles = api.get_circles()
			id = circles[0]['id']
			circle = api.get_circle(id)
			for m in circle['members']:
				retList.append(m['firstName'])
		return retList


	def test_api_auth(self, filter="", valuesDict=None, typeId="", targetId=0):
		return

	############################
	# Action Method
	#############################


	def refresh_member_data(self,pluginAction, device):
		local_day = datetime.datetime.now().date()
		device_states.append({'key': 'last_api_update','value': local_day })
		device.updateStatesOnServer(device_states)
		return


	
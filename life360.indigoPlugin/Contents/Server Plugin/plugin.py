#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2021 ryanbuckner 
# https://github.com/ryanbuckner/life360-plugin/wiki
#
# Based on neilk Solcast plugin

################################################################################
# Imports
################################################################################
import indigo
from life360 import life360
import datetime
from geopy.geocoders import Nominatim


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

		self.authorization_token = self.pluginPrefs['authorizationtoken']
		self.username = self.pluginPrefs['life360_username']
		self.password = self.pluginPrefs['life360_password']
		self.refresh_frequency = self.pluginPrefs['refresh_frequency']

		self.life360data = []

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
			pollingFreq = int(self.pluginPrefs['refresh_frequency']) * 60
		except:
			pollingFreq = 300

		self.debugLog("Current polling frequency is: " + str(pollingFreq) + " seconds")

		try:
			while True:
				self.sleep(1 * pollingFreq)
				self.get_new_life360json()
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
					self.updatedevicestates(indigo.devices[deviceId])
		except self.StopThread:
			pass


	########################################
	def update(self, device):
		self.debugLog(device.name)
		# # device.stateListOrDisplayStateIdChanged()
		return

	########################################
	# UI Validate, Device Config
	########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, device):

		return (True, valuesDict)


	# doesn't do anything, just needed to force other menus to dynamically refresh
	def menuChanged(self, valuesDict = None, typeId = None, devId = None):
		return valuesDict

		
	########################################
	# UI Validate, Plugin Preferences
	########################################
	def validatePrefsConfigUi(self, valuesDict):
		if not (valuesDict['life360_username']):
			self.errorLog("Account Email Cannot Be Empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Account Email Cannot Be Empty"
			return (False, valuesDict, errorsDict)
		if not (valuesDict['life360_password']):
			self.errorLog("Account Password Cannot Be Empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_password'] = "Account Password Cannot Be Empty"
			return (False, valuesDict, errorsDict)
		try:
			self.get_new_life360json()
		except:
			self.errorLog("Error when trying to access life360")
			return (False, valuesDict, errorsDict)

		return (True, valuesDict)



	def get_member_list(self, filter="", valuesDict=None, typeId="", targetId=0):
		retList = []
		api = life360(authorization_token=self.authorization_token, username=self.username, password=self.password)
		if api.authenticate():
			circles = api.get_circles()
			id = circles[0]['id']
			circle = api.get_circle(id)
			for m in circle['members']:
				retList.append(m['firstName'])
		return retList


	def get_new_life360json(self):
		api = life360(authorization_token=self.authorization_token, username=self.username, password=self.password)
		if api.authenticate():
			circles = api.get_circles()
			id = circles[0]['id']
			circle = api.get_circle(id)
			self.life360data = circle
		else:
			self.errorLog("Error retrieving new Life360 JSON")
		return


	############################
	# Action Method
	#############################


	def refresh_member_data(self,pluginAction, device):
		self.get_new_life360json()
		self.updatedevicestates(device)
		return


	def updatedevicestates(self, device):
		device_states = []
		member_device = device.pluginProps['membername']
		self.debugLog("Updating device for username: " + member_device)
		geocoder = Nominatim(user_agent='life360')
		for m in self.life360data['members']:
			if m['firstName'] == member_device:
				device_states.append({'key': 'member_id','value': m['id'] })
				device_states.append({'key': 'member_avatar','value': m['avatar'] })
				device_states.append({'key': 'member_first_name','value': m['firstName'] })
				device_states.append({'key': 'member_last_name','value': m['lastName'] })
				device_states.append({'key': 'member_phone_num','value': m['loginPhone']})
				device_states.append({'key': 'member_email','value': m['loginEmail']})
				device_states.append({'key': 'member_360_location','value': m['location']['name']})
				device_states.append({'key': 'member_battery','value': m['location']['battery']})
				device_states.append({'key': 'member_battery_charging','value': m['location']['charge']})
				device_states.append({'key': 'member_lat','value': float(m['location']['latitude'])})
				device_states.append({'key': 'member_long','value': float(m['location']['longitude'])})
				#device_states.append({'key': 'last_api_update','value': datetime.datetime.now().date()})
				try: 
					# get address from lat long information 
					loclat = float(m['location']['latitude'])
					loclng = float(m['location']['longitude'])
					geoloc = geocoder.reverse((loclat, loclng))
					currentaddress = geoloc
				except GeocoderTimedOut as g:
					self.errorLog(u"Geocoder timed out: " + g.msg, type=plugin_name)
					currentaddress = "unknown - geocoder error"

		device_states.append({'key': 'member_closest_address','value': str(currentaddress) })

		device.updateStatesOnServer(device_states)
		return





	
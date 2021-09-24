#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2021 ryanbuckner 
# https://github.com/ryanbuckner/life360-plugin/wiki
#
# Based on neilk's Solcast plugin

################################################################################
# Imports
################################################################################
import indigo
import sys
from life360 import life360
import datetime
try:
	from geopy.geocoders import Nominatim
except: 
	self.errorLog("Geopy python library is not installed. Closest address location will be black. Install with 'pip install geopy' ")
	pass


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

		self.logger.info(u"")
		self.logger.info(u"{0:=^130}".format("Starting Life360 Plugin Engine"))
		self.logger.info(u"{0:<30} {1}".format("Plugin name:", pluginDisplayName))
		self.logger.info(u"{0:<30} {1}".format("Plugin version:", pluginVersion))
		self.logger.info(u"{0:<30} {1}".format("Plugin ID:", pluginId))
		self.logger.info(u"{0:<30} {1}".format("Refresh Frequency:", str(self.refresh_frequency) + " minutes"))
		self.logger.info(u"{0:<30} {1}".format("Indigo version:", indigo.server.version))
		self.logger.info(u"{0:<30} {1}".format("Python version:", sys.version.replace('\n', '')))
		self.logger.info(u"{0:<30} {1}".format("Python Directory:", sys.prefix.replace('\n', '')))
		self.logger.info(u"{0:=^130}".format(""))

		self.life360data = {}
		self.member_list = {}

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

		# Refresh device states immediately after restarting the Plugin
		iterationcount = 1

		try:
			while True:
				if (iterationcount > 1):
					self.sleep(1 * pollingFreq)
				self.get_new_life360json()
				iterationcount += 1
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


	# assigns the device.address to the value of the member.id
	def menuChanged(self, valuesDict = None, typeId = None, devId = None):
		self.create_member_list()
		self.debugLog(self.member_list)
		if valuesDict['membername'] in self.member_list:
			tempName = valuesDict['membername']
			valuesDict['address'] = self.member_list[tempName] # m['id']
		else:
			valuesDict['address'] = "Unknown"
		return valuesDict

	#dump JSON to event log
	def write_json_to_log(self):
		if (len(self.life360data) == 0):
			self.get_new_life360json()
		self.debugLog(self.life360data)
		if (not self.debug):
			indigo.server.log("Life360 data has been written to the debugLog. If you did not see it you may need to enable debugging in the Plugin Config UI")
		return


	########################################
	# UI Validate, Plugin Preferences
	########################################
	def validatePrefsConfigUi(self, valuesDict):
		if int(valuesDict['refresh_frequency']) < 2:
			self.errorLog("Invalid entry for Refresh Frequency - must be greater than 1")
			errorsDict = indigo.Dict()
			errorsDict['refresh_frequency'] = "Invalid entry for Refresh Frequency - must be greater than 1"
			return (False, valuesDict, errorsDict)

		if (not valuesDict['life360_username']):
			self.errorLog("Invalid entry for Life360 username - cannot be empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - cannot be empty"
			return (False, valuesDict, errorsDict)

		if (valuesDict['life360_username'].find('@') == -1):
			self.errorLog("Invalid entry for Life360 username - must be a valid email address")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - must be a valid email address"
			return (False, valuesDict, errorsDict)

		if (valuesDict['life360_username'].find('.') == -1):
			self.errorLog("Invalid entry for Life360 username - must be a valid email address")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - must be a valid email address"
			return (False, valuesDict, errorsDict)

		if (not valuesDict['life360_password']):
			self.errorLog("Invalid entry for Life360 password - cannot be empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_password'] = "Invalid entry for Life360 password - cannot be empty"
			return (False, valuesDict, errorsDict)

		auth_result = self.validate_api_auth(valuesDict['life360_username'], valuesDict['life360_password'], valuesDict['authorizationtoken'])
		if (not auth_result):
			self.errorLog("Life360 API Authentication failed - check your username and password")
			errorsDict = indigo.Dict()
			errorsDict['life360_password'] = "Life360 API Authentication failed - check your username and password"
			return (False, valuesDict, errorsDict)

		return (True, valuesDict)


	def validate_api_auth(self, username, password, authorization_token):
		api = life360(authorization_token=authorization_token, username=username, password=password)
		try:
			if api.authenticate():
				self.debugLog("Validation of API was successful")
				return True
			else:
				self.errorLog("Validation of API FAILED")
				return False
		except Exception as e:
			self.errorLog("Error authenticating: " + e.msg)
			return False


	def get_member_list(self, filter="", valuesDict=None, typeId="", targetId=0):
		if (len(self.member_list) == 0):
			self.create_member_list()
		retList = list(self.member_list.keys())
		return retList


	def get_new_life360json(self):
		api = life360(authorization_token=self.authorization_token, username=self.username, password=self.password)
		if api.authenticate():
			circles = api.get_circles()
			id = circles[0]['id']
			circle = api.get_circle(id)
			self.life360data = circle
			self.create_member_list()
		else:
			self.errorLog("Error retrieving new Life360 JSON")
		return


	def create_member_list(self):
		if len(self.life360data) == 0:
			self.get_new_life360json()
		self.member_list.clear()
		for m in self.life360data['members']:
			self.member_list[m['firstName']] = m['id']
		return

	def toggleDebugging(self):
		if self.debug:
			indigo.server.log("Turning off debug logging")
			self.debugLog(u"Turning off debug logging (Toggle Debugging menu item chosen).")
			self.pluginPrefs['showDebugInfo'] = False
		else:
			indigo.server.log("Turning on debug logging")
			self.pluginPrefs['showDebugInfo'] = True
			self.debugLog(u"Turning on debug logging (Toggle Debugging menu item chosen).")
			# Turn on/off for the Indigo log level.
		self.debug = not self.debug


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
		self.debugLog("Updating device: " + member_device)
		try: 
			geocoder = Nominatim(user_agent='life360')
		except:
			self.errorLog("Error instantiating geocoder object")
			pass
		for m in self.life360data['members']:
			if m['firstName'] == member_device:
				x = datetime.datetime.now()
				cur_date_time = x.strftime("%m/%d/%Y %I:%M %p")

				device_states.append({'key': 'member_id','value': m['id'] })
				device_states.append({'key': 'member_avatar','value': m['avatar'] })
				device_states.append({'key': 'member_first_name','value': m['firstName'] })
				device_states.append({'key': 'member_last_name','value': m['lastName'] })
				device_states.append({'key': 'member_phone_num','value': m['loginPhone']})
				device_states.append({'key': 'member_email','value': m['loginEmail']})
				device_states.append({'key': 'member_360_location','value': m['location']['name']})
				device_states.append({'key': 'member_battery','value': m['location']['battery']})
				device_states.append({'key': 'member_wifi','value': m['location']['wifiState']})
				device_states.append({'key': 'member_battery_charging','value': m['location']['charge']})
				device_states.append({'key': 'member_lat','value': float(m['location']['latitude'])})
				device_states.append({'key': 'member_long','value': float(m['location']['longitude'])})
				device_states.append({'key': 'member_is_driving','value': m['location']['isDriving']})
				device_states.append({'key': 'last_api_update','value': str(cur_date_time)})
				try: 
					# get address from lat long information 
					loclat = float(m['location']['latitude'])
					loclng = float(m['location']['longitude'])
					geoloc = geocoder.reverse((loclat, loclng))
					currentaddress = geoloc
					sleep(1) # terms of service requirement 
				except Exception as g:
					self.errorLog(u"Geocoder error: " + g.msg, type=plugin_name)
					currentaddress = "unknown - geocoder error"

				device_states.append({'key': 'member_closest_address','value': str(currentaddress) })

				if (m['location']['since']):
					sincedate = datetime.datetime.fromtimestamp(m['location']['since'])
					sincedatestr  = sincedate.strftime("%m/%d/%Y %I:%M %p")
					device_states.append({'key': 'member_location_since_datetime','value': sincedatestr})
				else: 
					device_states.append({'key': 'member_location_since_datetime','value': ''})

				if (m['location']['name'] == "Home"):
					device.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
				else:
					device.updateStateImageOnServer(indigo.kStateImageSel.None)

		device.updateStatesOnServer(device_states)
		return





	
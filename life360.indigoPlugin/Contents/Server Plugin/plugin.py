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
import re
import sys
from life360 import life360
import datetime
try:
	from geopy.geocoders import Nominatim
	from geopy import Point
	from geopy.distance import great_circle
except: 
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
		self.geoDeviceList = []

		try:
			self.authorization_token = self.pluginPrefs.get('authorizationtoken', 'cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg')
			self.authorization_token = "Y2F0aGFwYWNyQVBoZUtVc3RlOGV2ZXZldnVjSGFmZVRydVl1ZnJhYzpkOEM5ZVlVdkE2dUZ1YnJ1SmVnZXRyZVZ1dFJlQ1JVWQ=="
			self.username = self.pluginPrefs.get('life360_username', None)
			self.password = self.pluginPrefs.get('life360_password', None)
			self.refresh_frequency = self.pluginPrefs.get('refresh_frequency', 30)
			self.logger.debug("Success retrieving preferences from Plugin config")
		except:
			self.logger.error("Error retrieving Plugin preferences. Please use Configure to set")

		self.logger.info(u"")
		self.logger.info(u"{0:=^130}".format("Starting Life360 Plugin Engine"))
		self.logger.info(u"{0:<30} {1}".format("Plugin name:", pluginDisplayName))
		self.logger.info(u"{0:<30} {1}".format("Plugin version:", pluginVersion))
		self.logger.info(u"{0:<30} {1}".format("Plugin ID:", pluginId))
		self.logger.info(u"{0:<30} {1}".format("Refresh Frequency:", str(self.refresh_frequency) + " seconds"))
		self.logger.info(u"{0:<30} {1}".format("Indigo version:", indigo.server.version))
		self.logger.info(u"{0:<30} {1}".format("Python version:", sys.version.replace('\n', '')))
		self.logger.info(u"{0:<30} {1}".format("Python Directory:", sys.prefix.replace('\n', '')))
		self.logger.info(u"{0:=^130}".format(""))

		self.life360data = {}
		self.placesdata = {}
		self.member_list = {}
		self.places_list = {}


	########################################
	def deviceStartComm(self, device):
		self.logger.debug("Starting device: " + device.name)
		device.stateListOrDisplayStateIdChanged()

		if device.id not in self.deviceList:
			self.update(device)
			if (device.deviceTypeId == "members"):
				self.deviceList.append(device.id)
			elif  (device.deviceTypeId == "geofence"):
				self.geoDeviceList.append(device.id)

	########################################
	def deviceStopComm(self, device):
		self.logger.debug("Stopping device: " + device.name)
		if device.id in self.deviceList:
			self.deviceList.remove(device.id)
		if device.id in self.geoDeviceList:
			self.geoDeviceList.remove(device.id)

	########################################
	def runConcurrentThread(self):
		self.logger.debug("Starting concurrent thread")
		try:
			pollingFreq = int(self.pluginPrefs['refresh_frequency']) * 1
		except:
			pollingFreq = 60

		self.logger.debug("Current polling frequency is: " + str(pollingFreq) + " seconds")

		# Refresh device states immediately after restarting the Plugin
		iterationcount = 1

		try:
			while True:
				if (iterationcount > 1):
					self.sleep(1 * pollingFreq)
				self.get_new_life360json()
				iterationcount += 1
				self.logger.debug(self.deviceList)
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
					self.updatedevicestates(indigo.devices[deviceId])
				for geoDeviceId in self.geoDeviceList:
					self.updategeodevicestates(indigo.devices[geoDeviceId])
		except self.StopThread:
			pass


	########################################
	def update(self, device):
		#self.logger.debug(device.name)
		# # device.stateListOrDisplayStateIdChanged()
		return

	########################################
	# UI Validate, Device Config
	########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, device):
		if (typeId == 'geofence'):
			if (not valuesDict['geofence_lat']):
				self.logger.error("Geofence latitude is a required field")
				errorsDict = indigo.Dict()
				errorsDict['geofence_lat'] = "Geofence latitude is a required field"
				return (False, valuesDict, errorsDict)

			if (not bool(re.match(r'^[-+]?\d*\.?\d+$', valuesDict['geofence_lat']))):
				self.logger.error("Geofence latitude must be a valid float")
				errorsDict = indigo.Dict()
				errorsDict['geofence_lat'] = "Geofence latitude must be a valid float"
				return (False, valuesDict, errorsDict)

			if (not valuesDict['geofence_long']):
				self.logger.error("Geofence latitude is a required field")
				errorsDict = indigo.Dict()
				errorsDict['geofence_long'] = "Geofence longitude is a required field"
				return (False, valuesDict, errorsDict)

			if (not bool(re.match(r'^[-+]?\d*\.?\d+$', valuesDict['geofence_long']))):
				self.logger.error("Geofence longitude must be a valid float")
				errorsDict = indigo.Dict()
				errorsDict['geofence_long'] = "Geofence longitude must be a valid float"
				return (False, valuesDict, errorsDict)

			if (not valuesDict['geofence_name']):
				self.logger.error("Geofence name is a required field")
				errorsDict = indigo.Dict()
				errorsDict['geofence_name'] = "Geofence name is a required field"
				return (False, valuesDict, errorsDict)

			if (not valuesDict['geofence_radius']):
				self.logger.error("Geofence radius is a required field")
				errorsDict = indigo.Dict()
				errorsDict['geofence_name'] = "Geofence radius is a required field"
				return (False, valuesDict, errorsDict)

		return (True, valuesDict)


	# assigns the device.address to the value of the member.id
	def menuChanged(self, valuesDict = None, typeId = None, devId = None):
		self.create_member_list()
		self.logger.debug(self.member_list)
		if valuesDict['membername'] in self.member_list:
			tempName = valuesDict['membername']
			valuesDict['address'] = self.member_list[tempName] # m['id']
		else:
			valuesDict['address'] = "Unknown"
		return valuesDict


	def populate_places_attributes(self, valuesDict, typeId, devId):
		if valuesDict['places_name'] in self.places_list:
			for p in self.placesdata['places']:
				if (p['name'] == valuesDict['places_name']):
					# assign the values
					valuesDict['geofence_name'] = p['name']
					valuesDict['geofence_lat'] = p['latitude']
					valuesDict['geofence_long'] = p['longitude']
					valuesDict['geofence_radius'] = self.convertMetersToKm(float(p['radius']))
		return valuesDict


	def convert_feet_to_km_props(self, valuesDict, typeId, devId):
		kmRadius = self.convertFeetToKm(float(valuesDict['radius_to_convert']))
		valuesDict['radius_converted_km'] = kmRadius
		return valuesDict


	########################################
	# UI Validate, Plugin Preferences
	########################################
	def validatePrefsConfigUi(self, valuesDict):
		if int(valuesDict['refresh_frequency']) < 15:
			self.logger.error("Invalid entry for Refresh Frequency - must be greater than 15")
			errorsDict = indigo.Dict()
			errorsDict['refresh_frequency'] = "Invalid entry for Refresh Frequency - must be greater than 15"
			return (False, valuesDict, errorsDict)

		if (not valuesDict['life360_username']):
			self.logger.error("Invalid entry for Life360 username - cannot be empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - cannot be empty"
			return (False, valuesDict, errorsDict)

		if (valuesDict['life360_username'].find('@') == -1):
			self.logger.error("Invalid entry for Life360 username - must be a valid email address")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - must be a valid email address"
			return (False, valuesDict, errorsDict)

		if (valuesDict['life360_username'].find('.') == -1):
			self.logger.error("Invalid entry for Life360 username - must be a valid email address")
			errorsDict = indigo.Dict()
			errorsDict['life360_username'] = "Invalid entry for Life360 username - must be a valid email address"
			return (False, valuesDict, errorsDict)

		if (not valuesDict['life360_password']):
			self.logger.error("Invalid entry for Life360 password - cannot be empty")
			errorsDict = indigo.Dict()
			errorsDict['life360_password'] = "Invalid entry for Life360 password - cannot be empty"
			return (False, valuesDict, errorsDict)

		auth_result = self.validate_api_auth(valuesDict['life360_username'], valuesDict['life360_password'], valuesDict['authorizationtoken'])
		if (not auth_result):
			self.logger.error("Life360 API Authentication failed - check your username and password")
			errorsDict = indigo.Dict()
			errorsDict['life360_password'] = "Life360 API Authentication failed - check your username and password"
			return (False, valuesDict, errorsDict)

		self.debug = valuesDict['showDebugInfo']
		self.logger.debug("Debug set to: " + str(self.debug))

		return (True, valuesDict)


	def validate_api_auth(self, username, password, authorization_token):
		return True
		api = life360(authorization_token=authorization_token, username=username, password=password)
		try:
			if api.authenticate():
				self.logger.debug("Validation of API was successful")
				return True
			else:
				self.logger.debug("Validation of API FAILED")
				return False
		except Exception as e:
			self.logger.debug("Error authenticating: " + e.msg)
			return False


	def get_member_list(self, filter="", valuesDict=None, typeId="", targetId=0):
		if (len(self.member_list) == 0):
			self.create_member_list()
		retList = list(self.member_list.keys())
		return retList


	def get_places_list(self, filter="", valuesDict=None, typeId="", targetId=0):
		if (len(self.places_list) == 0):
			self.create_places_list()
		retList = list(self.places_list.keys())
		return retList


	def get_new_life360json(self):
		try:

			api = life360(authorization_token=self.authorization_token, username=self.username, password=self.password)
		except Exception as g:
				self.logger.error(str(g))
				self.logger.error("Error retrieving new Life360 JSON")
				return
		if api.authenticate():
			try:
				self.logger.debug("Attempting to get list of circles and places")
				circles = api.get_circles()
				id = circles[0]['id']
				circle = api.get_circle(id)
				places = api.get_circle_places(id)
				self.life360data = circle
				self.placesdata = places
				self.create_member_list()
				self.create_places_list()
			except Exception as e:
				self.logger.error(str(e))
		else:
			self.logger.error("Error retrieving new Life360 JSON, Make sure you have the correct credentials in Plugin Config")
		return


	def create_member_list(self):
		if len(self.life360data) == 0:
			self.get_new_life360json()
		self.member_list.clear()
		for m in self.life360data['members']:
			self.member_list[m['firstName']] = m['id']
		return


	def create_places_list(self):
		if len(self.life360data) == 0:
			self.get_new_life360json()
		self.places_list.clear()
		for p in self.placesdata['places']:
			self.places_list[p['name']] = p['id']
		self.logger.debug("creating places_list")
		self.logger.debug(self.places_list)


	def toggleDebugging(self):
		if self.debug:
			self.debug = False
			self.logger.info(u"Turning off debug logging (Toggle Debugging menu item chosen).")
			self.pluginPrefs['showDebugInfo'] = False
		else:
			self.debug = True
			self.pluginPrefs['showDebugInfo'] = True
			self.logger.debug(u"Turning on debug logging (Toggle Debugging menu item chosen).")



	############################
	# Action Method
	#############################


	#dump JSON to event log
	def write_json_to_log(self):
		if (len(self.life360data) == 0):
			self.get_new_life360json()
		self.logger.debug(self.life360data)
		if (not self.debug):
			indigo.server.log("Life360 data has been written to the debug Log. If you did not see it you may need to enable debugging in the Plugin Config UI")
		return


	def refresh_member_data(self,pluginAction, device):
		self.get_new_life360json()
		self.updatedevicestates(device)
		return


	def create_quick_geofence(self, pluginAction, device):
		self.logger.info("Action called for creation of temporary geofence")
		# get member information 
		temp_name = device.states['member_first_name']
		temp_long = device.states['member_long']
		temp_lat = device.states['member_lat']
		temp_radius = '0.0762' #later pull this from prefs
		temp_folder = '' #pull this from prefs
		# create a new geofence device 
		self.logger.debug(f"Creating temporary geofence using member info from {temp_name}")
		indigo.device.create(protocol=indigo.kProtocol.Plugin, name='Life360 temp geofence - ' + temp_name, \
			description='Dynamic Geofence', pluginId='com.ryanbuckner.indigoplugin.life360',  \
			deviceTypeId='geofence', props={'geofence_name': 'Life360 temp geofence - ' + temp_name , 'geofence_lat': temp_lat, \
			'geofence_long':temp_long , 'geofence_radius':temp_radius})
		return


	def isDriving(self, speed_int):
		if (round(speed_int) > 1):
			return 1
		else:
			return 0


	def mphSpeed(self, speed_int):
		if speed_int < 2:
			return str(speed_int)
		else: 
			return str(round(2.2 * speed_int))


	def kphSpeed(self, speed_int):
		if speed_int < 2:
			return str(speed_int)
		else: 
			return str(round(1.6093440006147 * 2.2 * speed_int))

	
	def convertFeetToKm(self, radius_feet):
		feet_per_kilometer = 3280.84  # 1 kilometer = 3280.84 feet
		return radius_feet / feet_per_kilometer

	def convertMetersToKm(self, radius_meters):
		return radius_meters / 1000


	def isInsideGeoFence(self, device, memberLat, memberLong):
		fenceLat = device.pluginProps['geofence_lat']
		fenceLong =  device.pluginProps['geofence_long']
		fenceRadius =  device.pluginProps['geofence_radius']
		
		center = Point(fenceLat, fenceLong)
		
		memberPoint = Point(memberLat, memberLong)

		distance = great_circle(center, memberPoint).km
		
		return distance <= float(fenceRadius)


	def updategeodevicestates(self, device):
		device_states = []
		self.logger.debug("Updating Geofence device: " + device.name)
		prevMemberCount = int(device.states['number_of_members_in_geofence'])
		# firstEnteredTimestamp = device.states['first_entered_timestamp']
		# lastExitedTimestamp = device.states['last_existed_timestamp']
		memberCount = 0
		memberList = []
		occupied = False
		x = datetime.datetime.now()
		cur_date_time = x.strftime("%m/%d/%Y %I:%M %p")

		for deviceId in self.deviceList:
			# self.logger.debug(deviceId)
			dev = indigo.devices[deviceId]
			loclat = float(dev.states['member_lat'])
			loclng = float(dev.states['member_long'])
			#self.logger.debug(dev.states)
			self.logger.debug("Checking member " + dev.states['member_first_name'] + " to see if they are in the fence")
			isFenced = self.isInsideGeoFence(device, loclat, loclng)
			if (isFenced):
				self.logger.debug("Member " + dev.states['member_first_name'] + " is in the fence")
				memberCount += 1
				memberList.append(dev.states['member_first_name'])
				occupied = True

		
		if (memberCount > 0):
			if (prevMemberCount == 0):
				firstEnteredTimestamp = cur_date_time
				device_states.append({'key': 'first_entered_timestamp','value': firstEnteredTimestamp })
		elif (memberCount == 0):
			if (prevMemberCount > 0):
				lastExitedTimestamp = cur_date_time
				device_states.append({'key': 'last_existed_timestamp','value': lastExitedTimestamp })

		device_states.append({'key': 'members_in_geofence','value': ', '.join(memberList) })
		device_states.append({'key': 'number_of_members_in_geofence','value': memberCount })
		device_states.append({'key': 'occupied','value': occupied })
		device_states.append({'key': 'last_update','value': cur_date_time })

		if (memberCount > 0):
			device.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
		else:
			device.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)


		device.updateStatesOnServer(device_states)


	def updatedevicestates(self, device):

		device_states = []
		member_device = device.pluginProps['membername']
		member_device_address = device.address
		self.logger.debug("Updating device: " + member_device)
		try: 
			geocoder = Nominatim(user_agent='life360')
		except:
			self.logger.error("Error instantiating geocoder object")
		pass


		try:
			if self.life360data['members']:
				pass
		except Exception as m:
			self.logger.debug("Life360 error when parsing JSON: " + str(m))
			self.logger.info("Life360 JSON file unreadable. Skipping...")
			return


		if self.life360data['members']:
			for m in self.life360data['members']:
				if ((m['id'] == member_device_address) and (m['location'])):
					x = datetime.datetime.now()
					cur_date_time = x.strftime("%m/%d/%Y %I:%M %p")

					# the raw speed from Life360 is exstimated to be MPH/2.2
					adjustedSpeed = self.mphSpeed(float(m['location']['speed']))

					# the raw speed from Life360 is exstimated to be mph * 1.609344
					adjustedSpeedkm = self.kphSpeed(float(m['location']['speed']))

					# the raw Life360 isDriving boolean always comes back 0. Let's use speed to determine isDriving for Indigo
					adjustedDriving = self.isDriving(float(adjustedSpeed))

					device_states.append({'key': 'member_id','value': m['id'] })
					device_states.append({'key': 'member_avatar','value': m['avatar'] })
					device_states.append({'key': 'member_first_name','value': m['firstName'] })
					device_states.append({'key': 'member_last_name','value': m['lastName'] })
					device_states.append({'key': 'member_phone_num','value': m['loginPhone']})
					device_states.append({'key': 'member_email','value': m['loginEmail']})
					device_states.append({'key': 'last_api_update','value': str(cur_date_time)})
					device_states.append({'key': 'member_360_location','value': m['location']['name']})
					device_states.append({'key': 'member_battery','value': m['location']['battery']})
					device_states.append({'key': 'batteryLevel','value': int(float(m['location']['battery']))})
					device_states.append({'key': 'member_wifi','value': m['location']['wifiState']})
					device_states.append({'key': 'member_battery_charging','value': m['location']['charge']})
					device_states.append({'key': 'member_in_transit','value': m['location']['inTransit']})
					device_states.append({'key': 'member_driveSDKStatus','value': m['location']['driveSDKStatus']})
					device_states.append({'key': 'member_lat','value': float(m['location']['latitude'])})
					device_states.append({'key': 'member_long','value': float(m['location']['longitude'])})
					device_states.append({'key': 'member_is_driving','value': adjustedDriving })
					device_states.append({'key': 'member_speed','value': adjustedSpeed })
					device_states.append({'key': 'member_speed_km','value': adjustedSpeedkm })
					

					try: 
						# get address from lat long information 
						loclat = float(m['location']['latitude'])
						loclng = float(m['location']['longitude'])
						geoloc = geocoder.reverse((loclat, loclng))
						currentaddress = geoloc
					except Exception as g:
						self.logger.debug(u"Geocoder error")
						currentaddress = "-geocoder error-"

					try:
						device_states.append({'key': 'member_closest_address','value': str(currentaddress) })
					except:
						device_states.append({'key': 'member_closest_address','value': "" })


					if (m['location']['since']):
						sincedate = datetime.datetime.fromtimestamp(m['location']['since'])
						sincedatestr  = sincedate.strftime("%m/%d/%Y %I:%M %p")
						device_states.append({'key': 'member_location_since_datetime','value': sincedatestr})
					else: 
						device_states.append({'key': 'member_location_since_datetime','value': ''})

					if (m['location']['name'] == "Home"):
						device.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
					else:
						device.updateStateImageOnServer(indigo.kStateImageSel.NoImage)

					for deviceId in self.geoDeviceList:
						# call the update method with the device instance
						isFenced = self.isInsideGeoFence(indigo.devices[deviceId], loclat, loclng)
						if (isFenced):
							#self.logger.debug(m['firstName'] + ' is within the geofence named ' + indigo.devices[deviceId].pluginProps['geofence_name'])
							device_states.append({'key': 'member_within_geofence','value': indigo.devices[deviceId].pluginProps['geofence_name']}) 
						else:
							#self.logger.debug(m['firstName'] + ' is not in the fence named ' + indigo.devices[deviceId].pluginProps['geofence_name'])
							device_states.append({'key': 'member_within_geofence','value': 'None'}) 
					
		
					device.updateStatesOnServer(device_states)

		else:
			pass

		return





	
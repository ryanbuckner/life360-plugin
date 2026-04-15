<img src="https://s2-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/245/300/resized/life360-horizontal-logo-trimmed.png?1558125703" >

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://mit-license.org)
[![Platform](https://img.shields.io/badge/Platform-Indigo-blueviolet)](https://www.indigodomo.com/) 
[![Language](https://img.shields.io/badge/Language-python%203.10-orange)](https://www.python.org/)
[![Requirements](https://img.shields.io/badge/Requirements-Indigo%20v2022.1%2B-green)](https://www.indigodomo.com/downloads.html)
![Releases](https://img.shields.io/github/release-date/ryanbuckner/life360-plugin?color=red&label=latest%20release)


# Life360 Plugin for Indigo Domotics Home Automation
## life360-indigo-plugin for Python3.10
This Indigo Plugin provides a way to connect Indigo to your Life360.com family tracking information. This plugin is only supported for [Indigo Domotics Software ](http://www.indigodomo.com)

### Updated for CloudFlare
This plugin has been updated to use the CloudFlare authentication from pnbruckner/ha-life360.


### What is Life360?

Life360 is a mobile application referred to as a "family-oriented private social network". The app is a social network for families and differentiates itself in this way as it is not based around peer groups or professional networks such as Find My Friends and LinkedIn. It allows users to share locations, group messages, and call for roadside assistance. It has four main features: location sharing, circles, places, and premium.

###### Location sharing
The main feature of the app is location sharing. Users can open the app and see where other members are instantly. Users can choose to share or not their location with any particular circle at any particular time.

###### Circles
Circles allows users to create separate groups within the app, e.g. "caregivers," "extended family," and "John's baseball team." Users' location is only visible to those who are also in the circle, and members in "caregivers" cannot see the location of users in "extended family," unless they are also in that circle.

###### Places
Places are a great way to know when your loved ones are leaving work or just arrived at school. Places are areas you can define so you are alerted when a Circle member enters or leaves a location. Some Places you might want to set up are work, home, and school. Free plans can set up two Places. To set up more Places, upgrade to a Premium plan.

###### Premium
Life360 operates as a freemium app, and users can pay for extra features. These extra features include: stolen phone insurance, access to a live advisor 24/7, unlimited creation of "Places," and emergency roadside assistance (known as 'Driver Protect').

###### Bubbles
Life360 Bubbles is a new way to customize Location Sharing for your Circle. Bubbles is an optional feature and not a default setting. After a temporary Bubble is created, it shares only your approximate location while all safety and messaging features remain on. If a car crash or emergency is detected, Bubbles will automatically burst.

To stay connected with your family during Bubble time, you can message to request a Check-In for their exact location, or use the Message feature to communicate. If you are concerned about safety, you can burst a Bubble at any time.

More information can be found about Life360 [here](https://www.life360.com/support/popular-questions/)

### The Life360 Plugin

The plugin is my first attempt at an Indigo plugin, based on a script I wrote to update variables in Indigo. The Life360 api example was leveraged from the work done by [harperreed](https://github.com/harperreed/life360-python) 

More informaton will be listed [on the GitHub Wiki](https://github.com/ryanbuckner/life360-plugin/wiki)

This plugin is not endorsed or associated with Life360 

###### The plugin currently supports:

1) Support for only 1 Circle. This must be the first Circle in your account
2) Multiple devices that each represent users in your Circle
3) Custom device states of the member device
  - Unique Member ID 
  - First Name
  - Last Name
  - Phone Number 
  - Email Address
  - Avatar (http address) 
  - Battery % 
  - Battery is charging or not
  - Latitude 
  - Longitude
  - Current Geofence
  - Closest known address 
  - Wifi turn on or not
  - Is Driving (boolean determined by speed)
  - Speed (raw Life360 speed * 2.2)
  - Speed (in kph)
  - Location Since Timestamp
  - Last API update 
4) Custom device states of the Life360 Custom Geofence
  - Occupied
  - Number of Members in Geofence 
  - Members in Geofence
  - Last Update Timestamp
  - First Entered Timestamp
  - Last Exited Timestamp 

#### Installation

Download the `life360.indigoPlugin` file and double-click it to install.

> **Note:** This plugin requires Indigo 2022.1 or later running Python 3.

###### Plugin Config

Open the plugin's configuration dialog (Plugins → Life360 → Configure...) and enter:

- **Username:** Your Life360 account email address. Any Circle member's account works. If you don't have a password, use the Life360 app to initiate a password reset.
- **Password:** Your Life360 account password.
- **Refresh Rate:** Time in seconds between API calls to update device states. Minimum is 15 seconds; 30–60 seconds is recommended to avoid rate limiting by Life360's servers.

> **Authentication Token:** This field is no longer needed and can be left at its default value. The plugin now uses the current Life360 API authentication mechanism automatically.

The Plugin Config dialog will not close unless your credentials are successfully authenticated. Check the Indigo Event Log for error details if the dialog does not close.

###### Device Config

1. In Indigo, create a new device (Devices → New...)
2. Set **Type** to `Life360` and **Model** to `Life360 Circle Member`
3. Name the device — using the person's name is recommended (e.g. "Ryan - Life360")
4. Click **Edit Device Settings...**
5. Choose the Circle member this device will represent from the dropdown list
   - If the dropdown is empty, there is likely a credential problem — check the Event Log

###### Geofence Device Config

- Create a new device of Type Life360
  - Model should be `Life360 Custom Geofence`
  - The geofence is a circle comprised of a center and a perimeter based on the radius (in Km) you enter
  - You have the option to pre-populate the name, latitude, longitude, and radius from predefined Life360 app Places definitions. Check the box that says "Use Life 360 Places", choose the place from the dropdown, and press the "populate" button
  - The Geofence radius is defined in Kilometers. If you use the Places option it will be populated for you. If not, use the tool to convert from feet to Km
  - You can create a temporary geofence using the current location of a member via the plugin menu


### Cautions:

This plugin is not endorsed by or affiliated with Life360.

The Life360 API is unofficial and undocumented. Life360 has made breaking API changes in the past; if the plugin stops working, check this repository for updates.

Usage is at your own risk.

### Troubleshooting:

- **Authentication fails:** Life360 changed their API in 2024. Make sure you are running the latest version of this plugin, which uses the updated `api-cloudfront.life360.com` endpoint and current client token.
- **Dropdown is empty in Device Config:** Your credentials may be incorrect, or the API call to fetch circle members failed. Check the Event Log and verify your username and password in Plugin Config.
- **member_is_driving is always 0:** This is expected. The raw `isDriving` field from Life360 is unreliable and always returns 0. The plugin derives driving status from speed instead — any speed above 1 (after conversion) sets `member_is_driving` to true.
- **Speed looks wrong:** The raw Life360 speed value is approximately MPH ÷ 2.2. The plugin multiplies it back by 2.2 to estimate MPH. Values of -1 or 0 mean the member is not moving fast enough to register.
- **Name change not reflected:** If a member changes their name in Life360, open the Indigo device settings and reselect them from the dropdown to re-sync the member ID.
- **Location shows "-geocoder error-":** Reverse geocoding uses the Nominatim service (OpenStreetMap). Occasional failures are normal; the state will update on the next successful poll.
- **The plugin will skip all updates** for devices mapped to a member who has disabled or paused location sharing.




<img src="https://s2-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/245/300/resized/life360-horizontal-logo-trimmed.png?1558125703" >

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://mit-license.org)
[![Platform](https://img.shields.io/badge/Platform-Indigo-blueviolet)](https://www.indigodomo.com/) 
[![Language](https://img.shields.io/badge/Language-python%202.7-orange)](https://www.python.org/)
[![Requirements](https://img.shields.io/badge/Requirements-Indigo%20v7%2B-green)](https://www.indigodomo.com/downloads.html)
![Releases](https://img.shields.io/github/release-date/ryanbuckner/life360-plugin?color=red&label=latest%20release)


# Life360 Plugin for Indigo Domotics Home Automation 
## life360-indigo-plugin
This Indigo Plugin provides a way to connect Indigo to your Life360.com family tracking information. This plugin is only supported for [Indigo Domotics Software ](http://www.indigodomo.com)

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

This version has not been testedby any other users but myself.  It is my first plugin so I look forward to the community adding more features and error handling before it's place in the Indigodomo Plugin Store. More informaton will be listed [on the GitHub Wiki](https://github.com/ryanbuckner/life360-plugin/wiki)

This plugin is not endorsed or associated with Life360 

###### The plugin currently supports:

1) Support for only 1 Circle. This must be the first Circle in your account
2) Multiple devices that each represent users in your Circle
3) Custom device states
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
  - Location Since Timestamp
  - Last API update 

#### Installation

Download the Life360.indigoPlugin file and double click it

###### Plugin Config 
- configure the Plugin by entering:
  - Username: your life360 username (email address). Any account holder in the Circle can use their account. If you don't have a username or password, you can initiate a password change in the app 
  - Password: your life360 password
  - Authentication Token: Leave this value alone
  - Refresh Rate: This is the time (in seonds) between API calls to refresh device states. It's recommended to keep this rate at 15 seconds or more

The Plugin Config Dialog should not close unless your username and password are authenticated.  Check the Event Log for any errors. 

###### Device Config 
- create a new device of Type life360
  - model should be life360 Circle Member 
  - Name your device anything you want. It's preferred to use something indicating the name of the person your device represents
  - Press Edit Device Settings... 
  - Choose the member that this device will represent from the dropdown list. If there is nothing in the dropdown, there maybe a problem with your username and password. Check the event log

### Cautions:

I am not an expert on Life360. I have not yet had the Indigo community test this plugin. 

As this is the first version of my first plugin, so usage is at your own risk ! By using this version you are joining the testing team, thanks for the help.   I would love to hear your feedback and thoughts.

### Troubleshooting:

- If someone changes their name in Life360, you will have to go into their device and reselect them from the dropdown if you make any other changes to the device.
- member_is_driving is now a derived boolean based on the Life360 speed for that member. The raw isDriving status is always returned as 0, so it's ignored
- The Life360 raw speed is a number that appears to be the actual speed in MPH divided by 2.2. This plugin attempts to correct that, but it's an estimate. -1 or 0 means not moving fast enough to register
- The plugin will skip all updates for devices mapped to someone who has disabled or paused location sharing 




# life360-indigo-plugin
## life360-indigo-plugin
This Indigo Plugin provides a way to connect Indigo to your Life360.com family tracking information. This plugin is only supported for [Indigo Domotics Software ](http://www.indigodomo.com)

### What is Life360?

Life360 is a mobile application referred to as a "family-oriented private social network". The app is a social network for families and differentiates itself in this way as it is not based around peer groups or professional networks such as Find My Friends and LinkedIn. It allows users to share locations, group messages, and call for roadside assistance. It has four main features: location sharing, circles, places, and premium.

###### Location sharing
The main feature of the app is location sharing. Users can open the app and see where other members are instantly. Users can choose to share or not their location with any particular circle at any particular time.[19]

###### Circles
Circles allows users to create separate groups within the app, e.g. "caregivers," "extended family," and "John's baseball team." Users' location is only visible to those who are also in the circle, and members in "caregivers" cannot see the location of users in "extended family," unless they are also in that circle.

###### Places
Life360 allows users to create geofences that alert them when another enters or leaves another location.

###### Premium
Life360 operates as a freemium app, and users can pay for extra features. These extra features include: stolen phone insurance, access to a live advisor 24/7, unlimited creation of "Places," and emergency roadside assistance (known as 'Driver Protect').

###### Bubbles
Bubbles allows a user to set a radius of between 1 and 25 miles and a set time frame of 1 to 6 hours. This means you won't be able to see where people are in the Bubbles however safety features and messaging features remain active.

### The Life360 Plugin

The plugin is my first attempt at an Indigo plugin, based on a script I wrote to update variables in Indigo. The Life360 api example was leveraged from the work done by [harperreed](https://github.com/harperreed/life360-python) 

This alpha version has not been testedby any other users but myself.  It is my first plugin so I look forward to the community adding more features and error handling before it's place in the Indigodomo Plugin Store. More informaton will be listed [on the GitHub Wiki](https://github.com/ryanbuckner/life360-plugin/wiki)

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
  - Last API update 

#### Installation

Before installation, please install the geopy library using the following command: 
`sudo pip install geopy`

Download the Life360.indigoPlugin file and double click it

###### Plugin Config 
- configure the Plugin by entering:
  - Username: your life360 username (email address). Any account holder in the Circle can use their account. If you don't have a username or password, you can initiate a password change in the app 
  - Password: your life360 password
  - Authentication Token: Leave this value alone
  - Refresh Rate: This is the time (in minutes) between API calls to refresh device states. It's recommended to keep this rate at 3 minutes or more

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



# life360-indigo-plugin
An Indigo Plugin for the life360 family location sharing API

NOTE: This plugin is still in development and does not yet having working features

This is a very basic Indigo plugin that collects member information from your life360 circle. It is currently restricted to 1 circle. 

This version has very limited functionality and has no configuration validation etc.

Usage:

Create an account on the life360 app which is free for limited use. This has only been tested on life360 premium accounts. 

config.py: 

Currently usernamae and password will be stored in the config file until the UI can store them

In the plugin:

Enter your username and password in the configuaraton

Devices: 

Create a device of plugin life360 and type circle member. Choose the name of your member from the drop down.  Give it any name 

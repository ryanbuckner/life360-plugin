from life360 import life360
import datetime
import indigo
from geopy.geocoders import Nominatim
from config import authorization_token, password, username

plugin_name = "Life 360 Plugin"
#indigo.server.log(u"Starting script...", type=plugin_name)

if __name__ == "__main__":
    try:
        # instantiate the API
        api = life360(authorization_token=authorization_token, username=username, password=password)
        if api.authenticate():
            circles = api.get_circles()
            id = circles[0]['id']
            circle = api.get_circle(id)

            #instantiate the geocorder to reverse lat long into an address
            geocoder = Nominatim(user_agent='life360')

            # grab the information from the life360 json response
            for m in circle['members']:
                bat = int(float(m['location']['battery']))
                loclat = float(m['location']['latitude'])
                loclng = float(m['location']['longitude'])
                location = m['location']['name']
                phone_num = m['communications'][0]['value']
                memberid = m['id']
                first_name = m['firstName']
                charging = m['location']['charge']
                avatar = m['avatar']

                try: 
                    # get address from lat long information 
                    geoloc = geocoder.reverse((loclat, loclng))
                    currentaddress = geoloc
                except GeocoderTimedOut as g:
                    indigo.server.log(u"Geocoder timed out: " + g.msg, type=plugin_name)
                    currentaddress = "unknown - geocoder error"

                # assign user specific informaton to Indigo variables
                if memberid == 'd88322d1-f894-4dca-89b0-9ce0b9eb3281': #Ryan
                    print("This is Ryan - " + first_name)
                elif memberid == '97ded1d4-db31-403b-a9e2-63477a9f9f6b': #Dawn
                    #print("This is Dawn - " + first_name)
                    indigo.variable.updateValue(80336455, value=location)
                    indigo.variable.updateValue(1958153929, value=str(bat))
                    indigo.variable.updateValue(319900190, value=str(loclat))
                    indigo.variable.updateValue(345547923, value=str(loclng))
                    indigo.variable.updateValue(1984283932, value=str(currentaddress))
                    indigo.variable.updateValue(482459252, value=str(charging))
                    indigo.variable.updateValue(1836853387, value=str(avatar))
                elif memberid == '725e209b-05e4-4b32-a66d-05185090056a': #Lexi
                    indigo.variable.updateValue(771386486, value=location)
                    indigo.variable.updateValue(186608979, value=str(bat))
                    indigo.variable.updateValue(915555447, value=str(loclat))
                    indigo.variable.updateValue(1655256712, value=str(loclng))
                    indigo.variable.updateValue(836244599, value=str(currentaddress))
                    indigo.variable.updateValue(44126099, value=str(charging))
                    indigo.variable.updateValue(1909192424, value=str(avatar))
        else:
            print("Error authenticating life360 api. Check your username and password")
    except Exception as e: 
        indigo.server.log(e, "life360 script")
    else:
        pass
        #indigo.server.log("life 360 process successful", plugin_name)


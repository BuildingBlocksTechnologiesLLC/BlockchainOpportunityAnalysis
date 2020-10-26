#Under Construction Locations Function
""" 
Locations.py 
Author: John-Paul Besong
Function: Locations.py was written as backup to NLP.py to enhance location capabilities of the NLP system. 
This function will take in string location text from NLP.py and return a location object ready for conversion to a JSON object
"""
import pycountry
'''
class Location:
    def __init__(self,city,state = "",country=""):
        self.city = city
        if(state != None):
            self.state = state
        if(country != None):
            self.country = country
        self.loc = {"city": self.city, "state":self.state, "country": self.country}

    def print(self):
        print(self.city,",",self.state,",",self.country)
        print(self.loc)

'''

class Location:
    #parse through text of region to identify specific areas
    def __init__(self,region):
        self.reg = region
        self.city = ""
        self.state = ""
        self.country = ""

    def concreteLocation(self):
        #testing for locator
        print(self.reg)
        for elem in self.reg.split(", "):
            print("Looking up", elem)
            try:
                print(pycountry.countries.lookup(elem))
                self.country = (pycountry.countries.lookup(elem)).name
            except:
                print("Could not find: ",elem)


'''
if __name__ == "__main__":
    #loc = Location("Norwhich",country="Greater Oxford")
    #loc.print()
    print("in Locations")
    '''

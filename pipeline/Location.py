#Under Construction Locations Function
""" 
Locations.py 
Author: John-Paul Besong
Function: Locations.py was written as backup to NLP.py to enhance location capabilities of the NLP system. 
This function will take in string location text from NLP.py and return a location object ready for conversion to a JSON object
"""
import pycountry
import pycity as pc
import json
import csv

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
        #need to decide on efficient lookup method for each location
        #Parse through first part of string to see if US city? 

        extra = []
        city = []
        #Extract all city names from csv file
        #Put all us cities in city variable
        with open('us_cities_states.csv',mode='r') as uscities:
            cities  = csv.reader(uscities)

        #print("is NY in cities? ", "New York" in cities)
            for line in cities:
                #print(line," : ",type(line)," : ",line[0])

                city.append(line[0].split("|")[0])
            #print("is NY in lines? ", "New York" in cities)

        
        #print("Here are the cities: ", sorted(set(city)))
        #print('Dallas' in city)


        #testing for locator
        print(self.reg)
        for elem in self.reg.split(", "):
            print("Looking up", elem)
            try:
                print(pycountry.countries.lookup(elem))
                self.country = (pycountry.countries.lookup(elem)).name
            except:
                print("Could not find: ",elem)
                extra.append(elem)
                
        print(elem in city, ". ",elem, " in city?")

        if(self.country != 'United States of America' and self.city == ""):
            self.city = " ".join(extra)

        
                


        

       



if __name__ == "__main__":
    #loc = Location("Norwhich",country="Greater Oxford")
    #loc.print()
    #print("in Pycity testing")
     #Pycity Testing 
    #print(pc.cities.get(code='US-NY'))
    print("Looking for locs")
    



    

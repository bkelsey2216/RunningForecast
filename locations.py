import json
import gzip

"""
Classes with static functions to handle parsing bulk data files,
e.g. city.list.json.gz, needed to convert City ID <=> City Name.
Uses global variables to avoid multiple parses.
"""

DATA_DIR = "data"
CITY_FILE = "city.list.json.gz"

BY_ID = {}
BY_NAME = {}

class LocationParser:

    @staticmethod
    def nameIdHook(city):
        global BY_NAME
        global BY_ID

        # JSON custom object_hook to create 2 indices, by name and ID
        # for faster lookups
        if city.get("coord"):
            BY_NAME[city["name"]] = {"id" : city["id"], 
                                    "coord" : city["coord"],
                                    "country" : city["country"]}
            BY_ID[int(city["id"])] = {"name" : city["name"], 
                                    "coord" : city["coord"],
                                    "country" : city["country"]}

        return city

    @staticmethod
    def parseCityFile():

        # only parse city file again if we don't have it already
        if not len(BY_ID):
            print("Parsing city locations...")
            with gzip.open(("%s/%s" % (
                DATA_DIR, CITY_FILE)), "r") as gzf:
                json.load(gzf, object_hook=LocationParser.nameIdHook)
            print("Done parsing city locations.")

class CityFinder:

    @staticmethod
    def getCityIdFromName(name):
        # Warmup the locations if necessary
        # No other class besides CityFinder needs to know
        # about the existence of the file.
        LocationParser.parseCityFile()

        global BY_NAME
        try:
            return BY_NAME[name]["id"]
        except KeyError as err:
            print("KeyError: %s" % err)
            return -1

    @staticmethod
    def getCityNameFromId(cityId):
        LocationParser.parseCityFile()
        global BY_ID
        try:
            return BY_ID[cityId]["name"]
        except KeyError as err:
            print("KeyError: %s" % err)
            return ""

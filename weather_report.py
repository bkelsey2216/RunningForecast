from internal import config, api
from locations import LocationParser, CityFinder
from scorer import Scorer
import requests
import json
import os
from datetime import datetime

SAMPLE_DIR = "samples"
FIVE_DAY = "fiveday.json"
CURRENT = "current.json"

SUCCESS_CODE = 200
ERROR_CODE = 400
CITY_NOT_FOUND = 404

SAMPLE_CITIES = {"New York" : 5128581, 
                "London" : 5367815, 
                "Florence" : 5727032, 
                "Madrid" : 4865871}

class WeatherReport:

    def __init__(self, identifier=None):
        global SAMPLE_CITIES

        if not identifier:
            raise Exception("WeatherReport requires one of ID or City Name")

        if isinstance(identifier, str):
            self.__name = identifier

            # avoid expensive file parsing for now
            if self.__name in SAMPLE_CITIES:
                self.__cityId = SAMPLE_CITIES[self.__name]
            else:
                self.__cityId = CityFinder.getCityIdFromName(self.__name)

        elif isinstance(identifier, int):
            self.__cityId = identifier
            self.__name = CityFinder.getCityNameFromId(self.__cityId)
        else:
            raise Exception("WeatherReport identifier must be int or string")

    # Define a string representation for the weather, allows f"{WeatherReport}"
    def __str__(self):
        return f"Name: {self.__name}, ID: {self.cityId}"

    # Public Methods
    def getBestTimesToRun(self):
        forecast = self.getForecast()

        groupedScores = {}
        for entry in forecast:
            
            asDatetime = datetime.fromtimestamp(entry['dt'])
            weatherDict = {}

            weatherDict['datetime'] = asDatetime
            weatherDict['temp'] = entry['main']['temp']
            weatherDict['wind'] = entry['wind']['speed']
            weatherDict['humidity'] = entry['main']['humidity']
            weatherDict['sky'] = {"parentCat" : entry['weather'][0]['main'], 
                                  "subCat" : entry['weather'][0]['description'],
                                  "precip" : 0.0 }
            
            if "Rain" == entry['weather'][0]['main']:
                weatherDict['sky']['precip'] = entry['rain']['3h']
            elif "Snow" == entry['weather'][0]['main']:
                weatherDict['sky']['precip'] = entry['snow']['3h']

            timeScore = Scorer(weatherDict).score

            day = asDatetime.strftime("%m/%d/%Y")
            time = asDatetime.strftime("%H:%M:%S")
            # print((time, timeScore))
            groupedScores.setdefault(day, [])
            groupedScores[day].append((time, timeScore))

        bestTimes = {}
        for date, times in groupedScores.items():
            bestTime = ("", 999.0)
            for time in times:
                if time[1] < bestTime[1]:
                    bestTime = time
            bestTimes[date] = bestTime
        
        return bestTimes    

    def getCurrent(self):
        currentSample = f"{SAMPLE_DIR}/{self.__name}_{CURRENT}"
        currentURL = self.buildCurrentById()
        return self.callAPIAndStore(currentURL, currentSample) 

    def getForecast(self):
        fiveDaySample = f"{SAMPLE_DIR}/{self.__name}_{FIVE_DAY}"
        forecastURL = self.buildForecastById()
        return self.callAPIAndStore(forecastURL, fiveDaySample)["list"]

    # Other accessors
    @property
    def name(self):
        return self.__name
    
    @property
    def cityId(self):
        return self.__cityId

    # API interaction handled here
    # If data in sample file exists, use that. Otherwise get fresh API call.
    # TODO: Smarter sample file handling
    def callAPIAndStore(self, url, sampleFile):
        if os.path.exists(sampleFile):
            with open(sampleFile, "r") as sf:
                loaded = json.load(sf)
            
            rc = int(loaded["cod"])
            if rc == SUCCESS_CODE:
                return loaded
            elif rc == ERROR_CODE:
                print("Stored data has error, retrying...")
            elif rc == CITY_NOT_FOUND:
                print("City not found, returning")
                return {}
        
        print(f"Making fresh API request with URL: {url}")    
        response = requests.get(url)
        asJson = response.json()
        rc = int(asJson["cod"])
        if rc != SUCCESS_CODE:
            print(f"New response contains error, dumping:\n{asJson}")
            return {}
        else:
            with open(sampleFile, "w") as sf:
                json.dump(asJson, sf)
                print("Wrote response JSON to sample file.")
            
            return asJson


    # API Query Builders
    def buildForecastById(self) :
        return api.API_BASE.format(api_tail=api.FORECAST_DAY_BY_ID.format(city_id=self.__cityId), api_key=config.WEATHER_KEY)
    
    def buildCurrentById(self) :
        return api.API_BASE.format(api_tail=api.CURRENT_BY_ID.format(city_id=self.__cityId), api_key=config.WEATHER_KEY)
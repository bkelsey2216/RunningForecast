import math
import datetime
"""
Handles assigning scores to relevant parts of the weather forecast
Input: Weather dictionary, expected format:
        {
            "temp" : 49.1
            "windspeed" 10.3
            "humidity" : 82
            "sky" : {
                "parentCat" : "Rain"
                "subCat" : "light rain"
                "precip" : 0.345
            }
        }
       Preferences Dictionary, expected format:
        {
            "optimalTemp": 55.0,
            "preferCold" : True, # weights positive temps heavily
            "preferEarly" : False  # weights morning more heavily
        }
Output: Score of relative difficult of the run

All scores should be normalized to a range of 1-10,
with a higher score indicating more difficult weather.
"""

DEFAULT_PREF = {
        "optimalTemp": 55.0,
        "preferCold" : True, # weights positive temps heavily
        "preferEarly" : False  # weights morning more heavily
    }

class Scorer:

    def __init__(self, weather, preferences={}):
        if not len(weather):
            raise Exception("Weather forecast cannot be empty!")
    
        if not weather.get('datetime'):
            raise Exception("Datetime cannot be empty!")
        
        # input
        self.__datetime = weather.get("datetime")
        self.__weather = weather
        self.__preferences = preferences

        self.setDefaultPreferences()

        # output
        self.__score = 0
        self.runScore()

    @property
    def score(self):
        return self.__score
    
    def setDefaultPreferences(self):
        global DEFAULT_PREF
        for pref, val in DEFAULT_PREF.items():
            if pref not in self.__preferences:
                self.__preferences[pref] = val

    def runScore(self):
        self.scoreWeather()
        self.scoreTime()
    
    def scoreWeather(self):
        self.scoreTemp()
        self.scoreHumidity()
        self.scoreWind()
        self.scoreSky()  # TODO: expand to include precipitation

    def scoreTemp(self):
        """
            Normalize squared distance from optimal temperature,
            Then multiply by 10 to get to 0-10 range.
        """
        # Farenheit; should be made configurable later
        maxTemp = 125.0
        minTemp = -20.0

        optimal = self.__preferences["optimalTemp"]
        expected = self.__weather['temp']

        score = 10*(math.sqrt(((expected - optimal) - minTemp)**2))/(maxTemp - minTemp)

        if ((expected > optimal and self.__preferences["preferCold"]) or 
            (expected < optimal and not self.__preferences["preferCold"])) :
            score *= 2

        # print(f"Set temp score: {score}")
        self.__score += score

    def scoreHumidity(self):
        """
        Humidity is already on a scale of 0-100.
        Higher score given to higher humidity.
        """
        score = ((self.__weather['humidity'])**2/100)/10
        # print(f"Set humidity score: {score}")
        self.__score += score
    
    def scoreWind(self):
        """
        Grade wind based on arbitrary scale of 0-65mph
        Higher score given to higher wind.
        """

        # Imperial; should be made configurable later
        maxSpeed = 65.0

        # Normalized; minspeed = 0.
        score = (self.__weather['wind'])/(maxSpeed)

        # print(f"Set wind score: {score}")
        self.__score += score
    
    def scoreSky(self):
        """
        Sky Scale:
            "Clouds" ("few clouds", "broken clouds", "overcast clouds"),
            "Clear" ("clear sky")
            "Rain" ("light rain", "moderate rain")
            "Snow" ("light snow", "moderate snow")

            0: "overcast clouds"
            1: "few clouds", "broken clouds"
            3: "clear sky"
            6: "light rain", "light snow"
            8: "moderate rain", "moderate snow"
            10: "heavy rain", "heavy snow"
        """

        score = 0
        if self.__weather['sky']['parentCat'] == "Clear":
            score += 3

        elif self.__weather['sky']['parentCat'] == "Clouds":
            if ("light" in self.__weather['sky']['subCat'] or 
            "broken" in self.__weather['sky']['subCat'] or
            "few" in self.__weather['sky']['subCat']):
                score += 1
            elif "overcast" in self.__weather['sky']['subCat']:
                score += 0
            else:
                print(f"Unrecognized subcategory {self.__weather['sky']['subCat']}; using default of 5")
                score += 5

        elif (self.__weather['sky']['parentCat'] == "Rain" or
            self.__weather['sky']['parentCat'] == "Snow"):
            if "light" in self.__weather['sky']['subCat']:
                score += 6
            elif "moderate" in self.__weather['sky']['subCat']:
                score += 8
            elif "heavy" in self.__weather['sky']['subCat']:
                score += 10
            else:
                print("Unrecognized sub category; using default of 5")
                score += 5
        else:
            print("Unrecognized parent category; ignoring sky in score.")

        # print(f"Set sky score: {score}")
        self.__score += score

    def scoreTime(self):
        """
        Time scale:
            0-10 based on personal preference
            99 - Night time (12AM, 3AM), exclude
            8 = Morning run, 6AM
            6 = Evening run, 9PM
            4 = Afternoon run, 12PM, 3PM
            2 = Early evening run, 6PM
        """
        score = 0
        time = self.__datetime.strftime("%H:%M:%S")
        if time < "05:30:00":
            score = 9
        elif time > "05:30:00" and time <= "07:30:00":
            score = 5
        elif time > "07:30:00" and time <= "18:30:00":
            weekno = (self.__datetime).weekday()
            if weekno < 5:
                score = 99
            else:
                score = 4
        elif time > "18:30:00" and time <= "21:30:00" :
            score = 2
        elif time > "21:00:00":
            score = 8
        else:
            score = 99
        
        if self.__preferences["preferEarly"]:
            score = math.abs(score - 10)
        
        # print(f"Set time score: {score}")
        self.__score += score
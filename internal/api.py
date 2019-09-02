API_BASE = "https://api.openweathermap.org/data/2.5{api_tail}&units=imperial&APPID={api_key}"
FORECAST_DAY_BY_ID = "/forecast?id={city_id}"
FORECAST_DAY_BY_CITY = "/forecast?q={city_name},{country_code}"
CURRENT_BY_CITY = "/weather?q={city_name}"
CURRENT_BY_CITY_AND_COUNTRY = "/weather?q={city_name},{country_code}"
CURRENT_BY_ID = "/weather?id={city_id}"
CURRENT_BY_LAT_LONG = "/weather?lat={lat}&lon={lon}"

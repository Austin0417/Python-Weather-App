

class WeatherData:
    def __init__(self, data):
        self.id = data['weather'][0]['id']
        self.description = data['weather'][0]['description']
        self.currentCondition = data['weather'][0]['main']
        self.temperature = data['main']['temp']
        self.humidity = data['main']['humidity']
        self.windSpeed = data['wind']['speed']

    def getCurrentWeather(self):
        if self.id == 200 or self.id == 201 or self.id == 202 or self.id == 210 or self.id == 211 or self.id == 212 or self.id == 221 or self.id == 230 or self.id == 231 or self.id == 232:
            # THUNDERSTORM
            return "Thunderstorm"
            
        elif self.id == 300 or self.id == 301 or self.id == 302 or self.id == 310 or self.id == 311 or self.id == 312 or self.id == 313 or self.id == 314 or self.id == 321:
            # DRIZZLE
            return "Drizzle"
            
        elif self.id == 500 or self.id == 501 or self.id == 502 or self.id == 503 or self.id == 504 or self.id == 511 or self.id == 520 or self.id == 521 or self.id == 522 or self.id == 531:
            # RAIN
            return "Rain"
            
        elif self.id == 600 or self.id == 601 or self.id == 602 or self.id == 611 or self.id == 612 or self.id == 613 or self.id == 615 or self.id == 616 or self.id == 620 or self.id == 621 or self.id == 622:
            # SNOW
            return "Snow"
            
        elif self.id == 701:
            # MIST
            return "Mist"
            
        elif self.id == 711:
            # SMOKE
            return "Smoke"
            
        elif self.id == 721:
            # HAZE
            return "Haze"
            
        elif self.id == 731:
            # SAND/DUST WHIRLS
            return "Sand/Dust Whirls"
            
        elif self.id == 741:
            # FOG
            return "Fog"
            
        elif self.id == 751:
            # SAND
            return "Sand"
            
        elif self.id == 761:
            # DUST
            return "Dust"
            
        elif self.id == 762:
            # VOLCANIC ASH
            return "Volcanic Ash"
            
        elif self.id == 771:
            #SQUALLS
            return "Squalls"
            
        elif self.id == 781:
            # TORNADO
            return "Tornado"
            
        elif self.id == 800:
            # CLEAR
            return "Clear"
            
        else:
            # CLOUDS
            return "Clouds"
            

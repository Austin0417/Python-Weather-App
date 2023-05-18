

class GeoData:
    def __init__(self, geoData=None, location=None, latitude=None, longitude=None):
        if geoData:
            self.location = geoData['results'][0]['formatted_address']
            self.latitude = geoData['results'][0]['geometry']['location']['lat']
            self.longitude = geoData['results'][0]['geometry']['location']['lng']
        else:
            self.location = location
            self.latitude = latitude
            self.longitude = longitude






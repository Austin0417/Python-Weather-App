

class GeoData:
    def __init__(self, geoData):
        self.location = geoData['results'][0]['formatted_address']
        self.latitude = geoData['results'][0]['geometry']['location']['lat']
        self.longitude = geoData['results'][0]['geometry']['location']['lng']
        self.status = geoData['status']



# Function to map latitude and longitude to NESDIS sector
def latlon_to_sector(lat, lon):

#I hate this
#There should be an option for "satellite PSW" or something instead of just basing it off of the lat/lon of the user

    if 25 <= lat <= 50 and -125 <= lon <= -66:
        if lon <= -109:
            return "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/CONUS/GEOCOLOR/416x250.jpg"  # Western US
        else:
            return "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/625x375.jpg"  # Eastern US
    elif lat >= 54 and lat <= 72 and lon >= -170 and lon <= -130:
        return "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/SECTOR/ak/GEOCOLOR/250x250.jpg"  # Alaska
    elif lat >= 18 and lat <= 23 and lon >= -161 and lon <= -154:
        return "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/SECTOR/hi/GEOCOLOR/300x300.jpg"  # Hawaii
    elif lat >= 17 and lat <= 19 and lon >= -68 and lon <= -65:
        return "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/pr/GEOCOLOR/300x300.jpg"  # Puerto Rico
    elif lat >= 49 and lat <= 61 and lon >= -10 and lon <= 2:
        return "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/na/GEOCOLOR/450x270.jpg"  # UK
    elif lat >= 36 and lat <= 42 and lon >= -10 and lon <= -6:
        return "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/na/GEOCOLOR/450x270.jpg"  # Portugal
    else:
        return f"https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/678x678.jpg"  # Full Disk
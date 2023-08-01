import math

EARTH_RADIUS = 3959 #miles

DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'] #2nd N to simplify overruns

def degrees_to_direction(angle):
    """
    Converts an angle to a cardinal or intercardinal direction
    """
    return DIRECTIONS[round(angle/45)%8]

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the bearing and surface distance for 1->2 on a sphere
    Shamelessly derived from chatgpt code.
    """
    rad_lat1 = math.radians(float(lat1))
    rad_lon1 = math.radians(float(lon1))
    rad_lat2 = math.radians(float(lat2))
    rad_lon2 = math.radians(float(lon2))

    delta_lon = rad_lon2 - rad_lon1

    y = (math.sin(delta_lon) * math.cos(rad_lat2))
    x = (
        (math.cos(rad_lat1) * math.sin(rad_lat2)) 
        - (math.sin(rad_lat1) * math.cos(rad_lat2) * math.cos(delta_lon))
    )
    
    bearing = math.atan2(y,x)
    bearing = (math.degrees(bearing)+360)%360

    delta_sigma = math.acos(
        (math.sin(rad_lat1) * math.sin(rad_lat2)) 
        + (math.cos(rad_lat1) * math.cos(rad_lat2) * math.cos(delta_lon))
    )
    
    distance = EARTH_RADIUS * delta_sigma

    return bearing, distance

def reverse_haversine(lat1, lon1, distance, bearing):
    """
    Given a point, bearing and distance, this calculates the endpoint on a sphere
    Shamelessly derived from chatgpt code.
    """
    rad_lat1 = math.radians(float(lat1))
    rad_lon1 = math.radians(float(lon1))

    d = distance / EARTH_RADIUS

    rad_lat2 = math.asin(
        (math.sin(rad_lat1) * math.cos(d)) 
        + (math.cos(rad_lat1) * math.sin(d) * math.cos(bearing))
    )

    rad_lon2 = rad_lon1 
    rad_lon2 += math.atan2(
        math.sin(bearing) * math.sin(d) * math.cos(rad_lat1), 
        math.cos(d) - (math.sin(rad_lat1) * math.sin(rad_lat2))
    )

    lat2 = math.degrees(rad_lat2)
    lon2 = math.degrees(rad_lon2)

    return lat2, lon2

def bounding_box(lat, lon, dist): 
    """
    Given point coords and a distance, this creates a bounding box in Airnow format
    """
    coords = [reverse_haversine(lat,lon,dist,x) for x in [0, math.pi, math.pi/2, 3*math.pi/2]]
    return f"{coords[3][1]:.6f},{coords[1][0]:.6f},{coords[2][1]:.6f},{coords[0][0]:.6f}"



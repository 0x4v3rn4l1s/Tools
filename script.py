#!/usr/bin/env python3

import math
import os
import googlemaps
import requests
import argparse


# Necessary functions

def getPathLength(lat1,lng1,lat2,lng2):
    R = 6371000
    lat1rads = math.radians(lat1)
    lat2rads = math.radians(lat2)
    deltaLat = math.radians((lat2-lat1))
    deltaLng = math.radians((lng2-lng1))
    a = math.sin(deltaLat/2) * math.sin(deltaLat/2) + math.cos(lat1rads) * math.cos(lat2rads) * math.sin(deltaLng/2) * math.sin(deltaLng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def getDestinationLatLong(lat,lng,azimuth,distance):
    R = 6378.1 #Radius of the Earth in km
    brng = math.radians(azimuth) #Bearing is degrees converted to radians.
    d = distance/1000 #Distance m converted to km
    lat1 = math.radians(lat) #Current dd lat point converted to radians
    lon1 = math.radians(lng) #Current dd long point converted to radians
    lat2 = math.asin(math.sin(lat1) * math.cos(d/R) + math.cos(lat1)* math.sin(d/R)* math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d/R)* math.cos(lat1), math.cos(d/R)- math.sin(lat1)* math.sin(lat2))
    #convert back to degrees
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return[lat2, lon2]

def calculateBearing(lat1,lng1,lat2,lng2):
    startLat = math.radians(lat1)
    startLong = math.radians(lng1)
    endLat = math.radians(lat2)
    endLong = math.radians(lng2)
    dLong = endLong - startLong
    dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
    if abs(dLong) > math.pi:
         if dLong > 0.0:
             dLong = -(2.0 * math.pi - dLong)
         else:
             dLong = (2.0 * math.pi + dLong)
    bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;
    return bearing

def getPairs(interval,azimuth,lat1,lng1,lat2,lng2):
    # Return every possible coordinate pair between start and end point giving internal

    d = getPathLength(lat1,lng1,lat2,lng2)
    remainder, dist = math.modf((d / interval))
    counter = float(interval)
    coords = []
    coords.append([lat1,lng1])
    for distance in range(0,int(dist)):
        coord = getDestinationLatLong(lat1,lng1,azimuth,counter)
        counter = counter + float(interval)
        coords.append(coord)
    coords.append([lat2,lng2])
    return coords
def get_street_view_images(path_coordinates, save_directory):
    try:
        for i, (lat, lng) in enumerate(path_coordinates):
            # Generate Street View image URL
            streetview_url = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{lng}&size=600x600&key={api_key}&fov=120&heading=65&pitch=-1" # You can change the FOV,heading and pitch to any value you like. For more information, check the Google maps API docs!

            # Make a request to the Street View API and save the image
            response = requests.get(streetview_url)
            if len(response.content)==8605:
                continue
            image_path = os.path.join(save_directory, f"streetview_{i}.png")

            with open(image_path, 'wb') as f:
                f.write(response.content)
           

    except Exception as e:
        print(f"Error capturing Street View images: {e}")
        exit()

def run():
    save_directory = "streetview_images"
    os.makedirs(save_directory, exist_ok=True)
    get_street_view_images(path_coordinates, save_directory)


if __name__ == "__main__":

    # Parse arguments
    parser= argparse.ArgumentParser(description='I will gather streetview images for you between two specified points given their latitude and longitude!')
    parser.add_argument('-k','--api-key',help='Your googlemaps API key',required=True)
    parser.add_argument('-lat1','--latitude1',help='The latitude of the starting point',required=True,type=float)
    parser.add_argument('-lat2','--latitude2',help='The latitude of the end point',required=True,type=float)
    parser.add_argument('-lng1','--longitude1',help='The longitude of the starting point',required=True,type=float)
    parser.add_argument('-lng2','--longitude2',help='The longitude of the end point',required=True,type=float)
    parser.add_argument('-i','--interval',help='Interval to calculate the coordinate pairs between',default=5.0,type=float)
    args=parser.parse_args()

    api_key=args.api_key
    lat1=args.latitude1
    lat2=args.latitude2
    lng1=args.longitude1
    lng2=args.longitude2
    interval=args.interval

    # Get the coordinate pairs

    azimuth=calculateBearing(lat1,lng1,lat2,lng2)
    pairs=getPairs(interval,azimuth,lat1,lng1,lat2,lng2)

    # Use the pairs to get the streetview images

    gmaps = googlemaps.Client(key=api_key)

    path_coordinates=pairs
    run()
    print('Images saved!')
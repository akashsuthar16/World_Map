from multiprocessing import context
from turtle import color, distance
from django.shortcuts import render , get_object_or_404
from .models import *
from .forms import *
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo,get_center_coordinates,get_zoom,get_ip_address
import folium

# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolcator = Nominatim(user_agent='measurements')

    ip_ = get_ip_address(request)
    print(ip_)
    ip = '43.241.194.77'
    country,city,lat,lon = get_geo(ip)
    # print('location country',country)
    # print('location city',city)
    # print('location lat,lon',lat,lon)

    location = geolcator.geocode(city)
    # print('###',location)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat,l_lon) 

    # initial folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat,l_lon), zoom_start=8)
    # location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'], icon=folium.Icon(color='red')).add_to(m)

    if  form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolcator.geocode(destination_)
        # print(destination)
        d_lat = destination.latitude
        d_lon = destination.longitude

        pointB = (d_lat,d_lon)

        distance = round(geodesic(pointA,pointB).km, 2)

        # folium map modification
        m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat,l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'], icon=folium.Icon(color='red')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination, icon=folium.Icon(color='purple', icon='cloud')).add_to(m)

        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
        m.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()

    context ={
        'distance' : distance,
        'destination': destination,
        'form':form,
        'map':m,
    }

    return render(request,'measurements/main.html', context)
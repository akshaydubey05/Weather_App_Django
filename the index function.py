from django.shortcuts import render
import requests
import datetime

def index(request):
    api_key = 'bffc71b55fbb6752e3bb54df5c1cc7f6'
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'

    if request.method == 'POST':
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url,forecast_url)
        else:
            weather_data2, daily_forecasts2 = None, None

        context = {
            'weather_data1': weather_data1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'daily_forecasts2': daily_forecasts2,
        }

        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    current_weather_response = requests.get(current_weather_url.format(city, api_key))

    if current_weather_response.status_code != 200:
        # Handle error in the current weather response
        print(f"Error in current weather API request. Status code: {current_weather_response.status_code}")
        return None, []

    response = current_weather_response.json()

    lat, lon = response['coord']['lat'], response['coord']['lon']

    forecast_response = requests.get(forecast_url.format(lat, lon, api_key))

    if forecast_response.status_code != 200:
        # Handle error in the forecast response
        print(f"Error in forecast API request. Status code: {forecast_response.status_code}")
        return None, []

    forecast_response = forecast_response.json()

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    daily_forecasts = []
    
    # Check if 'daily' key is present in the forecast response
    if 'daily' in forecast_response:
        for daily_data in forecast_response['daily'][:5]:
            daily_forecasts.append({
                'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
                'min_temp': round(daily_data['temp']['min'] - 273.15, 2),
                'max_temp': round(daily_data['temp']['max'] - 273.15, 2),
                'description': daily_data['weather'][0]['description'],
                'icon': daily_data['weather'][0]['icon'],
            })
    else:
        # Handle the case where 'daily' key is not present in the forecast response
        print(f"Error: {forecast_response['message']}")

    return weather_data, daily_forecasts

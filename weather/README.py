# __Getting a wind forecast anywhere from lat,lon__
#
# Selected provider: openweathermap  
# https://home.openweathermap.org
#
# # TODO
# - change python requests for qGIS requests
# - 'ddos prevention' check for recently download data instead of requesting every time
#
# # credentials
# ## account
# Get your free account for forecast5 api at:  
# https://home.openweathermap.org/users/sign_in  
# OneCall api is better but needs a credit card 
#
# ## api key
# Then go to https://home.openweathermap.org/api_keys to get your api key, that will look like this:  
# b972f4e533854e860838ab3e0f967d19
#
# ### General apis reference
# https://stackoverflow.com/questions/51429617/http-requests-body-vs-param-vs-headers-vs-data
#
# # Selected APIs
# ## 1. onecall api 1hr
# 1000 a day free after registering __MY__ credit card  
#
# -  Current weather
# -  Minute forecast for 1 hour
# -  Hourly forecast for 48 hours !!!
# -  Daily forecast for 8 days
# -  National weather alerts
# -  Historical weather data for 40+ years back (since January 1, 1979) Use datetime!
#
# https://openweathermap.org/api/one-call-3  
# https://api.openweathermap.org/data/3.0/onecall?lat=-33.456&lon=-70.695&exclude=minutely,daily,alerts&appid=b972f4e533854e860838ab3e0f967d19  
#
# ## 2. forecast5 (days) every 3 hours
# 5 day forecast is available at any location on the globe. It includes weather forecast data with 3-hour step.  
# Available without credit card!  
# https://openweathermap.org/forecast5  
# https://api.openweathermap.org/data/2.5/forecast?lat=-33.456&lon=-70.695&appid=b972f4e533854e860838ab3e0f967d19  
#
# ## 3. statistics-api
# Not available  
# https://openweathermap.org/api/statistics-api  
# https://history.openweathermap.org/data/2.5/aggregated/month?month=1,6&lat=-33.456&lon=-70.695&appid=b972f4e533854e860838ab3e0f967d19  
#
# ## 4. Hourly forecast
# Not available  
# https://openweathermap.org/api/hourly-forecast  
# https://pro.openweathermap.org/data/2.5/forecast/hourly?lat=-33.456&lon=-70.695&appid=b972f4e533854e860838ab3e0f967d19  
#
# ## some api options
# COMMON  
# - &units=standard, metric, imperial units are available. default: standard 
# ONECALL (2d1h)  
# - &exclude=minutely,current, minutely, hourly, daily, alerts 
# - &history=datetime from January 1st, 1979
# FORECAST (5d3h)   
# - &cnt=int : limit number of timestamp responses  

_APIKEY="b972f4e533854e860838ab3e0f967d19"
import requests, json, csv, datetime, os
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# TODO : stop user from spam clicking & DDOS the API & my credit card
#        a.if requests are less than 1hr apart, just use the pickled json latest response
#        b.make user put their own apikey (1->3h forecast)
import pickle
def doPickle( obj, file_name='save.p', path=os.getcwd()):
    pickle.dump( obj,   open( os.path.join(path,file_name), 'wb' ) )
def unPickle( file_name='save.p', path=os.getcwd()):
    return pickle.load( open( os.path.join(path,file_name), 'rb' ) )


def getForecast2d1h(lat=-33.456, lon=-70.695, appid=_APIKEY):
    '''
    https://api.openweathermap.org/data/3.0/onecall
    '''
    params = {"lat":lat, "lon":lon, "appid":appid, 'exclude':'minutely,daily,alerts'}
    response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall", params=params)
    if response.status_code==200:
        print('request ok!')
        return response.json()
    else:
        print('http response code not ok:',response.status_code)


def getForecast5d3h(lat=-33.456, lon=-70.695, cnt=-1, appid=_APIKEY):
    '''
    https://api.openweathermap.org/data/2.5/forecast
    cnt : limit number of timestamps

    rj = getForecast5()
    rj.keys()
    >>> dict_keys(['cod', 'message', 'cnt', 'list', 'city'])

    assert response.json() == json.loads(response.content.decode('utf-8'))
    >>> True

    print(type(response.json()))
    >>> json

    print(response.json())
    '''
    if cnt==-1:
        params = {"lat":lat, "lon":lon, "appid":appid }
    else:
        params = {"lat":lat, "lon":lon, "appid":appid, "cnt":cnt }
    response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast", params=params)
    if response.status_code==200:
        print('request ok!')
        return response.json()
    else:
        print('http response code not ok:',response.status_code)


def Forecast5d3htoWindDf( rj : json):
    '''
    WARNING: Wind speed in m/s converted to km/h
    rj['list'][0]['wind']
    >>> {'speed': 2.23, 'deg': 245, 'gust': 2.06}

    - datetime is converted by the csv writer
    import datetime
    datetime.datetime.fromtimestamp(rj['list'][0]['dt'])
    >>> datetime.datetime(2023, 1, 11, 12, 0)

    $ head Weather.csv
    Instance,datetime,WS,WD,FireScenario
    Jaime,2001-10-16 13:00,10,0,2
    '''
    data = [[datetime.datetime.fromtimestamp(f['dt']), 
             round(f['wind']['speed']*3.6, 2), 
             round(f['wind']['gust' ]*3.6, 2), 
                   f['wind']['deg']            ] for f in rj['list'] ]
    df = DataFrame( data, columns=['dt','speed','gust','dir'])
    return df


def Forecast2d1htoWindDf( rj : json):
    '''
    WARNING: Wind speed in m/s converted to km/h
    rj['list'][0]['wind']
    >>> {'speed': 2.23, 'deg': 245, 'gust': 2.06}

    - datetime is converted by the csv writer
    import datetime
    datetime.datetime.fromtimestamp(rj['hourly'][0]['dt'])
    >>> datetime.datetime(2023, 1, 11, 12, 0)

    $ head Weather.csv
    Instance,datetime,WS,WD,FireScenario
    Jaime,2001-10-16 13:00,10,0,2
    '''
    data = [[datetime.datetime.fromtimestamp(f['dt']), 
             round(f['wind_speed']*3.6, 2), 
             round(f['wind_gust' ]*3.6, 2), 
                   f['wind_deg']            ] for f in rj['hourly'] ]
    df = DataFrame( data, columns=['dt','speed','gust','dir'])
    return df


def writeWeatherCSV( df, instance_name='instance_name', fireScenario=2, file_name='Weather.csv', path=os.getcwd()):
    df2 = df.drop('gust', axis=1)
    df2.insert(0,'Instance',[instance_name for i in range(len(df))])
    df2 = df2.assign(FireScenario=lambda x:fireScenario)
    df2.to_csv(os.path.join(path,file_name), header=['Instance','datetime','WS','WD','FireScenario'], index=False)


def plot( df : DataFrame, save_png=True, show_plt=True, file_name='wind_forecast.png', path=os.getcwd()):
    '''
    Plot a time series with the windgusts as line and wind speed & direction as quiver arrows
    returns fig,ax
    '''
    U = np.cos(np.radians(df['dir']))
    V = np.sin(np.radians(df['dir']))
    fig, ax = plt.subplots()
    ax.plot(df['dt'], df['gust'], 'r-', label='Gusts')
    ax.quiver(df['dt'], df['speed'], U, V, label='Winds')
    ax.legend()
    if save_png:
        plt.savefig(os.path.join(path,file_name))
    if show_plt:
        plt.show(block=False)
        plt.clf()
    return fig,ax


def main():
    print('hello world!\ndemonstrating the use of openweather.org Forecast & OneCall API to generate Cell2Fire Weather.csv input file')
    # forecast
    forecastJSON = getForecast5d3h(lat=-33.456, lon=-70.695, cnt=10)
    print('5d3h got json response')
    dff = Forecast5d3htoWindDf(forecastJSON )
    print('5d3h parsed to list')
    writeWeatherCSV(dff, file_name='Weather5d3h.csv')
    print('wrote the file Weather.csv on current working directory')
    plot(dff, file_name='wind_forecast5d3h.png')
    doPickle( forecastJSON, file_name='forecast.p')
    # onecall
    onecallJSON = getForecast2d1h(lat=-33.456, lon=-70.695)
    print('2d1h got json response')
    dfo = Forecast2d1htoWindDf(onecallJSON )
    print('2d1h parsed to list')
    writeWeatherCSV(dfo, file_name='Weather2d1h.csv')
    print('wrote the file Weather.csv on current working directory')
    plot(dfo, file_name='wind_forecast2d1h.png')
    doPickle( onecallJSON , file_name='onecall.p')

    print('get your own api key! on openweather.org\nbye world!')


if __name__ == '__main__':
    main()
    '''
    return [   (Instance,
                datetime.datetime.fromtimestamp(f['dt']), 
                round(f['wind']['speed']*3.6, 2), 
                f['wind']['deg'],
                FireScenario)               for f in rj['list'] ]
    with open(os.path.join(path,file_name), 'w') as csvfile:
    with open(file_name, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Instance,datetime,WS,WD,FireScenario'])
        csvwriter.writerows(weather)
    '''

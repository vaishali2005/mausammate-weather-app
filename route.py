from flask import Flask, render_template, url_for, request, redirect
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import pycountry

load_dotenv()
app = Flask(__name__)


app.secret_key = os.getenv("SECRET_KEY")
API_KEY = os.getenv("WEATHER_API_KEY")


#Current weather data
def fetch_wether_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

#Forecast Weather data
def fetch_forecast_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

@app.route("/", methods=["GET", "POST"])
def dashboard():
    weather_data = None
    # forecast_weather = None
    today = datetime.now()
    time = today.strftime("%I:%M %p")
    day = today.strftime("%A")
    try:
        if request.method == "POST":
            city = request.form.get("city")
            # data = fetch_wether_data(city)
            # forcaste_data = fetch_forcast_weather(city)
        else:
            city = "Delhi" 
        data= fetch_wether_data(city)
            # forcaste_data = fetch_forcast_weather("Delhi")
        # print(forcaste_data)    
        if str(data.get("cod")) == "200":
            sunrise_time =  datetime.fromtimestamp(data["sys"]["sunrise"])
            time_diffr = today - sunrise_time
            icon_code = data["weather"][0]["icon"]
            weather_data = {
                "city": data["name"],
                "country" : pycountry.countries.get(alpha_2=(data["sys"]["country"])).name,
                "day": day,
                "current_time": time,
                "temp": round(data["main"]["temp"]),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime(
                    "%I:%M %p"
                ),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime(
                    "%I:%M %p"),
                "time_since_sunrise" : f"{time_diffr.seconds//3600}h {(time_diffr.seconds % 3600) // 60}m",
                "current_weather" : data["weather"][0]["description"],
                "icon" :f"http://openweathermap.org/img/wn/{icon_code}@2x.png",
                "humidity" : data["main"]["humidity"],
                "wind" : data["wind"]["speed"],
                "feels_like" : data["main"]["feels_like"],
                "temp_min" : round(data["main"]["temp_min"]),
                "temp_max" : round(data["main"]["temp_max"]),
                "clouds" : data["clouds"]["all"],
                "visibility" : data["visibility"] / 1000,
                "wind_dir" : data["wind"]["deg"],
                "pressure" : data["main"]["pressure"]
            }
        else:
            weather_data = {"error": "City Not Found"}
            
        #Forecast Section 
        forecast_data = fetch_forecast_weather(city)
        forecast_weather = []
        flag = None
        if str(forecast_data.get("cod")) == "200":
            for i in  forecast_data["list"]:
                dt_txt = datetime.strptime(i["dt_txt"], "%Y-%m-%d %H:%M:%S")
                dt_date = dt_txt.date()
                dt_time = dt_txt.time().hour
                dt_day = dt_txt.strftime("%A")
                dt = dt_date
                
                if dt_date > today.date():
                    if flag != dt:
                        if dt_time == 12 or dt_time == 15:
                            
                            icon_code = i["weather"][0]["icon"]
                            day ={
                                "temp": round(i["main"]["temp"]),
                                "description" : i["weather"][0]["description"],
                                "icon" :f"http://openweathermap.org/img/wn/{icon_code}@2x.png",
                                "day" : dt_day
                            }
                            # print(dt_day)
                            forecast_weather.append(day)
                            flag = dt_date  
    except Exception as e:
        print(e)
    return render_template("dashboard.html", weather=weather_data, forecast = forecast_weather)


if __name__ == "__main__":
    app.run()

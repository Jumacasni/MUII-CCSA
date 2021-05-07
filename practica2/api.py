from flask import Flask, Response
from datetime import datetime, timedelta
from fbprophet import Prophet
import pmdarima as pm
import pickle

app = Flask(__name__)

# Cargar modelo de predicción de temperatura de ARIMA
with open('v1/model_temperature.pkl', 'rb') as file_temperature:
	model_temperature_v1 = pickle.load(file_temperature)

# Cargar modelo de predicción de humedad de ARIMA
with open('v1/model_humidity.pkl', 'rb') as file_humidity:
	model_humidity_v1 = pickle.load(file_humidity)

# Cargar modelo de predicción de temperatura de Prophet
with open('v2/model_temperature.pkl', 'rb') as file_temperature:
	model_temperature_v2 = pickle.load(file_temperature)

# Cargar modelo de predicción de humedad de Prophet
with open('v2/model_humidity.pkl', 'rb') as file_humidity:
	model_humidity_v2 = pickle.load(file_humidity)


def get_prediction_v1(periods):
	""" Predecir temperatura y humedad con ARIMA y devolver resultados en formato JSON """

	fc_temperature = model_temperature_v1.predict(n_periods=periods, return_conf_int=True)

	fc_humidity = model_humidity_v1.predict(n_periods=periods, return_conf_int=True)

	return to_json(periods, fc_temperature, fc_humidity)


def get_prediction_v2(periods):
	""" Predecir temperatura y humedad con Prophet y devolver resultados en formato JSON """

	future_temperature = model_temperature_v2.make_future_dataframe(periods=periods, freq="h")
	prophet_pred_temperature = model_temperature_v2.predict(future_temperature)
	prophet_pred_temperature = [prophet_pred_temperature[-periods:]["yhat"].array,prophet_pred_temperature[-periods:]['ds'].array]

	future_humidity = model_humidity_v2.make_future_dataframe(periods=periods, freq="h")
	prophet_pred_humidity = model_humidity_v2.predict(future_humidity)
	prophet_pred_humidity = [prophet_pred_humidity[-periods:]["yhat"].array,prophet_pred_humidity[-periods:]['ds'].array]
	
	return to_json(periods, prophet_pred_temperature, prophet_pred_humidity)

def daterange(n_hours):
	""" Genera el rango de horas de las próximas n_hours a partir de la hora actual"""

	start = datetime.today().replace(minute=0, second=0, microsecond=0)

	delta = timedelta(hours=1)
	date_list = []

	for i in range(n_hours):
		date_str = ':'.join(str(start).split(':')[:2])
		date_list.append(date_str)
		start += delta

	return date_list


def to_json(periods, temp, hum):
	""" Convertir los resultados a formato JSON siguiendo la estructura indicada en el guión de prácticas """

	date_list = daterange(periods)

	res = "{\n"
	for index, date in enumerate(date_list):
		res += '{"hour":'+date+',"temp":'+str(temp[0][index])+',"hum":'+str(hum[0][index])+'}'
		
		if index != (len(date_list)-1):
			res += ",\n"

	return res


@app.route("/")
def index():
	return Response("Microservicio funcionando", status=200)


@app.route("/servicio/v1/prediccion/<string:horas>", methods=['GET'])
def obtener_prediccion_v1(horas):
	if horas == "24horas" or horas == "48horas" or horas == "72horas":
		hora = horas[:2]
		
		pred = get_prediction_v1(int(hora))

		return Response(response=pred,
				status=200,
				mimetype='application/json')

	return Response("Error en la consulta", status=400)


@app.route("/servicio/v2/prediccion/<string:horas>", methods=['GET'])
def obtener_prediccion_v2(horas):
	if horas == "24horas" or horas == "48horas" or horas == "72horas":
		hora = horas[:2]
		
		pred = get_prediction_v2(int(hora))

		return Response(response=pred,
				status=200,
				mimetype='application/json')

	return Response("Error en la consulta", status=400)

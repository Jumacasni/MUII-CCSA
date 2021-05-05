from flask import Flask, Response
from datetime import datetime, timedelta
import pmdarima as pm
import pickle
import json

app = Flask(__name__)

with open('model_temperature.pkl', 'rb') as file_temperature:
	model_temperature = pickle.load(file_temperature)

with open('model_humidity.pkl', 'rb') as file_humidity:
	model_humidity = pickle.load(file_humidity)

def get_prediction(periods):
	fc_temperature = model_temperature.predict(n_periods=periods, return_conf_int=True)

	fc_humidity = model_humidity.predict(n_periods=periods, return_conf_int=True)

	return to_json(periods, fc_temperature, fc_humidity)


def daterange(n_hours):
	start = datetime.today().replace(minute=0, second=0, microsecond=0)

	delta = timedelta(hours=1)
	date_list = []

	for i in range(n_hours):
		date_str = ':'.join(str(start).split(':')[:2])
		date_list.append(date_str)
		start += delta

	return date_list


def to_json(periods, temp, hum):
	date_list = daterange(periods)
	data_dict = dict()

	for index, date in enumerate(date_list):
		data_dict[date] = {"temperature": temp[0][index],"humidity": hum[0][index]}
	
	return json.dumps(data_dict, indent=4)


@app.route("/")
def index():
	return Response("Microservicio funcionando", status=200)


@app.route("/servicio/v1/prediccion/<string:horas>", methods=['GET'])
def obtener_prediccion(horas):
	if horas == "24horas" or horas == "48horas" or horas == "72horas":
		hora = horas[:2]
		
		pred = get_prediction(int(hora))

		return Response(response=pred,
										status=200,
										mimetype='application/json')

	return Response("Error en la consulta", status=400)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8000)
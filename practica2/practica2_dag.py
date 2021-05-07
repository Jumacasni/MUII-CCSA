from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from pymongo import MongoClient
from zipfile import ZipFile
from datetime import datetime, timedelta
from statsmodels.tsa.arima_model import ARIMA
from fbprophet import Prophet
import os
import pandas as pd
import pickle
import pmdarima as pm
import json

###################
# PYTHON CALLABLE #
###################

def capture_data():
	""" Descomprimir los datos y obtener sólo las columnas DATE y SAN FRANCISCO
			Unificar los datos en un mismo archivo forecast.csv con la estructura DATE;TEMP;HUM
	"""

	with ZipFile('/tmp/humidity.csv.zip', 'r') as file:
		file.extractall('/tmp/')

	with ZipFile('/tmp/temperature.csv.zip', 'r') as file:
		file.extractall('/tmp/')

	df_humidity = pd.read_csv('/tmp/humidity.csv',
									usecols=['datetime','San Francisco'])

	df_temperature = pd.read_csv('/tmp/temperature.csv',
										usecols=['San Francisco'])

	data = [df_humidity['datetime'], df_temperature['San Francisco'], df_humidity['San Francisco']]
	headers = ['DATE', 'TEMP', 'HUM']

	# Unir datos y eliminar las filas que contengan NaN
	df = pd.concat(data, axis=1, keys=headers).dropna()

	df.to_csv("/tmp/forecast.csv")


def store_data():
	""" Almacenar los datos en MongoDB """

	df = pd.read_csv('/tmp/forecast.csv')

	client = MongoClient('0.0.0.0', port=27017)

	db = client["forecast"]
	collection = db["sanfrancisco"]

	data_dict = df.to_dict(orient='records')
	collection.insert_many(data_dict)


def models_arima():
	""" Creación del modelo de predicción con ARIMA para la humedad y temperatura
			Se guarda el modelo en un archivo .pkl para su posterior uso en la predicción
			Versión 1 de la API
	""" 

	client = MongoClient('0.0.0.0', port=27017)
	db = client["forecast"]
	collection = db["sanfrancisco"]
	df_humidity = pd.DataFrame(list(collection.find()))['HUM']
	df_temperature = pd.DataFrame(list(collection.find()))['TEMP']

	model_temperature = pm.auto_arima(df_temperature, start_p=1, start_q=1,
											test='adf',       # use adftest to find optimal 'd'
											max_p=3, max_q=3, # maximum p and q
											m=1,              # frequency of series
											d=None,           # let model determine 'd'
											seasonal=False,   # No Seasonality
											start_P=0, 
											D=0, 
											trace=True,
											error_action='ignore',  
											suppress_warnings=True, 
											stepwise=True)

	model_humidity = pm.auto_arima(df_humidity, start_p=1, start_q=1,
											test='adf',       # use adftest to find optimal 'd'
											max_p=3, max_q=3, # maximum p and q
											m=1,              # frequency of series
											d=None,           # let model determine 'd'
											seasonal=False,   # No Seasonality
											start_P=0, 
											D=0, 
											trace=True,
											error_action='ignore',  
											suppress_warnings=True, 
											stepwise=True)

	if not os.path.exists('/tmp/practica2'):
		os.mkdir('/tmp/practica2')

	if not os.path.exists('/tmp/practica2/v1'):
		os.mkdir('/tmp/practica2/v1')

	file_model_temperature = '/tmp/practica2/v1/model_temperature.pkl'
	file_model_humidity = '/tmp/practica2/v1/model_humidity.pkl'

	with open(file_model_temperature, 'wb') as file:
		pickle.dump(model_temperature, file)

	with open(file_model_humidity, 'wb') as file:
		pickle.dump(model_humidity, file)

def models_prophet():
	""" Creación del modelo de predicción con Prophet para la humedad y temperatura
			Se guarda el modelo en un archivo .pkl para su posterior uso en la predicción
			Versión 2 de la API
	""" 

	client = MongoClient('0.0.0.0', port=27017)
	db = client["forecast"]
	collection = db["sanfrancisco"]
	df_date = pd.DataFrame(list(collection.find()))['DATE']
	df_humidity = pd.DataFrame(list(collection.find()))['HUM']
	df_temperature = pd.DataFrame(list(collection.find()))['TEMP']

	data_temperature = [df_date, df_temperature]
	headers_temperature = ['ds', 'y']
	df_temperature = pd.concat(data_temperature, axis=1, keys=headers_temperature)

	model_temperature = Prophet()
	model_temperature.fit(df_temperature)

	data_humidity = [df_date, df_humidity]
	headers_humidity = ['ds', 'y']
	df_humidity = pd.concat(data_humidity, axis=1, keys=headers_humidity)

	model_humidity = Prophet()
	model_humidity.fit(df_humidity)

	if not os.path.exists('/tmp/practica2'):
		os.mkdir('/tmp/practica2')

	if not os.path.exists('/tmp/practica2/v2'):
		os.mkdir('/tmp/practica2/v2')

	file_model_temperature = '/tmp/practica2/v2/model_temperature.pkl'
	file_model_humidity = '/tmp/practica2/v2/model_humidity.pkl'

	with open(file_model_temperature, 'wb') as file:
		pickle.dump(model_temperature, file)

	with open(file_model_humidity, 'wb') as file:
		pickle.dump(model_humidity, file)
	
############
# INIT DAG #
############
default_args = {
	'owner': 'Juan Manuel Castillo Nievas',
	'depends_on_past': False,
	'start_date': days_ago(2),
	'email': ['jumacasni@correo.ugr.es'],
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retry_delay': timedelta(minutes=5),
	# 'queue': 'bash_queue',
	# 'pool': 'backfill',
	# 'priority_weight': 10,
	# 'end_date': datetime(2016, 1, 1),
	# 'wait_for_downstream': False,
	# 'dag': dag,
	# 'sla': timedelta(hours=2),
	# 'execution_timeout': timedelta(seconds=300),
	# 'on_failure_callback': some_function,
	# 'on_success_callback': some_other_function,
	# 'on_retry_callback': another_function,
	# 'sla_miss_callback': yet_another_function,
	# 'trigger_rule': 'all_success'
}

dag = DAG(
	'practica2',
	default_args=default_args,
	description='Forecast DAG',
	schedule_interval='@once',
)

#########
# TASKS #
#########

InitMongoDB = BashOperator(
	task_id='init_mongodb',
	bash_command='docker run -d --rm -p 27017:27017 --name mongodb mongo:latest',
	dag=dag,
)

GetHumidity = BashOperator(
	task_id='get_humidity',
	depends_on_past=True,
	bash_command='curl -o /tmp/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
	dag=dag,
)

GetTemperature = BashOperator(
	task_id='get_temperature',
	depends_on_past=True,
	bash_command='curl -o /tmp/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
	dag=dag,
)

CaptureData = PythonOperator(
	task_id='capture_data',
	depends_on_past=True,
	python_callable=capture_data,
	dag=dag
)

StoreData = PythonOperator(
	task_id='store_data',
	depends_on_past=True,
	python_callable=store_data,
	dag=dag
)

PredictionModelV1 = PythonOperator(
	task_id='prediction_model_v1',
	depends_on_past=True,
	python_callable=models_arima,
	dag=dag
)

PredictionModelV2 = PythonOperator(
	task_id='prediction_model_v2',
	depends_on_past=True,
	python_callable=models_prophet,
	dag=dag
)

GitClone = BashOperator(
	task_id='git_clone',
	depends_on_past=True,
	bash_command='cd /tmp/practica2 && git clone https://github.com/Jumacasni/MUII-CCSA.git && mv MUII-CCSA/practica2/* .',
	dag=dag,
)

UnitTest = BashOperator(
	task_id='unit_test',
	depends_on_past=True,
	bash_command='cd /tmp/practica2 && python3 tests.py',
	dag=dag,
)

Build = BashOperator(
	task_id='build',
	depends_on_past=True,
	bash_command='cd /tmp/practica2 && docker build --rm -t api .',
	dag=dag,
)

Deploy = BashOperator(
	task_id='deploy',
	depends_on_past=True,
	bash_command='docker run --rm --name api -p 8000:8000 api',
	dag=dag,
)

#######
# DAG #
#######

InitMongoDB >> [GetHumidity, GetTemperature] >> CaptureData >> StoreData >> [PredictionModelV1, PredictionModelV2] >> GitClone >> UnitTest >> Build >> Deploy

import unittest
import api_v1

app = api_v1.app.test_client()

class TestAPIV1(unittest.TestCase):
	def test_root(self):
		response = app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data.decode('UTF-8'), "Microservicio funcionando")

	def test_bad_request(self):
		response = app.get('servicio/v1/prediccion/error')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.data.decode('UTF-8'), "Error en la consulta")

	def test_good_request_24horas(self):
		response = app.get('servicio/v1/prediccion/24horas')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content_type, "application/json")

	def test_good_request_48horas(self):
		response = app.get('servicio/v1/prediccion/48horas')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content_type, "application/json")

	def test_good_request_72horas(self):
		response = app.get('servicio/v1/prediccion/72horas')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content_type, "application/json")

if __name__ == "__main__":
	unittest.main() 
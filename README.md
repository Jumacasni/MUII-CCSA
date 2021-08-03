# MUII-CCSA
Asignatura de Cloud Computing: Servicios y Aplicaciones (CCSA) - Máster Profesional en Ingeniería Informática 2020/2021

<details open="open">
  <summary>Tabla de contenidos</summary>
  <ol>
    <li>
      <a href="#practica1">Práctica 1: Despliegue de servicio de almacenamiento en contenedores</a>
    </li>
    <li>
      <a href="#practica2">Práctica 2: Airflow</a>
    </li>
    <li>
      <a href="#practica3">Práctica 3: MongoDB</a>
    </li>
    <li>
      <a href="#practica4">Práctica 4: Spark</a>
    </li>
  </ol>
      
<a name="practica1"></a>
## Práctica 1: Despliegue de servicio de almacenamiento en contenedores

La práctica consiste en desplegar un servicio **Nextcloud** junto con **nginx** para el balanceo de carga.

El archivo [Makefile](practica1/Makefile) proporciona una ejecución más sencilla de la práctica. Usando ```make up``` y ```make down``` se pueden desplegar y detener los contenedores, respectivamente.

Una vez desplegados, es necesario hacer ```sh configuration.sh``` antes de entrar en la URL para que Nextcloud confíe en el dominio de nginx.

<a name="practica2"></a>
## Práctica 2: Airflow

El objetivo de esta práctica es llevar a cabo un despliegue completo de un servicio **Cloud Native**. Se ha desarrollado un sistema de predicción de temperature y humedad y se debe desplegar un servicio que proporcione una API RESTful con las predicciones. La API consta de 2 versiones y en cada versión se ha utilizado un modelo de predicción distinto. Los endpoints son los siguientes:

* **/servicio/v1/prediccion/24horas**
* **/servicio/v1/prediccion/48horas**
* **/servicio/v1/prediccion/72horas**
* **/servicio/v2/prediccion/24horas**
* **/servicio/v2/prediccion/48horas**
* **/servicio/v2/prediccion/72horas**

Toda la documentación y explicación del proceso llevado a cabo en esta práctica se encuentra [aquí](practica2/P2_JuanManuelCastilloNievas.pdf)

<a name="practica3"></a>
## Práctica 3: MongoDB

A partir de los datos recopilados en [SacramentocrimeJanuary2006.csv](practica3/SacramentocrimeJanuary2006.csv), se piden realizar dos consultas en MongoDB:

* Totalizar el número de delitos por cada tipo
* Franjas horarias con más números de delitos

Estas consultas se pueden consultar en la documentación hecha [aquí](practica3/P3_JuanManuelCastilloNievas.pdf)

<a name="practica4"></a>
## Práctica 4: Spark

El objetivo de esta práctica es usar la plataforma **Spark** para poner en uso diferentes métodos y técnicas de preprocesamiento. Para ello, se ha utilizado la biblioteca **MLLib**. Se han usado las siguientes técnicas:

* Random Forest
* Decision Trees
* Gradient Boosted Trees

Toda la documentación y explicación del proceso llevado a cabo en esta práctica se encuentra [aquí](practica4/P4_JuanManuelCastilloNievas.pdf)
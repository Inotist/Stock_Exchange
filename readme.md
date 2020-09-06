# Proyecto Stock Exchange Predictions
&nbsp;
![#f03c15](https://placehold.it/15/f03c15/000000?text=+) <span style="color:red">Se mostrará en rojo aquellas ideas que no se han implementado por falta de tiempo.</span>

##### [Enlace para visualizar la App](https://stock-exchange-predictions.ew.r.appspot.com/IBM)

## Idea general
Crear una aplicación web mediante la que se puedan visualizar diferentes estimaciones sobre el crecimiento de las acciones de diferentes empresas en el mercado de NASDAQ.

## Nombre del producto
Stock Exchange Predictions

## Estrategia del DAaaS
Utilizaré la API de Alpha Vantage para extraer los datos diarios de las transacciones en forma de serie temporal y también los informes trimestrales, y con Google Cloud Functions se generarán nuevas predicciones en base a los datos extraídos. Esta información se actualiza diaria y trimestralmente.

![#f03c15](https://placehold.it/15/f03c15/000000?text=+) <span style="color:red">También cada día se extraerán las últimas noticias y una red LSTM se encargará de predecir si el crecimiento que se prevee en base a estas noticias será positivo o negativo.</span>

La intención es conseguir una arquitectura que sea capaz de mantener por sí misma la disponibilidad de los datos actualizados, que sea fácilmente escalable y que al menos en un principio sea gratuita.

## Arquitectura
Arquitectura Cloud basada Google Cloud Functions, Google Cloud Storage, y Google App Engine.

![#f03c15](https://placehold.it/15/f03c15/000000?text=+) <span style="color:red">Crawler con scrapy desplegado en una Cloud Function que extrae las últimas noticias de la web oficial de NASDAQ</span>

Segmento de Google Cloud donde se almacenarán de forma estructurada todos los datos necesarios para el funcionamiento de la App:

- Los archivos que incluyen información acerca de la arquitectura, los hiperparámetros y los pesos de los modelos se generan en local y se suben a mano.
- Los datos respectivos a series temporales e informes trimestrales se obtienen por medio de Cloud Functions que conectan con la API de Alpha Vantage y se almacenan en el segmento por medio de la App desplegada en App Engine.
- Los datos de las predicciones se generan por medio de Cloud Functions y se almacenan en el segmento por medio de la App desplegada en App Engine.

Las Cloud Functions se ejecutan a petición de la App desde App Engine cuando ésta detecta que los datos almacenados en el segmento están desactualizados.

## Operating Model
El modelo que realiza las predicciones trimestrales puede usarse indistintamente para todo el mercado de NASDAQ. Sin embargo, las predicciones semanales utilizan un modelo que es entrenado específicamente para cada una de las empresas disponibles:

- Entrenar diferentes modelos para cada una de las empresas del mercado, subirlos al proyecto e incluir dichas empresas en el listado de índices disponibles en la App.
- Reentrenar en local los modelos disponibles cada cierto tiempo considerable o cuando se considere oportuno y actualizar los datos del segmento si los resultados son mejores que los del modelo en producción.

## [Diagrama](https://docs.google.com/drawings/d/1W_Ztst7hCrN_vDeb-7FDiigbrX8TsU-ExqKruTUYS7M)

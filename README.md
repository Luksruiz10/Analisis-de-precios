# Análisis de Precios en Supermercados - Proyecto de Ciencia de Datos

# Descripcion
Este proyecto analiza los precios de productos en un supermercado reconocido de España a lo largo del tiempo, permitiendo estudiar la inflación diaria, identificar tendencias y destacar las mayores variaciones de precio. Los datos se obtienen mediante scraping diario, se almacenan en una base de datos SQLite y se visualizan con Streamlit y Plotly, ademas de publicar datos diariamente en X.

## Características
- Registro diario de precios de productos y categorías.
- Cálculo automático de la inflación diaria en la canasta básica, comparación de la misma contra la inflación.
- Identificación de productos con mayor variación de precios.
- Envió automático de ofertas vía correo electrónico
- Comparaciones de precios entre fechas específicas.
- Visualizaciones interactivas de datos usando Plotly y Streamlit.
- Predicción básica de precios futuros

## Tecnologías Utilizadas
Lenguaje: Python 3.12
Bases de Datos: SQLite
Bibliotecas: pandas, plotly, streamlit, sqlite3, statsmodels, prophet

## Futuras Mejoras
- Integrar más fuentes de datos para comparar precios entre supermercados.
- Mejorar la predicción de precios futuros con Prophet.
- Añadir reportes anualizados
- Graficos semanales automatizados en X

## Accede a mi trabajo
Puedes probar la aplicación accediendo a este enlace:
https://analysis-de-precios.streamlit.app/

Red social X con actualizaciones diarias de la canasta basica:
https://x.com/MercaDBot
Desde allí, podrás explorar gráficos, buscar productos y analizar precios sin necesidad de instalación.

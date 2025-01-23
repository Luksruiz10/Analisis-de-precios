import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import plotly.express as px

def precio_ofertas():
    #fecha_actual = datetime.now().strftime("%Y-%m-%d")
    fecha_actual = '2025-01-06'
    conn = sqlite3.connect('Mercadona.db')
    cursor = conn.cursor()

    query = f'''
        SELECT * FROM Principal
        WHERE Fecha = '{fecha_actual}'
    '''
    df = pd.read_sql_query(query, conn)
    producto_seleccionado = st.selectbox('Selecciona uno o más productos', df['Nombre'])

    query = f'''
        SELECT * FROM Principal
        WHERE Nombre = '{producto_seleccionado}'
    '''
    df_producto = pd.read_sql_query(query, conn)
    df_producto.sort_values('Fecha', inplace=True)

    st.markdown(f"""El producto seleccionado es:   
    **{producto_seleccionado}**  \nPrecio actual: **${df_producto['Precio'].iloc[-1]}**  
    Esta en oferta: {'Si' if df_producto['Oferta'].iloc[-1] == 1 else 'No'}""")

#Grafico

    fig = px.line(df_producto, x='Fecha', y='Precio', title=f'Variacion de precio de {producto_seleccionado}')
    st.plotly_chart(fig)
    
    conn = sqlite3.connect('Mercadona.db')
    cursor = conn.cursor()

    # Interfaz de Streamlit
    st.write('¿Quieres que te avisemos cuando haya alguna oferta?')
    email = st.text_input('Introduce tu email', max_chars=50, placeholder='Escribe aquí tu email')
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if st.button('Confirmar'):
        if email:  # Verificar si se ingresó un correo
            if not re.match(email_regex, email):
                    st.error("Por favor, ingresa un correo electrónico válido.")
            else:
                try:
                    # Insertar el correo si no existe
                    if not re.match(email_regex, email):
                        st.error("Por favor, ingresa un correo electrónico válido.")
                    
                    cursor.execute("""
                        INSERT INTO Correos (email) VALUES (?);
                    """, (email,))
                    conn.commit()

                    # Obtener el ID del correo
                    cursor.execute("SELECT id FROM Correos WHERE email = ?;", (email,))
                    correo_id = cursor.fetchone()[0]

                    # Relacionar el correo con el producto
                    cursor.execute("""
                        INSERT INTO ProductosSeguidos (correo_id, producto_id) VALUES (?, ?);
                    """, (correo_id, df_producto['Id_Producto'].iloc[-1]))
                    conn.commit()

                    st.success(f"¡Gracias! Te avisaremos a {email} cuando haya alguna oferta.")
                except sqlite3.IntegrityError:
                    st.error("El correo electrónico ya está registrado.")
        #Guardar mail en la base de datos relacionado con el producto seleccionado


    from datetime import date

    # Obtener productos cuyo precio bajó en comparación al precio anterior
    cursor.execute("""
        SELECT p.id, p.Nombre, p.Precio, c.email
        FROM Principal p
        JOIN ProductosSeguidos ps ON p.id = ps.producto_id
        JOIN Correos c ON ps.correo_id = c.id
        WHERE p.Fecha = ? AND p.Precio < (
            SELECT p2.Precio
            FROM Principal p2
            WHERE p2.id = p.id AND p2.Fecha < ?
            ORDER BY p2.Fecha DESC
            LIMIT 1
        );
    """, (date.today(), date.today()))
    productos_a_notificar = cursor.fetchall()


    import smtplib
    from email.message import EmailMessage
    # Usuario y contraseña
    usuario = 'lucasruiz048@gmail.com'
    password= " "
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(usuario, password)

    for producto_id, nombre_producto, precio_actual, email in productos_a_notificar:
        msg = EmailMessage()
        msg['From'] = usuario
        msg['To'] = email
        msg['Subject'] = "¡Bajada de precio!"
        cuerpo_del_mail = f"El producto '{nombre_producto}' ahora cuesta {precio_actual}.\n¡Aprovecha la oferta!"
        msg.set_content(cuerpo_del_mail)

        server.send_message(msg)
        print(f"Correo enviado a {email} sobre el producto {nombre_producto}.")

    server.quit();
        
    conn.close()
    
    
    
    #Predicciones
    
    import statsmodels.api as sm
    from statsmodels.tsa.arima.model import ARIMA
    import plotly.graph_objects as go
    
    df_producto["Fecha"] = pd.to_datetime(df_producto["Fecha"])

    # Crear el modelo
    model = ARIMA(df_producto["Precio"], order=(5, 1, 0))  # Ajusta el orden según los datos
    model_fit = model.fit()

    # Hacer predicciones
    forecast = model_fit.forecast(steps=10)
    forecast_df = pd.DataFrame({
        "Fecha": pd.date_range(start=df_producto["Fecha"].iloc[-1] + pd.Timedelta(days=1), periods=len(forecast), freq="D"),
        "Prediccion": forecast
    })
    
    from prophet import Prophet

    # Crear el DataFrame para Prophet
    # Crear el DataFrame para Prophet
    df_prophet = df_producto[["Fecha", "Precio"]].rename(columns={"Fecha": "ds", "Precio": "y"})

    # Crear y ajustar el modelo
    model = Prophet()
    model.fit(df_prophet)

    # Crear un DataFrame futuro y realizar predicciones
    future = model.make_future_dataframe(periods=10)
    forecast = model.predict(future)

    # Combinar datos reales y predicción para graficar
    df_combined = pd.concat([
        df_prophet.rename(columns={"y": "Precio", "ds": "Fecha"}).assign(Tipo="Datos reales"),
        forecast[["ds", "yhat"]].rename(columns={"yhat": "Precio", "ds": "Fecha"}).assign(Tipo="Predicción")
    ])

    # Crear el gráfico principal con datos reales y predicciones
    fig = px.line(
        df_combined,
        x="Fecha",
        y="Precio",
        color="Tipo",
        title="Predicción de precios con intervalos de confianza"
    )

    # Añadir los intervalos de confianza como áreas sombreadas
    fig.add_traces([
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            mode='lines',
            line=dict(width=0),  # Línea invisible para rellenar
            showlegend=False,
            name="Confianza superior"
        ),
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            mode='lines',
            line=dict(width=0),  # Línea invisible para rellenar
            fill='tonexty',  # Rellena el área entre 'Confianza superior' y 'Confianza inferior'
            fillcolor='rgba(0, 0, 255, 0.2)',  # Color de relleno con transparencia
            showlegend=True,
            name="Intervalo de confianza"
        )
    ])

    # Mostrar el gráfico
    st.plotly_chart(fig)
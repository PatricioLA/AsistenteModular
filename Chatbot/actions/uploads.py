import mysql.connector
import requests
import json
import base64
from rasa_sdk.executor import CollectingDispatcher


def uploadTelegram(dataSet):
    
    db = mysql.connector.connect(
    #    host="LeCuack",
    #    user="rasaserver",
    #    password="Rasa#2023",
    #    database="rasa"
        host='reportes-1.ce41nxatcuur.us-east-1.rds.amazonaws.com',
        user='admin',
        password='Proymodular123.',
        database='Reportes'
        )
    
    if db.is_connected():
        print("Conexión a la base de datos en 000webhost establecida con éxito")

    data = dataSet;
    photo_base64 = data["imagename"]
    photo = base64.b64decode(photo_base64)
    # Crear un cursor para interactuar con la base de datos
    cur = db.cursor()
    try:
        # Ejecutar una consulta SQL para insertar los datos
        cur.execute('INSERT INTO report (firstName, lastName, location_report, image) VALUES(%s, %s, %s, %s)', (data["first_name"], data["last_name"],  data["location_report"], photo))
                    #INSERT INTO usuarios (nombre, email) VALUES (%s, %s)', (data["first_name"], data["email"])')

        # Hacer un commit para guardar los cambios
        db.commit()
        cur.close()
        return True
    except mysql.connector.Error as err:
        # Si hay un error, puedes manejarlo y proporcionar un mensaje de error
        return False
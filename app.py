from flask import Flask, jsonify, request, abort
import os
import psycopg2
import time
import sys

# --- Configuración de la Aplicación ---
app = Flask(__name__)

# Función que maneja la conexión a la base de datos con reintentos
def get_db_connection():
    # Obtiene credenciales de las variables de entorno del contenedor Docker
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')

    # Configuración de reintentos para esperar a que la DB esté lista
    retries = 5
    while retries > 0:
        try:
            # Intenta conectarse a PostgreSQL
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            # Si tiene éxito, devuelve la conexión
            return conn
        except psycopg2.OperationalError as e:
            # Si falla (la DB aún no está lista), espera y reintenta
            retries -= 1
            app.logger.warning(f"Database not ready, retrying... ({retries} attempts left). Error: {e}")
            time.sleep(5)
        except Exception as e:
            # Maneja otros errores de conexión
            app.logger.error(f"Unexpected connection error: {e}")
            # Salida inmediata si es un error no relacionado con la disponibilidad
            sys.exit(1)


    app.logger.error("Could not connect to database after all retries.")
    return None

# --- Endpoints de la API ---

@app.route("/db-health", methods=["GET"])
def db_health_check():
    """
    Endpoint para verificar si la conexión a la base de datos es exitosa.
    """
    conn = get_db_connection()

    if conn is None:
        # Si get_db_connection devuelve None después de los reintentos
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

    try:
        # Si la conexión se estableció, la cerramos y devolvemos éxito
        conn.close()
        return jsonify({"status": "ok", "message": "Database connection successful"})
    except Exception as e:
        # Esto debería ser raro, pero maneja si la conexión falla al cerrar
        return jsonify({"status": "error", "message": f"Connection verification failed: {e}"}), 500


# NOTE: Aquí iría el código de CRUD de la Parte 4/5 para interactuar con la DB.
# Por ahora, solo se incluye el index base.

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Welcome to the News API with DB Check!",
        "endpoints": {
            "health_check": "GET /db-health",
            # Aquí se expandiría con el resto de endpoints CRUD...
        }
    })

if __name__ == "__main__":
    # La aplicación se ejecuta en el puerto 3000 y escucha en todas las interfaces
    app.run(threaded=True, host='0.0.0.0', port=3000)
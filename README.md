
# 📘 Proyecto Flask + Swagger

Este proyecto es una API RESTful construida con Flask y documentada con Swagger. A continuación se detallan los pasos para levantar el entorno y acceder a la documentación interactiva.

---

## 🚀 Requisitos previos

- Python 3.x instalado
- PostgreSQL instalado y con una base de datos creada
- Git (opcional pero recomendado)

---

## 🧪 Paso 1: Crear y activar entorno virtual

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

- En **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- En **Linux o macOS**:
  ```bash
  source venv/bin/activate
  ```

---

## 📦 Paso 2: Instalar dependencias

Instala todas las librerías necesarias:

```bash
pip install -r requirements.txt
```

Si no tienes el archivo `requirements.txt`, puedes generarlo con:

```bash
pip freeze > requirements.txt
```

---

## ⚙️ Paso 3: Configurar la base de datos

Edita el archivo `app/config.py` y coloca tu URL de conexión a la base de datos PostgreSQL:

```python
SQLALCHEMY_DATABASE_URI = "postgresql://usuario:contraseña@localhost:5432/nombre_basedatos"
JWT_SECRET_KEY = "clave_super_secreta"
```

---

## 🛠️ Paso 4: Crear y aplicar migraciones

Si es la primera vez que trabajas con migraciones:

```bash
flask db init
```

Luego, genera y aplica las migraciones:

```bash
flask db migrate -m "Migración inicial"
flask db upgrade
```

---

## ▶️ Paso 5: Ejecutar la aplicación

Levanta el servidor local ejecutando:

```bash
python run.py
```

La API quedará disponible en:

```
http://127.0.0.1:5000/
```

---

## 📄 Paso 6: Acceder a la documentación Swagger

Una vez que el servidor esté en ejecución, abre tu navegador y visita:

```
http://127.0.0.1:5000/
```

Ahí encontrarás la documentación Swagger generada automáticamente por Flask-RESTx.

# Signature-Rest-Api

Este proyecto backend está construido con Django REST Framework (DRF). Expone una API que maneja autenticación, usuarios, estudiantes, asignaturas y carreras. Todos los endpoints requieren autenticación (Token o sesión) excepto login

## Tecnologías utilizadas

---

- Python
- Django
- Django REST Framework
- SQLite (por defecto)
- Autenticación por Token
- Envío de emails (SMTP con Gmail)

---

## Instalación

1. Clona el repositorio:

```bash
   git clone https://github.com/Flaviongas/Signature-Rest-Api.git
   cd Signature-Rest-Api
```

2. **Crea un entorno virtual e instala las dependencias:**

```bash
- python -m venv .venv
- Windows: .venv\Scripts\activate o Linux source env/bin/activate
- pip install -r requirements.txt
```

3. **Configura las variables de entorno (.env):**

- Crea un archivo `.env` con al menos las siguientes variables:

```
EMAIL_ADDRESS=tu_correo@gmail.com
EMAIL_APP_PASSWORD=tu_clave_de_app
```

4. **Aplica migraciones:**

```bash
python manage.py migrate
```

5. **Corre el servidor de desarrollo:**

```bash
python manage.py runserver
```

## Autenticación

Este proyecto usa autenticación por Token y/o sesión. Para obtener un token, el usuario debe autenticarse usando /login/.

## Endpoints

### Usuarios

- POST /signup/: Crear nuevo usuario (y asociar carreras).
- POST /login/: Iniciar sesión y obtener token.
- GET /api/users/: Listar usuarios.

### Carreras

- GET /api/majors/: Listar carreras.
- GET /api/majors/getMajors/: Listado simplificado de {id, name}.

### Materias

- GET /api/subjects/: Listar materias.
- POST /api/subjects/: Crear materia.

### Estudiantes

- GET /api/students/: Listar estudiantes.
- POST /api/students/: Crear estudiante.

### Email

- POST /sendEmail/: Envía un correo con archivo adjunto (requiere campos filename, email, subject, y un archivo .xlsx en file).

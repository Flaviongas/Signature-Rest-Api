# Guía de Tests - Backend (pytest + Django REST)

## Roles y responsabilidades de QA en el Scrum Team

- **QA Lead (Diomedes Mora):**

  - Diseñar y mantener la estrategia de pruebas.
  - Definir Definition of Done y objetivos de calidad.
  - Supervisar el CI/CD y coordinar esfuerzos de QA.
  - Evaluar métricas y liderar retrospectivas de calidad.

- **QA Analyst (Manuel):**

  - Definir casos de prueba funcionales y regresión.
  - Mantener backlog de pruebas y checklist de validaciones.
  - Validar entregables contra criterios de aceptación.

- **QA Automation Engineer (Flavio):**
  - Desarrollar y mantener pruebas automatizadas (Pytest, Jest).
  - Generar reportes de cobertura y alertas de calidad.

## Configuración

- Todos los tests están implementados con `pytest`.
- La configuración está en el archivo `pytest.ini`.
- Para correr todos los tests manualmente:

```bash
  pytest tests
```

- Para correr un test específico:

```bash
pytest test/test_users.py
```

## Estructura de la carpeta tests/

```
tests/
│
├── test_accounts.py
├── test_majors.py
├── test_students.py
├── test_subjects.py
├── test_users.py
```

## Convenciones para los nombres de funciones

- Se usa el prefijo **test\_**
- Formato: **test_funcionalidad_caso**
- Ejemplos:
  - test_user_creation # prueba creación exitosa de usuario
  - test_create_user_missing_password # prueba creación sin password

## Contenido mínimo esperado para cada archivo de tests

### Para `test_users.py` se deben contemplar al menos los siguientes casos:

#### Consulta de usuarios (GET)

- [x] Listado de usuarios con autorización correcta

#### Creación de usuario (POST)

- [x] Creación exitosa de usuario con datos válidos
- [x] Intento de creación sin password (debe fallar con error 400)
- [x] Intento de creación con nombre de usuario inválido (caracteres no permitidos)

#### Modificación de usuario (PUT/PATCH)

- [x] Modificación exitosa con datos válidos
- [x] Intento de modificación con datos inválidos (ej: username con caracteres especiales)

#### Eliminación de usuario (DELETE)

- [x] Eliminación exitosa de un usuario existente
- [x] Intento de eliminación de un usuario inexistente (debe retornar 404)

#### Seguridad

- [x] Intento de acceso no autorizado (sin token)

### Checklist de pruebas para`test_students.py`

#### Consulta de estudiantes (GET)

- [x] Obtener el listado completo de estudiantes
- [x] Obtener estudiantes filtrados por carrera (`major`)

#### Creación de estudiante (POST)

- [x] Creación exitosa con todos los campos válidos
- [x] Creación fallida si falta algún campo obligatorio (ej: `dv`, `rut`, `major`, etc.)
- [x] Creación fallida si `rut` contiene caracteres no numéricos
- [x] Creación fallida si `dv` contiene caracteres no numéricos
- [x] Creación fallida si el estudiante no tiene al menos una carrera asignada (`major`)
- [x] Creación fallida si `first_name`, `last_name`, `second_name`, `second_last_name` u otros campos contienen caracteres especiales no permitidos (`*/.><` etc.)
- [x] No debe permitirse la creación de estudiantes duplicados con el mismo `rut` y `dv`

#### Eliminación de estudiante (DELETE)

- [x] Eliminación exitosa de un estudiante existente
- [x] Intento de eliminación de un estudiante inexistente (debe retornar 404)

#### Actualización de estudiante (PUT)

- [x] Actualización exitosa con datos válidos

#### Seguridad

- [x] Intento de acceso no autorizado (sin token)

### Checklist de pruebas para `test_subjects.py`

#### Consulta de asignaturas (GET)

- [x] Obtener listado completo de asignaturas
- [x] Obtener detalle de una asignatura por ID

#### Creación de asignaturas (POST)

- [x] Creación exitosa con nombre válido y al menos una carrera (`major`)
- [x] Creación fallida sin carrera asociada
- [x] Creación fallida con nombre vacío

#### Actualización de asignaturas (PATCH)

- [x] Actualización exitosa de nombre y carrera
- [x] Actualización fallida con datos inválidos (nombre vacío)

#### Eliminación de asignaturas (DELETE)

- [x] Eliminación exitosa de una asignatura existente
- [x] Eliminación fallida de asignatura inexistente (404)

#### Inscripción de estudiantes en asignaturas

- [x] Inscripción exitosa de estudiante a asignatura
- [x] Inscripción fallida si el estudiante no existe
- [x] Inscripción fallida si la asignatura no existe

#### Eliminación de inscripción (desinscripción)

- [x] Desinscripción exitosa de estudiante desde asignatura
- [x] Desinscripción fallida si el estudiante no existe

#### Seguridad

- [x] Intento de acceso no autorizado (sin token)

### Checklist de pruebas para `test_majors.py`

#### Consultas (GET)

- [x] Obtener listado de carreras
- [x] Obtener detalle de una carrera por ID
- [x] Acción personalizada `getMajors`
- [x] Detalle de carrera incluye materias asociadas

#### Métodos no permitidos (POST / PUT / PATCH / DELETE)

- [x] Bloqueo de creación (POST) - retorna 405 Method Not Allowed
- [x] Bloqueo de actualización completa (PUT) - retorna 405 Method Not Allowed
- [x] Bloqueo de actualización parcial (PATCH) - retorna 405 Method Not Allowed
- [x] Bloqueo de eliminación (DELETE) - retorna 405 Method Not Allowed

#### Seguridad

- [x] Bloqueo de acceso a usuarios no autenticados (401)

#### Asociación

- [x] Ver materias asociadas a una carrera desde su detalle

### Checklist de pruebas para `test_email_token.py`

#### Envío de correo electrónico

- [x] Envío exitoso de email con archivo adjunto (integración con endpoint `/sendEmail/`)
- [ ] Validación de token de autorización
- [ ] Manejo de error por archivo adjunto faltante o incorrecto
- [ ] Manejo de error por datos faltantes (email, subject, filename)

# Voice Command API en 4Geeks Academy

<!-- hide -->

Por [@ehiber](https://github.com/ehiber) y [otros contribuidores](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors) en [4Geeks Academy](https://4geeksacademy.com/)

[![build by developers](https://img.shields.io/badge/build_by-Developers-blue)](https://4geeks.com)
[![4Geeks Academy](https://img.shields.io/twitter/follow/4geeksacademy?style=social&logo=x)](https://x.com/4geeksacademy)

_These instructions are also available in [English](./README.md)._

**Antes de empezar**: Lee la guia de [como comenzar un proyecto de programacion](https://4geeks.com/lesson/how-to-start-a-project) antes de escribir codigo.

> ¡Te necesitamos! Estos ejercicios se construyen y mantienen en colaboracion con personas como tu. Si encuentras algun error 🐞 o falta de ortografia, por favor contribuye y/o reportalo.

<!-- endhide -->

---

## 🎯 Tu reto

Este repositorio es el template inicial del proyecto **Voice Command API**.

El frontend ya esta construido. Graba hasta **20 segundos** de audio en el navegador, envia ese audio a tu backend y muestra:

- la transcripcion devuelta por la API
- la respuesta final de tareas devuelta por la API

Tu trabajo es implementar el backend para que todo el flujo de voz a accion funcione de punta a punta.

---

## Como funciona el proyecto

El frontend usa un unico punto de entrada publico:

- `POST /transcribe`

El frontend **no** decide intenciones con Web Speech API. Solo captura audio (hasta 20 segundos), envia el archivo a `POST /transcribe` y muestra la transcripcion devuelta por el backend para depurar mejor.

Ese endpoint debe:

1. recibir el audio grabado desde el frontend
2. transcribirlo a texto
3. reutilizar la misma logica de routing que `POST /instruction`
4. ejecutar la accion correspondiente sobre las tareas en memoria
5. devolver la transcripcion, la instruccion y el resultado final

Tu backend tambien debe exponer:

- `POST /instruction`
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

Importante:

- Usa **solo almacenamiento en memoria**. No base de datos ni archivos.
- El frontend ya viene dado y no deberias modificarlo como parte del ejercicio.
- El backend incluido en este repositorio es solo un template. Tu debes completar la logica faltante.

---

## Estructura del repositorio

```text
voice-command-api/
|-- .devcontainer/           # Configuracion para Codespaces
|-- frontend/                # Frontend ya listo
|   |-- public/
|   `-- src/
|-- src/
|   `-- app/
|       |-- api/routes/      # /transcribe, /instruction, /tasks
|       |-- core/            # Configuracion
|       |-- schemas/         # Contratos de request y response
|       |-- services/        # Aqui va tu implementacion
|       `-- utils/
|-- pyproject.toml
|-- README.md
`-- README.es.md
```

---

## 🌱 Como iniciar el proyecto

Puedes abrir este proyecto en [GitHub Codespaces](https://codespaces.new/4GeeksAcademy/voice-command-api) o clonarlo localmente.

Si usas Codespaces, el repositorio ya incluye un `.devcontainer` preparado para Python, Node, FastAPI y Vite.

### Opcion A: GitHub Codespaces

1. Abre el repositorio en Codespaces.
2. Espera a que el dev container termine de instalar dependencias.
3. Crea `.env` a partir de `.env.example`.
4. Crea `frontend/.env` a partir de `frontend/.env.example`.
5. Ejecuta el backend y el frontend desde la terminal.

### Opcion B: Configuracion local

```bash
git clone https://github.com/4GeeksAcademy/voice-command-api
cd voice-command-api
```

Crea tu propio repositorio y actualiza el remoto:

```bash
git remote set-url origin https://github.com/TU_USUARIO/TU_REPOSITORIO
```

### Configuracion del backend

Configura un archivo `.env` con las variables necesarias para los proveedores. En este workspace, Groq se usa para transcribir audio y LUNA para generar las instrucciones. El enunciado original propone Groq para el routing; aqui se usa LUNA porque es el proveedor habilitado para la cuenta configurada.

```env
GROQ_API_KEY=tu_clave_de_groq
GROQ_TRANSCRIPTION_MODEL=whisper-large-v3-turbo
LUNA_API_KEY=tu_clave_de_luna
LUNA_URL_BASE=https://llm.4geeks.ai
LUNA_MODEL=online/openrouter/openai/gpt-6-luna
```

No subas `.env` al repositorio ni compartas las claves.

Instala dependencias y ejecuta la API:

```bash
uv sync
uv run uvicorn src.main:app --reload
```

### Configuracion del frontend

Crea `frontend/.env` a partir de `frontend/.env.example`.

Ejecuta el frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## 💻 Qué debes hacer

- [ ] Crea una lista `tasks` a nivel de modulo con `id`, `title` y `done`, usando IDs unicos e incrementales.
- [ ] Implementa `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}` y `DELETE /tasks/{task_id}` con almacenamiento en memoria.
- [ ] Implementa `POST /instruction` para recibir `{ "transcription": "..." }`, llamar a Groq y devolver **solo** JSON de routing (sin ejecutar tareas):

```json
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": { "title": "Buy groceries" }
}
```

- [ ] Implementa `POST /transcribe` para aceptar `multipart/form-data`, convertir audio a texto, reutilizar la logica de `/instruction`, ejecutar la accion y devolver `transcription`, `instruction` y `result`.
- [ ] No hardcodees el routing con reglas manuales como `if "add" in text`.

⚠️ **IMPORTANTE:** El frontend no decide intenciones con Web Speech API. Solo captura audio (hasta 20 segundos), envia a `POST /transcribe` y muestra la transcripcion del backend para depurar STT vs. routing.

```json
{
  "transcription": "add buy groceries to my list",
  "instruction": {
    "endpoint": "/tasks",
    "method": "POST",
    "params": {
      "title": "Buy groceries"
    }
  },
  "result": {
    "id": 1,
    "title": "Buy groceries",
    "done": false
  }
}
```

---

## Tip para depurar

Si la transcripcion que se ve en el frontend ya esta mal, el problema esta en la captura de audio o en el speech-to-text.

Si la transcripcion esta bien pero la accion sale mal, el problema esta en `/instruction`.

---

## ✅ Qué vamos a evaluar

- [ ] `POST /transcribe` recibe audio, transcribe y reutiliza la logica de `/instruction`.
- [ ] `POST /instruction` recibe texto plano y devuelve solo JSON de routing (sin ejecutar acciones).
- [ ] `GET /tasks`, `POST /tasks`, `PUT /tasks/{task_id}`, `PATCH /tasks/{task_id}` y `DELETE /tasks/{task_id}` funcionan correctamente con memoria en proceso.
- [ ] El frontend muestra la transcripcion devuelta por el backend para distinguir errores de STT vs. errores de routing.

---

## Guia paso a paso de la implementacion

Esta seccion explica como se conectan las piezas del backend y que aprende cada una. La interfaz incluida en este repositorio graba audio con `MediaRecorder` y llama a `POST /transcribe`; no llama directamente a `/instruction` para hacer una segunda peticion.

### 1. Configurar las credenciales y los modelos

La aplicacion carga desde `.env` las variables descritas en la configuracion del backend. No compartas ni subas las claves. En esta implementacion, Groq/Whisper convierte el audio en texto y LUNA interpreta ese texto para elegir una accion. El identificador del modelo LUNA se normaliza para quitar el prefijo `litellm/` si aparece en la configuracion.

### 2. Guardar tareas en memoria

En `src/app/api/routes/tasks.py`, la lista de modulo `tasks` guarda diccionarios con `id`, `title` y `done`. `next_task_id` asigna IDs consecutivos. Como no hay base de datos, las tareas se reinician cuando se reinicia el servidor.

Las rutas CRUD usan esa misma lista:

- `GET /tasks` devuelve todas las tareas.
- `POST /tasks` valida `title`, permite `done` opcional y devuelve `201` con la tarea creada.
- `PUT /tasks/{task_id}` reemplaza `title` y `done`; devuelve `404` si no existe el ID.
- `PATCH /tasks/{task_id}` actualiza solo los campos enviados.
- `DELETE /tasks/{task_id}` devuelve `204` sin cuerpo al eliminar y `404` si no encuentra la tarea.

### 3. Convertir texto en una instruccion

`POST /instruction` recibe un cuerpo JSON como:

```json
{ "transcription": "Añade comprar leche a mi lista" }
```

El servicio `src/app/services/voice.py` envia el texto y las tareas actuales al modelo LUNA. El prompt pide solo JSON; despues, el backend valida que el endpoint y el metodo pertenezcan a las operaciones de tareas admitidas. Esta ruta devuelve el plan, pero no ejecuta la accion.

Respuesta de ejemplo:

```json
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": { "title": "Comprar leche" }
}
```

### 4. Procesar el audio que envia la interfaz

`POST /transcribe` admite dos entradas para cubrir la interfaz completa:

1. Audio `multipart/form-data`, en el campo `file`; puede incluir `language`.
2. JSON con `transcription`, para el modo de transcripcion manual.

Para audio, Groq/Whisper devuelve el texto. Luego el backend reutiliza el servicio de routing, ejecuta la operacion sobre las tareas y responde con `transcription`, `instruction` y `result`. Asi el frontend puede mostrar tanto lo que entendio como el resultado de la accion.

```json
{
  "transcription": "Añade comprar leche a mi lista",
  "instruction": {
    "endpoint": "/tasks",
    "method": "POST",
    "params": { "title": "Comprar leche" }
  },
  "result": { "id": 1, "title": "Comprar leche", "done": false }
}
```

### 5. Ejecutar el routing sin duplicar el CRUD

`execute_instruction` traduce el JSON validado a una llamada a la funcion CRUD correspondiente. Por ejemplo, `POST /tasks` crea una tarea en memoria. El modelo propone la operacion; el backend valida sus parametros y realiza la accion. No se usan reglas como `if "añade" in transcription`.

### 6. Permitir la conexion desde el frontend

`src/app/main.py` configura CORS para los origenes locales y para el dominio de Codespaces usado por Vite en el puerto `5173`. Si ejecutas el frontend en otro puerto o dominio, agrega su origen a `ALLOWED_ORIGINS` o ajusta `ALLOWED_ORIGIN_REGEX` en la configuracion; no habilites cualquier origen sin necesidad.

### 7. Interpretar errores frecuentes

- `422`: falta un campo o el routing/parametro no es valido.
- `404`: el ID de tarea solicitado no existe.
- `502`: el proveedor de transcripcion o de routing rechazo la solicitud o no respondio. Revisa la terminal del backend; el log indica que proveedor y modelo fallaron, sin imprimir las claves.
- Error CORS en el navegador: comprueba el origen exacto del frontend, el puerto publicado y que el backend se haya reiniciado despues de cambiar la configuracion.

---

## 📦 Cómo entregar este proyecto

1. Sube tu solucion a tu repositorio de GitHub.
2. Asegurate de incluir backend y frontend configurados para correr localmente.
3. Comparte el enlace del repositorio y un breve video o GIF mostrando:
   - grabacion de audio (20 segundos maximo),
   - transcripcion visible en frontend,
   - ejecucion correcta de acciones sobre tareas.

---

Este y muchos otros proyectos son construidos por estudiantes como parte de los [Coding Bootcamps](https://4geeksacademy.com/) de 4Geeks Academy. Encuentra mas acerca de los cursos de [Full-Stack Software Developer](https://4geeksacademy.com/es/programas-de-carrera/desarrollo-full-stack), [Data Science & Machine Learning](https://4geeksacademy.com/en/career-programs/data-science-ml), [Ciberseguridad](https://4geeksacademy.com/es/programas-de-carrera/ciberseguridad) e [Ingeniería de IA](https://4geeksacademy.com/es/programas-de-carrera/ingenieria-ia).

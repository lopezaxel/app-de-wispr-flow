# NIKI Flow

Dictado por voz personal para Windows. Se activa mantenendo **Ctrl+Win+Espacio** o diciendo **"Hey Viki"** en voz alta, hablás, y el texto transcripto se pega donde tengas el cursor. Una barrita flotante siempre encima de todo te muestra si está escuchando o transcribiendo, con un botón para cancelar. Corre en segundo plano desde la bandeja del sistema.

Pensada para uso propio en dos equipos (notebook + PC de escritorio), sin las opciones ni el costo de Wispr Flow.

## Cómo funciona

1. Activación, de dos formas:
   - `Ctrl+Win+Espacio` mantenido: graba mientras lo sostenés, para al soltar (push-to-talk).
   - Decir "Hey Viki": graba y corta sola al detectar que dejaste de hablar (silencio sostenido).
2. El widget flotante muestra barras animadas con tu voz mientras graba, y un botón "✕" para cancelar en cualquier momento.
3. Al terminar: el audio se comprime a FLAC y se manda a la API de Groq (Whisper large-v3-turbo) para transcribir.
4. Se muestra el texto transcripto en una ventanita editable por un momento — si está bien, no hace falta tocar nada, se pega solo pasado el timeout. Si algo salió mal, lo corregís ahí mismo antes de que se pegue.
5. El texto final se copia al portapapeles y se pega automáticamente (`Ctrl+V`) donde esté el foco, preservando lo que tenías copiado antes.

## Revisión y aprendizaje

Antes de pegar, NIKI Flow te muestra el texto transcripto en una ventanita editable (misma zona que el widget flotante). Si lo dejás sin tocar, se pega solo a los pocos segundos. Si corregís algo ahí, esa corrección queda guardada — no se agrega sola al diccionario, pero alimenta la sección "Diccionario → Sugerencias" del panel, donde vas a ver las correcciones que se repiten con un botón para sumarlas al vocabulario personalizado con un clic.

- `Enter` acepta y pega.
- `Shift+Enter` inserta un salto de línea.
- `Esc` descarta (no se pega ni se guarda nada).
- Se puede desactivar del todo con `NIKI_FLOW_REVIEW_ENABLED=false` en tu `.env` (vuelve al pegado inmediato de antes).

## Panel

Desde el menú de la bandeja del sistema, "Abrir panel" abre una ventana nativa con:

- **Resumen**: total de dictados, cuántos corregiste, palabras dictadas.
- **Historial**: todos tus dictados, con lo que cambiaste resaltado en los que corregiste.
- **Diccionario**: tu vocabulario personalizado (alta/baja desde la UI) y las sugerencias de correcciones repetidas.

Los datos se guardan localmente en `niki_flow_data/` (SQLite, no versionado — es contenido personal, a diferencia de `dictionary.txt`).

El hotkey usa un hook de teclado nativo de Windows (vía `ctypes`, no una librería externa) para poder interceptar Ctrl+Win+Espacio de forma confiable sin abrir el menú Inicio. La detección de palabra clave corre 100% local con [openWakeWord](https://github.com/dscripka/openWakeWord) (open source, sin cuenta ni API key), escuchando en un stream de audio separado del de grabación.

### Palabra clave personalizada ("Hey Viki")

Ya está entrenada y configurada: `wakeword/hey-viki.onnx`, apuntada desde `.env` con `NIKI_FLOW_WAKEWORD_MODEL=wakeword/hey-viki.onnx`. Se entrenó en [openwakeword.com/train](https://openwakeword.com/train) (gratis, sin cuenta).

Si en el futuro querés otra palabra clave: entrenás un modelo nuevo ahí escribiendo la frase, descargás el `.onnx`, lo guardás en `wakeword/`, y actualizás `NIKI_FLOW_WAKEWORD_MODEL` en tu `.env`. Sin `.env` configurado, el código cae de vuelta al modelo `hey_jarvis` incluido por defecto.

Se puede desactivar del todo con `NIKI_FLOW_WAKEWORD_ENABLED=false` (queda solo el atajo de teclado).

## Instalación (en cada máquina)

1. Python 3.10+ instalado y en el PATH.
2. Clonar este repo.
3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Conseguir una API key gratis en [console.groq.com](https://console.groq.com) (tiene capa gratuita; el uso normal de dictado cuesta centavos por mes).
5. Copiar `.env.example` a `.env` y completar `GROQ_API_KEY`.
6. Probar: `python main.py` — debería aparecer un ícono gris en la bandeja del sistema.

## Iniciar automáticamente con Windows

1. Presioná `Win+R`, escribí `shell:startup` y Enter.
2. Poné ahí un acceso directo a `run_niki_flow.vbs` (este script corre `pythonw.exe` sin abrir consola).

No hace falta correrlo como administrador.

## Diccionario personalizado

Editá `dictionary.txt` (una palabra o frase por línea) para agregar nombres propios o términos que Whisper suele escribir mal — por ejemplo `NIKI Flow`, `sistemaniki`, `CAEIA`. Se usa como contexto en cada transcripción y se recarga solo, no hace falta reiniciar la app. También podés abrirlo desde el menú de la bandeja ("Abrir diccionario").

Como el archivo está versionado en este repo, si lo actualizás en una máquina y hacés `git pull` en la otra, el diccionario queda sincronizado en ambas.

## Configuración opcional (`.env`)

- `NIKI_FLOW_LANGUAGE`: idioma para la transcripción (default `es`).
- `NIKI_FLOW_MODEL`: modelo de Groq a usar (default `whisper-large-v3-turbo`).
- `NIKI_FLOW_WAKEWORD_MODEL`: nombre corto (`hey_jarvis`) o ruta a un `.onnx` propio (default `hey_jarvis`).
- `NIKI_FLOW_WAKEWORD_THRESHOLD`: confianza mínima para activar, 0 a 1 (default `0.5`).
- `NIKI_FLOW_WAKEWORD_ENABLED`: `true`/`false` para activar o no la escucha por voz (default `true`).
- `NIKI_FLOW_REVIEW_ENABLED`: `true`/`false` para mostrar o no la ventanita de revisión antes de pegar (default `true`).
- `NIKI_FLOW_REVIEW_TIMEOUT`: segundos antes de que la revisión se auto-acepte sola (default `4`).

## Estructura

```
main.py               # entrypoint: conecta hotkey -> grabación -> transcripción -> revisión -> pegado
niki_flow/
  config.py            # variables de entorno
  hotkey.py            # detección de Ctrl+Win+Espacio (push-to-talk, hook nativo de Windows)
  wakeword.py          # detección de palabra clave ("Hey Viki") con openWakeWord
  recorder.py          # captura de audio del micrófono + nivel para el widget
  transcriber.py        # llamada a la API de Groq (audio comprimido a FLAC)
  review.py              # ventanita de revisión/corrección antes de pegar
  injector.py           # pegado del texto vía portapapeles
  storage.py             # historial de dictados y correcciones (SQLite)
  dictionary.py          # carga y edición del vocabulario personalizado
  tray.py                # ícono de bandeja del sistema
  overlay.py              # widget flotante con barras de audio animadas
  dashboard/               # panel nativo (pywebview): python -m niki_flow.dashboard
    api.py                   # puente entre el JS del panel y storage.py / dictionary.py
    web/                     # index.html, style.css, app.js
dictionary.txt            # vocabulario personalizado (versionado)
niki_flow_data/            # historial local (SQLite, no versionado)
run_niki_flow.vbs         # lanzador silencioso para el inicio de Windows
```

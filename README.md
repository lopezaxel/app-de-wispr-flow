# NIKI Flow

Dictado por voz personal para Windows. Mantenés **Ctrl+Win+Espacio** apretado, hablás, soltás, y el texto transcripto se pega donde tengas el cursor. Una barrita flotante siempre encima de todo te muestra si está escuchando o transcribiendo. Corre en segundo plano desde la bandeja del sistema.

Pensada para uso propio en dos equipos (notebook + PC de escritorio), sin las opciones ni el costo de Wispr Flow.

## Cómo funciona

1. `Ctrl+Win+Espacio` mantenido: graba del micrófono (el widget flotante muestra barras animadas con tu voz).
2. Al soltar: el audio se comprime a FLAC y se manda a la API de Groq (Whisper large-v3-turbo) para transcribir.
3. El texto se copia al portapapeles y se pega automáticamente (`Ctrl+V`) donde esté el foco, preservando lo que tenías copiado antes.

El hotkey usa un hook de teclado nativo de Windows (vía `ctypes`, no una librería externa) para poder interceptar Ctrl+Win+Espacio de forma confiable sin abrir el menú Inicio.

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

## Estructura

```
main.py               # entrypoint: conecta hotkey -> grabación -> transcripción -> pegado
niki_flow/
  config.py            # variables de entorno
  hotkey.py            # detección de Ctrl+Win+Espacio (push-to-talk, hook nativo de Windows)
  recorder.py          # captura de audio del micrófono + nivel para el widget
  transcriber.py        # llamada a la API de Groq (audio comprimido a FLAC)
  injector.py           # pegado del texto vía portapapeles
  dictionary.py          # carga del vocabulario personalizado
  tray.py                # ícono de bandeja del sistema
  overlay.py              # widget flotante con barras de audio animadas
dictionary.txt            # vocabulario personalizado (versionado)
run_niki_flow.vbs         # lanzador silencioso para el inicio de Windows
```

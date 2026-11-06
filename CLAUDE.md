# IA al Toque: manual de producción diaria

Canal sin rostro de reels de IA práctica en español. Mascota: Kusi (alpaca robot). Voz: Laura (ElevenLabs, id `FGY2WhTYpPnrIDTdsKH5`).
Cuentas: YouTube @IAalToqueOficial · TikTok @iaaltoqueoficial · Instagram @iaaltoqueoficial.
Metricool: brand/blogId `7867705`, zona horaria `America/Lima`.
Documento de marca y guiones: https://claude.ai/artifact/DjzGM379bGwBbW6b371mT1

## Reglas de contenido
- 45–60 s, 5–7 escenas: `hook` → `step`/`list` → `cta`. Narración total de 600–750 caracteres.
- Español latino neutro, frases cortas, un truco concreto y útil por reel.
- Verificar con búsqueda web cualquier función, precio o dato de una herramienta. Nada inventado.
- No repetir temas de `reels/historial.md`. Alternar formatos (pasos, lista, comparativa, caso real).
- Nada de marcas o personajes ajenos dibujados; solo Kusi.

## Pasos de cada día
1. Elegir tema: revisar `reels/historial.md`; buscar en la web qué está en tendencia en IA práctica en español.
   No usar vidIQ (dado de baja). Para estadísticas, usar Metricool.
2. Crear `reels/reel_NN/guion.json` (ver formato en `tools/make_reel.py`). Añadir `titulo`, `descripcion` y `hashtags`.
3. Voz: `python3 -c "import json,sys;sys.path.insert(0,'tools');from make_reel import narration;open('reels/reel_NN/voz.txt','w').write(narration(json.load(open('reels/reel_NN/guion.json'))))"`
   y luego `python3 tools/tts.py reels/reel_NN/voz.txt reels/reel_NN/voz` (la clave la inserta el secreto de red del entorno).
   Si falla, NO usar otra voz: avisar al usuario y parar.
4. Video: `python3 tools/make_reel.py reels/reel_NN/guion.json reels/reel_NN/voz.mp3 reels/reel_NN/reel_NN.mp4 reels/reel_NN/voz.align.json`
5. Revisar 6 fotogramas a lo largo del video (texto legible, nada cortado, subtítulos sincronizados). Corregir y volver a renderizar si hace falta.
6. `git add reels/reel_NN && git commit && git push`. URL pública del video:
   `https://raw.githubusercontent.com/JuanCarlos0501/iaaltoque-media/main/reels/reel_NN/reel_NN.mp4`
7. Metricool `createScheduledPost` **programado** (`draft: false`, `autoPublish: true`) para hoy a las **10:00 Lima**
   (la hora con más actividad según `getBestTimeToPostByNetwork`). Redes: instagram (REEL, isAiGenerated true), tiktok (isAigc true, title = `titulo`: Metricool lo exige),
   youtube (type short, madeForKids false, category EDUCATION, título = `titulo`).
   Portada: añade `videoCoverMilliseconds: 800` (cuadro del gancho). Si Metricool lo rechaza con VIDEO_THUMBNAIL_NOT_APPLICABLE, repite sin ese campo.
   En la automatización diaria este paso lo hace la tarea "IA al Toque - programar en Metricool" (8:21 y 11:21 Lima), no la de producción.

## Automatización diaria (3 reels)
- "IA al Toque - producir 3 reels (nube)" (trig_01KaKZ4hFZPEboqxvXspRVsQ): 6:34 Lima, entorno de nube **IA al Toque** (api.elevenlabs.io permitido, secreto de red con la clave) y con el conector Claude_Code_Remote: el repo llega clonado y el push a main funciona (probado el 6 nov). Pasos 1–6 y 8 para tres reels: A "video listo, falta programar 10:00", B "…12:00", C "…18:00".
- "IA al Toque - programar en Metricool": 8:21 y 11:21 Lima. Programa en Metricool a las 10:00, 12:00 y 18:00 y avisa por push.
- Domingos 15:17 "IA al Toque - carruseles e historias de la semana" (3 carruseles IG lun/mié/vie 20:00 con `tools/make_social.py spec.json` + historia diaria 10:05 `social/historias/h_<dia>.jpg`).
- Domingos 15:43 "Metabolic Spa - publicaciones de la semana" (blogId 7870675: flyer diario 12:00 con `spa/textos.json` + 3 historias 09:00/13:00/19:30). Todas en la nube, entorno IA al Toque; no dependen de ningún equipo encendido.
- Ojo: una tarea de producción sin el repo autorizado falla con 403 al hacer push (pasó el 6 nov con "crear reels (Code)", ya desactivada). Las tareas de tipo Chat corren en el entorno por defecto, que bloquea ElevenLabs.
8. Añadir la línea del reel a `reels/historial.md` y hacer push.
9. Avisar al usuario (PushNotification + mensaje): título del reel, que sale a las 10:00 y el enlace en Metricool por si quiere editarlo antes.

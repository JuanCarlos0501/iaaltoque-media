"""Genera la voz de Kusi con ElevenLabs y guarda la alineación por carácter.

Uso: python3 tts.py texto.txt salida_sin_extension
Crea salida.mp3 y salida.align.json. La clave la pone el secreto de red del entorno (o ELEVENLABS_API_KEY).
"""
import base64, json, os, sys, urllib.request

VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"  # Laura (elegida para Kusi)
MODEL = "eleven_multilingual_v2"

txt_path, out = sys.argv[1], sys.argv[2]
text = open(txt_path, encoding="utf-8").read().strip()
# La clave la inserta el entorno (secreto de red para api.elevenlabs.io).
# Si además existe ELEVENLABS_API_KEY, se usa como respaldo.
key = os.environ.get("ELEVENLABS_API_KEY")

req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128",
    data=json.dumps({"text": text, "model_id": MODEL,
                     "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode(),
    headers={**({"xi-api-key": key} if key else {}), "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=180) as r:
    data = json.load(r)

open(out + ".mp3", "wb").write(base64.b64decode(data["audio_base64"]))
json.dump({"text": text, "alignment": data.get("alignment")}, open(out + ".align.json", "w"), ensure_ascii=False)
print("ok", len(text), "caracteres")

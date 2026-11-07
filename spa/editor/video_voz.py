"""Versión con voz de la doctora: cada escena dura lo que dura su frase; subtítulos exactos del guion."""
import json, subprocess, sys
from pathlib import Path
import video as v

VOZ = Path("/mnt/user-data/uploads/voz/voz_sanendi.wav")
TIEMPOS = Path("/mnt/user-data/uploads/voz/voz_sanendi.tiempos.json")
D, T, W, H = v.D, v.T, v.W, v.H

# (escena, frase exacta que dice la voz)
GUION = [
    ("intro", "Hola, soy la doctora Winifer González."),
    ("mov1", "Llegó a Metabolic Spa CAX la línea Sanendi, ácido hialurónico de alta pureza."),
    ("ultra", "Ultra Volume da volumen y define pómulos, mentón y línea mandibular."),
    ("light", "Light corrige líneas finas, el contorno de ojos y los labios, con un resultado sutil y natural."),
    ("deep", "Deep Line suaviza surcos nasolabiales y líneas de marioneta."),
    ("plla", "Y el ácido poli láctico es un bioestimulador: ayuda a tu piel a producir su propio colágeno, para más firmeza de forma progresiva."),
    ("mov2", "Cada tratamiento se aplica con una evaluación médica previa."),
    ("cierre", "Escríbenos por WhatsApp y agenda tu evaluación aquí en Cajamarca."),
]


def palabras(t): return len(t.split())


def tiempos_por_frase(total):
    """Reparte los tiempos del .tiempos.json (bloques) entre las frases del guion, por número de palabras."""
    bloques = json.loads(TIEMPOS.read_text())["frases"]
    marcas = []  # (inicio, fin) por frase
    gi = 0
    for b in bloques:
        n_b = palabras(b["texto"]); acum = 0
        dur = b["fin"] - b["inicio"]
        # frases del guion que caen en este bloque, hasta cubrir sus palabras
        while gi < len(GUION) and acum < n_b - 1:
            n = palabras(GUION[gi][1]); ini = b["inicio"] + dur * acum / n_b
            acum += n; fin = b["inicio"] + dur * min(acum, n_b) / n_b
            marcas.append([ini, fin]); gi += 1
    while len(marcas) < len(GUION):  # por si sobra alguna
        marcas.append([marcas[-1][1], total])
    return marcas


def ass(marcas):
    def ts(s):
        h, r = divmod(s, 3600); mi, se = divmod(r, 60); return f"{int(h)}:{int(mi):02d}:{se:05.2f}"
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: S,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0101018,1,0,0,0,100,100,0,0,3,14,0,2,90,90,640,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for (esc, frase), (ini, fin) in zip(GUION, marcas):
        pal = frase.split(); trozos = []; cur = []
        for p in pal:
            cur.append(p)
            if len(" ".join(cur)) > 26 or p.endswith((",", ":", ".")):
                trozos.append(" ".join(cur)); cur = []
        if cur: trozos.append(" ".join(cur))
        tot = sum(len(t) for t in trozos); t0 = ini
        for t in trozos:
            t1 = t0 + (fin - ini) * len(t) / tot
            pos = "{\\an2\\pos(540,1720)}" if esc in ("intro", "cierre") else ""
            ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},S,,0,0,0,,{pos}{t}")
            t0 = t1
    (T / "subs.ass").write_text(head + "\n".join(ev) + "\n")


if __name__ == "__main__":
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VOZ)],
                                 capture_output=True, text=True).stdout) + 1.8
    marcas = tiempos_por_frase(total)
    # duración de cada escena: del inicio de su frase al inicio de la siguiente
    inicios = [0.0] + [m[0] for m in marcas[1:]] + [total]
    durs = [round(inicios[i + 1] - inicios[i], 2) for i in range(len(GUION))]
    ass([[inicios[i], marcas[i][1]] for i in range(len(GUION))])
    for (esc, _), dur in zip(GUION, durs):
        if esc in ("intro", "cierre"): v.seg_tarjeta(esc, dur)
        elif esc == "mov1": v.seg_video(esc, 0.3, min(dur, 10.5), "ov_mov1")
        elif esc == "mov2": v.seg_video(esc, max(0, 11.1 - dur), dur, "ov_mov2")
        else: v.seg_foto(esc, v.FOTOS[esc], dur, f"ov_{esc}", zoom_in=esc in ("ultra", "deep"))
    v.musica(total)
    (T / "lista.txt").write_text("".join(f"file '{e}.mp4'\n" for e, _ in GUION))
    v.sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(T / "lista.txt"), "-i", str(VOZ),
         "-i", str(T / "musica.wav"), "-filter_complex",
         "[0:v]subtitles=" + str(T / "subs.ass") + ":fontsdir=/root/.fonts[vv];"
         "[1:a]highpass=f=70,loudnorm=I=-16:TP=-1.5,aresample=48000,asplit[vo][vo2];"
         "[2:a]volume=0.35[mu];[mu][vo]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[duck];"
         "[duck][vo2]amix=inputs=2:normalize=0,alimiter=limit=0.84[a]",
         "-map", "[vv]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-t", str(total), "-movflags", "+faststart", str(D / "sanendi_con_voz.mp4"))
    print("ok", total, durs)

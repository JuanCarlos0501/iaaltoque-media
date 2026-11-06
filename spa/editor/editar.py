#!/usr/bin/env python3
"""Editor de reels de Metabolic Spa CAX.

Uso:  python3 editar.py "<carpeta Metabolic Spa - Videos>" [--fecha AAAA-MM-DD] [--dry]

Toma los clips de "1 Entrada", arma UN reel vertical 1080x1920 (30-40 s) con los clips
del mismo servicio, le pone logo, título del servicio, cierre con precio y WhatsApp, y lo
guarda en "2 Editados". Los clips usados pasan a "3 Publicados/<fecha>/".
Funciona sin internet (solo ffmpeg + Pillow).

El servicio se detecta por el nombre del archivo (por ejemplo "exonucell 1.mov",
"botox paciente.mp4"). Si no tiene palabra clave, se usa el genérico del spa.
"""
import json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
MAX_TOTAL = 38.0      # segundos de clips (sin contar el cierre)
END = 3.5             # segundos del cierre
VIDEO_EXT = {".mov", ".mp4", ".m4v"}
WHATSAPP = "987 293 339 · 931 055 214"

SERVICIOS = [
    # (palabras clave, nombre, subtítulo, precio, hashtags)
    (["exonucell", "exosoma"], "Exonucell X", "PDRN + exosomas + GHK-Cu", "4 sesiones · S/ 1,800",
     "#Exosomas #PDRN #CuidadoDeLaPiel"),
    (["biolift", "bio-lift", "bio lift"], "Bio-Lift Facial", "Regeneración y efecto lifting", "4 sesiones · S/ 1,500",
     "#BioLift #Rejuvenecimiento #PDRN"),
    (["botox"], "Botox full face", "Resultado natural · aplicado por médico", "S/ 850 · en pareja S/ 750 c/u",
     "#EsteticaAvanzada #LineasDeExpresion"),
    (["lipo"], "Lipoescultor", "Tratamiento corporal", "1 zona S/ 300 · 5 zonas S/ 1,150",
     "#TratamientoCorporal #Lipoescultor"),
    (["prp", "plasma"], "PDRN + PRP", "Revitalización facial integral", "3 sesiones · S/ 800",
     "#PRP #PDRN #CuidadoDeLaPiel"),
    (["dermapen"], "Dermapen con PDRN", "Regeneración y textura", "S/ 175",
     "#Dermapen #PDRN #CuidadoDeLaPiel"),
    (["hydro", "hidro"], "Hydroglow", "Hidrofacial avanzado", "S/ 89",
     "#Hidrofacial #CuidadoDeLaPiel"),
    (["detox", "limpieza"], "Dermadetox", "Limpieza facial profunda", "S/ 70",
     "#LimpiezaFacial #CuidadoDeLaPiel"),
    (["sweep", "exfol"], "Dermasweep", "Exfoliación y renovación", "S/ 99",
     "#Exfoliacion #CuidadoDeLaPiel"),
    (["radiance", "aclar", "manchas"], "Radiance C-Matrix", "Tono más uniforme", "S/ 99",
     "#Manchas #CuidadoDeLaPiel"),
]
GENERICO = (["spa"], "Metabolic Spa CAX", "Ciencia · estética · bienestar", "Agenda tu evaluación",
            "#EsteticaAvanzada #CuidadoDeLaPiel")

GOLD = (217, 182, 110)
INK = (21, 17, 13)
CREAM = (245, 238, 226)


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def servicio_de(nombre):
    n = norm(nombre)
    for s in SERVICIOS:
        if any(k in n for k in s[0]):
            return s
    return GENERICO


def font(name, size, wght=600):
    f = ImageFont.truetype(str(HERE / "fonts" / name), size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd[:6]) + "...\n" + r.stderr[-2000:])
    return r.stdout


def probe(p):
    j = json.loads(sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)]))
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = any(s["codec_type"] == "audio" for s in j["streams"])
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = abs(int(float(sd["rotation"])))
    rot = rot or abs(int(v.get("tags", {}).get("rotate", 0) or 0))
    if rot in (90, 270):
        w, h = h, w
    hdr = v.get("color_transfer") in ("arib-std-b67", "smpte2084")
    return float(j["format"]["duration"]), w, h, a, hdr


def text_png(path, lines, box=True):
    """lines: [(texto, fuente, tamaño, color)] centradas, en una franja inferior."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fonts = [font(f, s) for _, f, s, _ in lines]
    hs = [d.textbbox((0, 0), t, font=fo)[3] for (t, *_), fo in zip(lines, fonts)]
    total = sum(hs) + 18 * (len(lines) - 1)
    y0 = 1300
    if box:  # degradado inferior (sin caja) + filete dorado: look de "lower third" profesional
        top, bot = y0 - 420, H
        for yy in range(top, bot):
            a = int(225 * min(1.0, (yy - top) / 420) ** 1.8)
            d.line([(0, yy), (W, yy)], fill=(*INK, a))
    y = y0
    for (t, _, _, col), fo, hh in zip(lines, fonts, hs):
        tw = d.textbbox((0, 0), t, font=fo)[2]
        d.text(((W - tw) / 2, y), t, font=fo, fill=col)
        y += hh + 18
        if box and col == GOLD:   # filete dorado bajo el nombre del servicio
            d.line([((W - 140) / 2, y + 2), ((W + 140) / 2, y + 2)], fill=GOLD, width=3)
            y += 22
    img.save(path)


def logo_png(path, size=150):
    lg = Image.open(HERE / "logo.png").convert("RGBA")
    lg.thumbnail((size, size))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # sombra suave para que se lea sobre cualquier fondo
    pad = Image.new("RGBA", (lg.width + 30, lg.height + 30), (21, 17, 13, 110))
    m = Image.new("L", pad.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *pad.size), radius=24, fill=255)
    img.paste(pad, (40, 70), m)
    img.paste(lg, (55, 85), lg)
    img.save(path)


def cierre_png(path, srv):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    lg = Image.open(HERE / "logo.png").convert("RGBA")
    lg.thumbnail((360, 360))
    img.paste(lg, ((W - lg.width) // 2, 330), lg)

    def c(t, fo, y, col):
        tw = d.textbbox((0, 0), t, font=fo)[2]
        d.text(((W - tw) / 2, y), t, font=fo, fill=col)

    c(srv[1], font("CormorantGaramond.ttf", 120), 800, GOLD)
    c(srv[3], font("Montserrat.ttf", 58), 980, CREAM)
    c("Agenda tu evaluación por WhatsApp", font("Montserrat.ttf", 44), 1180, CREAM)
    c(WHATSAPP, font("Montserrat.ttf", 64), 1260, GOLD)
    c("Cajamarca", font("Montserrat.ttf", 40), 1400, (190, 180, 165))
    img.save(path)


XF = 0.35            # segundos de transición suave entre clips
# Look de marca: limpieza de ruido suave, contraste y color moderados, cálido leve, nitidez fina y viñeta sutil.
GRADE = ("hqdn3d=1.2:1.2:4:4,eq=contrast=1.05:saturation=1.08:gamma=1.02,"
         "colorbalance=rm=0.03:bm=-0.03:rh=0.02:bh=-0.02,unsharp=5:5:0.45:5:5:0")
_FILTROS = None


def tiene_filtro(nombre):
    global _FILTROS
    if _FILTROS is None:
        try:
            _FILTROS = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        except Exception:
            _FILTROS = ""
    return f" {nombre} " in _FILTROS


def vf_clip(w, h, hdr, estab=None):
    tm = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
          "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,") if hdr else ""
    st = f"vidstabtransform=input='{estab}':smoothing=12:zoom=2," if estab else ""
    if h >= w:  # vertical: llenar el cuadro
        return (f"{tm}{st}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE},"
                f"setsar=1,fps={FPS},format=yuv420p")
    # horizontal: fondo desenfocado + video completo al centro
    return (f"{tm}{st}split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,"
            f"eq=brightness=-0.08[bg];[b]scale={W}:-2,{GRADE}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            f"setsar=1,fps={FPS},format=yuv420p")


def musica():
    """Si hay pistas en Herramientas/musica (libres de derechos), elige una distinta cada día."""
    d = HERE / "musica"
    pistas = sorted(p for p in d.glob("*") if p.suffix.lower() in {".mp3", ".m4a", ".wav"}) if d.exists() else []
    return pistas[date.today().toordinal() % len(pistas)] if pistas else None


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    base = Path(args[0])
    fecha = date.today().isoformat()
    if "--fecha" in args:
        fecha = args[args.index("--fecha") + 1]
    dry = "--dry" in args
    entrada, editados, publicados = base / "1 Entrada", base / "2 Editados", base / "3 Publicados"
    clips = sorted([p for p in entrada.iterdir() if p.suffix.lower() in VIDEO_EXT and not p.name.startswith(".")],
                   key=lambda p: p.stat().st_mtime)
    if not clips:
        print(json.dumps({"estado": "sin_clips"})); return
    srv = servicio_de(clips[0].name)
    grupo = [p for p in clips if servicio_de(p.name) is srv][:6]
    info = [(p, *probe(p)) for p in grupo]
    per = max(4.0, MAX_TOTAL / len(info))
    editados.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="spa_"))
    partes, durs = [], []
    total = 0.0
    estabilizar = tiene_filtro("vidstabdetect") and tiene_filtro("vidstabtransform") and "--sin-estabilizar" not in args
    for i, (p, dur, w, h, has_a, hdr) in enumerate(info):
        start = min(0.5, dur * 0.1)
        ln = min(per, dur - start, MAX_TOTAL - total)
        if ln < 1.5:
            continue
        out = tmp / f"p{i}.mp4"
        trf = None
        if estabilizar and not dry:   # quita el temblor de la mano (2 pasadas)
            trf = tmp / f"p{i}.trf"
            try:
                sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{ln:.2f}", "-i", str(p),
                    "-vf", f"vidstabdetect=shakiness=5:accuracy=9:result={trf}", "-f", "null", "-"])
            except RuntimeError:
                trf = None
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{ln:.2f}", "-i", str(p)]
        if not has_a:
            cmd += ["-f", "lavfi", "-t", f"{ln:.2f}", "-i", "anullsrc=r=48000:cl=stereo"]
        cmd += ["-filter_complex", f"[0:v]{vf_clip(w, h, hdr, trf)}[v]", "-map", "[v]",
                "-map", "0:a" if has_a else "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(out)]
        if not dry:
            sh(cmd)
        partes.append(out); durs.append(ln); total += ln
    if not partes:
        print(json.dumps({"estado": "clips_muy_cortos"})); return

    logo_png(tmp / "logo.png")
    text_png(tmp / "titulo.png", [(srv[1], "CormorantGaramond.ttf", 96, GOLD),
                                  (srv[2], "Montserrat.ttf", 44, CREAM)])
    cierre_png(tmp / "cierre.png", srv)
    slug = re.sub(r"[^a-z0-9]+", "-", norm(srv[1])).strip("-")
    salida = editados / f"{fecha}_{slug}.mp4"
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    largo = sum(durs) - XF * (len(durs) - 1)          # duración del cuerpo con transiciones
    if not dry:
        sh(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(END), "-i", str(tmp / "cierre.png"),
            "-f", "lavfi", "-t", str(END), "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", f"fps={FPS},format=yuv420p,zoompan=z='min(zoom+0.0006,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}",
            *enc, "-shortest", str(tmp / "cierre.mp4")])
        # 1) clips unidos con fundidos suaves (video y audio)
        if len(partes) == 1:
            shutil.copy(partes[0], tmp / "cuerpo.mp4")
        else:
            ins, fv, fa, off = [], [], [], 0.0
            for p in partes:
                ins += ["-i", str(p)]
            pv, pa = "[0:v]", "[0:a]"
            for k in range(1, len(partes)):
                off += durs[k - 1] - XF
                fv.append(f"{pv}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]")
                fa.append(f"{pa}[{k}:a]acrossfade=d={XF}[a{k}]")
                pv, pa = f"[v{k}]", f"[a{k}]"
            sh(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fv + fa),
                "-map", pv, "-map", pa, *enc, str(tmp / "cuerpo.mp4")])
        # 2) logo fijo + título que entra y sale con fundido
        sh(["ffmpeg", "-y", "-v", "error", "-i", str(tmp / "cuerpo.mp4"),
            "-loop", "1", "-t", f"{largo:.2f}", "-i", str(tmp / "logo.png"),
            "-loop", "1", "-t", f"{largo:.2f}", "-i", str(tmp / "titulo.png"),
            "-filter_complex",
            "[2:v]format=rgba,fade=t=in:st=0.3:d=0.5:alpha=1,fade=t=out:st=4.0:d=0.5:alpha=1[t];"
            "[0:v][1:v]overlay=0:0:shortest=1[a];[a][t]overlay=0:0:shortest=1,format=yuv420p[v]",
            "-map", "[v]", "-map", "0:a", *enc, str(tmp / "cuerpo2.mp4")])
        # 3) cierre con fundido, música de fondo (si hay) y volumen nivelado para redes (-14 LUFS)
        fin = largo + END - XF
        ins = ["-i", str(tmp / "cuerpo2.mp4"), "-i", str(tmp / "cierre.mp4")]
        fc = (f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={largo - XF:.3f},format=yuv420p[v];"
              f"[0:a][1:a]acrossfade=d={XF}[voz]")
        pista = musica()
        if pista:
            ins += ["-stream_loop", "-1", "-i", str(pista)]
            fc += (f";[2:a]volume=0.12,afade=t=in:d=1,afade=t=out:st={fin - 1.5:.2f}:d=1.5[m];"
                   "[voz][m]amix=inputs=2:duration=first:normalize=0[mx];"
                   "[mx]loudnorm=I=-14:TP=-1.5:LRA=11[au]")
        else:
            fc += ";[voz]loudnorm=I=-14:TP=-1.5:LRA=11[au]"
        sh(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
            "-t", f"{fin:.2f}", *enc, "-movflags", "+faststart", str(salida)])
    total = largo
    texto = (f"{srv[1]} en Metabolic Spa CAX ✨ {srv[2]}.\n\n💛 {srv[3]}\n\n"
             f"📲 Agenda tu evaluación por WhatsApp: {WHATSAPP}\n📍 Cajamarca\n\n"
             f"#Cajamarca #SpaCajamarca #MetabolicSpaCAX {srv[4]}")
    meta = {"estado": "ok", "video": str(salida), "servicio": srv[1], "duracion": round(total + END, 1),
            "clips": [p.name for p in grupo], "texto": texto}
    if not dry:
        (salida.with_suffix(".json")).write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        dest = publicados / fecha; dest.mkdir(parents=True, exist_ok=True)
        for p in grupo:
            shutil.move(str(p), str(dest / p.name))
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()

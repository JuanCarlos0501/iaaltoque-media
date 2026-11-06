#!/usr/bin/env python3
"""Rutina diaria de Metabolic Spa CAX para videos ya grabados (o ya editados en el celular).

Se corre en el Mac, dentro de "Metabolic Spa - Videos/Herramientas". Cada comando dura < 3 min
(los 4K HEVC del iPhone se procesan por partes de 14 s para no pasar el límite de device_bash).

  python3 diario.py pendientes                       -> JSON con los videos de "1 Entrada"
  python3 diario.py partes  IMG_1.MOV                -> JSON con los inicios de cada parte
  python3 diario.py parte   IMG_1.MOV 14             -> convierte esa parte a 1080x1920 SDR
  python3 diario.py unir    IMG_1.MOV biolift        -> une partes + audio -16 LUFS + cierre con precio
                                                        => "2 Editados/<fecha>_<servicio>_<nombre>.mp4"
  python3 diario.py tomas   "2 Editados/x.mp4"      -> 14 tomas + hoja de contactos (para elegir)
  python3 diario.py historia biolift toma.jpg "Título" [--noche] -> historia 1080x1920 en "4 Estados WhatsApp"
  python3 diario.py post     biolift toma.jpg        -> post 1080x1350 en "2 Editados"
  python3 diario.py archivar IMG_1.MOV               -> mueve el original a "3 Publicados/<fecha>/"
"""
import json, subprocess, sys, shutil, datetime, glob
from pathlib import Path

H = Path(__file__).resolve().parent
BASE = H.parent
ENTRADA, EDITADOS, PUBLICADOS, ESTADOS = (BASE / "1 Entrada", BASE / "2 Editados",
                                          BASE / "3 Publicados", BASE / "4 Estados WhatsApp")
TMP = H / "_diario"
HOY = datetime.date.today().isoformat()
VF = ("scale=1080:1920:flags=bilinear,zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
      "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")
VF_SDR = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p,fps=30"
PARTE = 14


def sh(*a, out=False):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-800:])
    return r.stdout


def dur(f):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)))


def es_hdr(f):
    t = sh("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
           "-of", "csv=p=0", str(f))
    return any(x in t for x in ("arib-std-b67", "smpte2084"))


def entrada(nombre):
    p = Path(nombre)
    return p if p.is_absolute() else ENTRADA / p.name


def cmd_pendientes():
    vids = sorted(p.name for p in ENTRADA.iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
    print(json.dumps({"videos": vids, "duraciones": {v: round(dur(ENTRADA / v), 1) for v in vids}}))


def cmd_partes(nombre):
    d = dur(entrada(nombre))
    print(json.dumps({"partes": list(range(0, int(d) + 1, PARTE)) if d > PARTE else [0], "duracion": d}))


def cmd_parte(nombre, ini):
    f = entrada(nombre)
    TMP.mkdir(exist_ok=True)
    out = TMP / f"{f.stem}_p{int(ini):04d}.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", str(PARTE), "-i", str(f),
       "-vf", VF if es_hdr(f) else VF_SDR, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out))
    print(json.dumps({"parte": out.name}))


def cierre(servicio):
    r = json.loads(sh("python3", str(H / "produccion.py"), "estado", "--servicio", servicio))
    img = ESTADOS / r["imagen"]
    out = TMP / f"cierre_{servicio}.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "3", "-i", str(img), "-f", "lavfi", "-t", "3",
       "-i", "anullsrc=r=48000:cl=stereo", "-vf", "scale=1080:1920,format=yuv420p,fps=30,fade=t=in:d=0.4",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out))
    return out, r["texto"]


def cmd_unir(nombre, servicio):
    f = entrada(nombre)
    partes = sorted(TMP.glob(f"{f.stem}_p*.mp4"))
    lista = TMP / f"{f.stem}_v.txt"
    lista.write_text("".join(f"file '{p.name}'\n" for p in partes))
    v = TMP / f"{f.stem}_v.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(v))
    av = TMP / f"{f.stem}_av.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-i", str(v), "-i", str(f), "-map", "0:v", "-map", "1:a?",
       "-af", "loudnorm=I=-16:TP=-1.5,aresample=48000", "-ac", "2", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
       "-shortest", str(av))
    c, texto = cierre(servicio)
    l2 = TMP / f"{f.stem}_final.txt"
    l2.write_text(f"file '{av.name}'\nfile '{c.name}'\n")
    EDITADOS.mkdir(exist_ok=True)
    out = EDITADOS / f"{HOY}_{servicio}_{f.stem}.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(l2), "-c:v", "libx264", "-preset",
       "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out))
    out.with_suffix(".json").write_text(json.dumps({"video": out.name, "servicio": servicio, "texto": texto},
                                                   ensure_ascii=False, indent=1))
    for p in partes + [lista, v, av, l2]:
        p.unlink(missing_ok=True)
    print(json.dumps({"video": out.name, "duracion": round(dur(out), 1), "texto": texto}, ensure_ascii=False))


def cmd_tomas(video):
    from PIL import Image, ImageDraw
    v = Path(video) if Path(video).is_absolute() else BASE / video
    d = TMP / f"tomas_{v.stem}"
    d.mkdir(parents=True, exist_ok=True)
    total = dur(v) - 3.2  # sin el cierre
    ts = [round(total * (k + 0.5) / 14, 1) for k in range(14)]
    fs = []
    for t in ts:
        o = d / f"t{int(t * 10):04d}.jpg"
        sh("ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(v), "-frames:v", "1", "-q:v", "2", str(o))
        fs.append(o)
    hoja = Image.new("RGB", (180 * 7, 340 * 2), "white")
    dr = ImageDraw.Draw(hoja)
    for k, f in enumerate(fs):
        x, y = (k % 7) * 180, (k // 7) * 340
        hoja.paste(Image.open(f).resize((180, 320)), (x, y))
        dr.text((x + 4, y + 322), f.name, fill="black")
    hoja.save(d / "hoja.jpg")
    print(json.dumps({"carpeta": str(d.relative_to(BASE)), "hoja": "hoja.jpg", "tomas": [f.name for f in fs]}))


def _foto(p):
    p = Path(p)
    return str(p if p.is_absolute() else (BASE / p))


def cmd_historia(servicio, toma, titulo, *extra):
    args = ["python3", str(H / "produccion.py"), "estado", "--servicio", servicio, "--foto", _foto(toma),
            "--titulo", titulo] + (["--noche"] if "--noche" in extra else [])
    r = json.loads(sh(*args))
    src = ESTADOS / r["imagen"]
    n = len(glob.glob(str(ESTADOS / f"{HOY}_{servicio}_historia-*.jpg"))) + 1
    dst = ESTADOS / f"{HOY}_{servicio}_historia-{n}.jpg"
    src.rename(dst)
    print(json.dumps({"historia": str(dst.relative_to(BASE))}, ensure_ascii=False))


def cmd_post(servicio, toma):
    r = json.loads(sh("python3", str(H / "produccion.py"), "post", "--servicio", servicio, "--foto", _foto(toma)))
    print(json.dumps(r, ensure_ascii=False))


def cmd_archivar(nombre):
    f = entrada(nombre)
    d = PUBLICADOS / HOY
    d.mkdir(parents=True, exist_ok=True)
    shutil.move(str(f), str(d / f.name))
    print(json.dumps({"archivado": f"3 Publicados/{HOY}/{f.name}"}))


if __name__ == "__main__":
    c, *a = sys.argv[1:] or ["-h"]
    fn = globals().get(f"cmd_{c}")
    if not fn:
        sys.exit(__doc__)
    fn(*a)

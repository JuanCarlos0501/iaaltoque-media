#!/usr/bin/env python3
"""Editor de fotos de Metabolic Spa CAX (sin internet, sin créditos: solo Pillow).

Uso:  python3 fotos.py "<carpeta Metabolic Spa - Videos>" [--fecha AAAA-MM-DD] [--dry]

Toma las fotos de "1 Entrada" (jpg, jpeg, png, heic) del MISMO servicio (hasta 5), y por cada una:
  - corrige orientación, luz, contraste, color y nitidez de forma suave (piel natural);
  - arma un post 4:5 (1080x1350) con logo y franja de marca;
  - arma una historia 9:16 (1080x1920) con fondo desenfocado, servicio, precio y WhatsApp.
Guarda todo en "2 Editados" con un .json (servicio, texto, posts, historias) y mueve las
originales a "3 Publicados/<fecha>/". Los videos de "1 Entrada" no se tocan (los procesa editar.py).

El servicio se detecta por el nombre del archivo, igual que en editar.py
("dermadetox antes.jpg", "hydroglow cabina.heic").
"""
import json, re, shutil, subprocess, sys
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from editar import HERE, WHATSAPP, GOLD, INK, CREAM, servicio_de, font, norm  # noqa: E402

FOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif"}
MAX_FOTOS = 5
POST = (1080, 1350)
STORY = (1080, 1920)


def abrir(p):
    """Abre la foto; las HEIC del iPhone se convierten con pillow-heif o con sips (Mac)."""
    if p.suffix.lower() in (".heic", ".heif"):
        try:
            import pillow_heif  # type: ignore
            pillow_heif.register_heif_opener()
        except ImportError:
            tmp = p.with_suffix(".tmp.jpg")
            r = subprocess.run(["sips", "-s", "format", "jpeg", str(p), "--out", str(tmp)], capture_output=True)
            if r.returncode != 0:
                raise RuntimeError(f"No pude abrir {p.name}: falta pillow-heif o sips")
            im = Image.open(tmp); im.load(); tmp.unlink()
            return ImageOps.exif_transpose(im).convert("RGB")
    im = Image.open(p)
    return ImageOps.exif_transpose(im).convert("RGB")


def mejorar(im):
    """Retoque suave: balance de blancos ligero, luz, contraste, color y nitidez."""
    # balance de blancos tipo "gray world", solo al 50% para no dejar la piel gris
    r, g, b = ImageStat.Stat(im).mean
    m = (r + g + b) / 3
    fac = [1 + 0.5 * (m / c - 1) if c else 1 for c in (r, g, b)]
    ch = [c.point(lambda v, f=f: min(255, int(v * f))) for c, f in zip(im.split(), fac)]
    im = Image.merge("RGB", ch)
    im = ImageOps.autocontrast(im, cutoff=0.6)
    luz = ImageStat.Stat(im.convert("L")).mean[0]
    if luz < 115:                       # foto oscura de cabina
        im = ImageEnhance.Brightness(im).enhance(min(1.25, 125 / max(luz, 1)))
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    return im


def recorte(im, size, alto_foco=0.42):
    """Recorta al tamaño pedido sin deformar; el foco queda un poco arriba (donde suele estar el rostro)."""
    tw, th = size
    esc = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x = (im.width - tw) // 2
    y = int(min(max(im.height * alto_foco - th / 2, 0), im.height - th))
    return im.crop((x, y, x + tw, y + th))


def logo(size):
    lg = Image.open(HERE / "logo.png").convert("RGBA")
    lg.thumbnail((size, size))
    return lg


def centrado(d, t, fo, y, col, w):
    tw = d.textbbox((0, 0), t, font=fo)[2]
    d.text(((w - tw) / 2, y), t, font=fo, fill=col)


def post(im, srv):
    base = recorte(im, POST).convert("RGBA")
    capa = Image.new("RGBA", POST, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    # franja inferior de marca
    d.rectangle((0, POST[1] - 190, POST[0], POST[1]), fill=(*INK, 215))
    centrado(d, srv[1], font("CormorantGaramond.ttf", 70), POST[1] - 176, GOLD, POST[0])
    centrado(d, f"{srv[2]}  ·  {srv[3]}", font("Montserrat.ttf", 32), POST[1] - 92, CREAM, POST[0])
    base = Image.alpha_composite(base, capa)
    lg = logo(120)
    pad = Image.new("RGBA", (lg.width + 24, lg.height + 24), (*INK, 110))
    base.paste(pad, (36, 36), pad)
    base.paste(lg, (48, 48), lg)
    return base.convert("RGB")


def historia(im, srv):
    fondo = recorte(im, STORY).filter(ImageFilter.GaussianBlur(40))
    fondo = ImageEnhance.Brightness(fondo).enhance(0.55)
    foto = recorte(im, (960, 1200))
    m = Image.new("L", foto.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *foto.size), radius=36, fill=255)
    fondo.paste(foto, (60, 230), m)
    d = ImageDraw.Draw(fondo)
    lg = logo(130)
    fondo.paste(lg, ((STORY[0] - lg.width) // 2, 60), lg)
    centrado(d, srv[1], font("CormorantGaramond.ttf", 96), 1470, GOLD, STORY[0])
    centrado(d, srv[3], font("Montserrat.ttf", 50), 1600, CREAM, STORY[0])
    centrado(d, "Escríbenos por WhatsApp", font("Montserrat.ttf", 38), 1700, CREAM, STORY[0])
    centrado(d, WHATSAPP, font("Montserrat.ttf", 52), 1760, GOLD, STORY[0])
    return fondo


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    base = Path(args[0])
    fecha = args[args.index("--fecha") + 1] if "--fecha" in args else date.today().isoformat()
    dry = "--dry" in args
    entrada, editados, publicados = base / "1 Entrada", base / "2 Editados", base / "3 Publicados"
    fotos = sorted([p for p in entrada.iterdir() if p.suffix.lower() in FOTO_EXT and not p.name.startswith(".")],
                   key=lambda p: p.stat().st_mtime) if entrada.exists() else []
    if not fotos:
        print(json.dumps({"estado": "sin_fotos"})); return
    srv = servicio_de(fotos[0].name)
    grupo = [p for p in fotos if servicio_de(p.name) is srv][:MAX_FOTOS]
    slug = re.sub(r"[^a-z0-9]+", "-", norm(srv[1])).strip("-")
    editados.mkdir(parents=True, exist_ok=True)
    posts, historias = [], []
    for i, p in enumerate(grupo, 1):
        im = mejorar(abrir(p))
        sp = editados / f"{fecha}_{slug}_foto{i}_post.jpg"
        sh = editados / f"{fecha}_{slug}_foto{i}_historia.jpg"
        if not dry:
            post(im, srv).save(sp, quality=92, optimize=True)
            historia(im, srv).save(sh, quality=92, optimize=True)
        posts.append(str(sp)); historias.append(str(sh))
    texto = (f"{srv[1]} en Metabolic Spa CAX ✨ {srv[2]}.\n\n💛 {srv[3]}\n\n"
             f"📲 Agenda tu evaluación por WhatsApp: {WHATSAPP}\n📍 Cajamarca\n\n"
             f"#Cajamarca #SpaCajamarca #MetabolicSpaCAX {srv[4]}")
    meta = {"estado": "ok", "tipo": "fotos", "servicio": srv[1], "fotos": [p.name for p in grupo],
            "posts": posts, "historias": historias, "texto": texto}
    if not dry:
        (editados / f"{fecha}_{slug}_fotos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        dest = publicados / fecha; dest.mkdir(parents=True, exist_ok=True)
        for p in grupo:
            shutil.move(str(p), str(dest / p.name))
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()

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


def _curva(x):
    """Curva en S suave (contraste de revista sin quemar luces ni empastar sombras)."""
    t = x / 255.0
    return int(255 * (t + 0.10 * (t - 0.5) * (1 - abs(2 * t - 1)) * 2) + 0.5)


def mejorar(im):
    """Retoque profesional y natural: balance de blancos, luz sin quemar, curva en S,
    claridad local, piel algo más cálida, nitidez fina y viñeta muy sutil."""
    # 1) balance de blancos tipo "gray world" al 35% (la piel no se pone gris)
    r, g, b = ImageStat.Stat(im).mean
    m = (r + g + b) / 3
    fac = [1 + 0.35 * (m / c - 1) if c else 1 for c in (r, g, b)]
    im = Image.merge("RGB", [c.point(lambda v, f=f: min(255, int(v * f))) for c, f in zip(im.split(), fac)])
    # 2) niveles automáticos suaves
    im = ImageOps.autocontrast(im, cutoff=0.3, preserve_tone=True)
    # 3) foto oscura: subir medios tonos con gamma (las luces no se queman)
    luz = ImageStat.Stat(im.convert("L")).mean[0]
    if luz < 118:
        gam = max(0.72, min(1.0, luz / 130))
        lut = [int(255 * ((v / 255) ** gam) + 0.5) for v in range(256)]
        im = im.point(lut * 3)
    # 4) curva en S + calidez leve
    s_curve = [_curva(v) for v in range(256)]
    rr = [min(255, int(v * 1.02)) for v in s_curve]
    bb = [int(v * 0.98) for v in s_curve]
    im = im.point(rr + s_curve + bb)
    # 5) color, claridad local y nitidez fina
    im = ImageEnhance.Color(im).enhance(1.05)
    im = im.filter(ImageFilter.UnsharpMask(radius=30, percent=14, threshold=0))   # claridad
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=2))  # detalle
    # 6) viñeta muy sutil para llevar la mirada al centro
    w, h = im.size
    mask = Image.radial_gradient("L").resize((w, h)).point(lambda v: int(v * 0.35))
    im = Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), im, mask.filter(ImageFilter.GaussianBlur(w // 20)))
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


def degradado(size, alto, alfa=225):
    """Capa con degradado oscuro de marca en la parte inferior."""
    w, h = size
    capa = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for y in range(h - alto, h):
        a = int(alfa * ((y - (h - alto)) / alto) ** 1.4)
        d.line([(0, y), (w, y)], fill=(*INK, a))
    return capa


def espaciado(d, t, fo, y, col, w, track=6):
    """Texto centrado con espaciado entre letras (como la cabecera de los flyers)."""
    anchos = [d.textbbox((0, 0), ch, font=fo)[2] for ch in t]
    total = sum(anchos) + track * (len(t) - 1)
    x = (w - total) / 2
    for ch, aw in zip(t, anchos):
        d.text((x, y), ch, font=fo, fill=col)
        x += aw + track


def marca(base, srv, alto, y_nombre):
    w, h = base.size
    base = Image.alpha_composite(base, degradado(base.size, alto))
    d = ImageDraw.Draw(base)
    espaciado(d, "METABOLIC SPA CAX", font("Montserrat.ttf", 22), y_nombre - 44, GOLD, w, 7)
    centrado(d, srv[1], font("CormorantGaramond.ttf", 78), y_nombre, CREAM, w)
    d.line([((w - 120) / 2, y_nombre + 100), ((w + 120) / 2, y_nombre + 100)], fill=GOLD, width=3)
    centrado(d, srv[2], font("Montserrat.ttf", 30), y_nombre + 118, CREAM, w)
    centrado(d, srv[3], font("Montserrat.ttf", 40), y_nombre + 162, GOLD, w)
    return base


def post(im, srv):
    base = recorte(im, POST).convert("RGBA")
    base = marca(base, srv, 520, POST[1] - 280)
    lg = logo(110)
    base.paste(lg, (POST[0] - lg.width - 40, 40), lg)
    return base.convert("RGB")


def historia(im, srv):
    fondo = recorte(im, STORY).filter(ImageFilter.GaussianBlur(45))
    fondo = ImageEnhance.Brightness(fondo).enhance(0.45).convert("RGBA")
    foto = recorte(im, (940, 1175))
    m = Image.new("L", foto.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *foto.size), radius=40, fill=255)
    marco = Image.new("RGBA", (foto.width + 6, foto.height + 6), (0, 0, 0, 0))
    ImageDraw.Draw(marco).rounded_rectangle((0, 0, *marco.size), radius=43, outline=GOLD, width=3)
    fondo.paste(marco, (67, 207), marco)
    fondo.paste(foto, (70, 210), m)
    d = ImageDraw.Draw(fondo)
    lg = logo(120)
    fondo.paste(lg, ((STORY[0] - lg.width) // 2, 50), lg)
    centrado(d, srv[1], font("CormorantGaramond.ttf", 96), 1430, CREAM, STORY[0])
    d.line([((STORY[0] - 140) / 2, 1550), ((STORY[0] + 140) / 2, 1550)], fill=GOLD, width=3)
    centrado(d, srv[3], font("Montserrat.ttf", 50), 1580, GOLD, STORY[0])
    centrado(d, "Escríbenos por WhatsApp", font("Montserrat.ttf", 36), 1680, CREAM, STORY[0])
    centrado(d, WHATSAPP, font("Montserrat.ttf", 52), 1736, GOLD, STORY[0])
    return fondo.convert("RGB")


def etiqueta(img, texto, x, y):
    d = ImageDraw.Draw(img)
    fo = font("Montserrat.ttf", 30)
    tw = d.textbbox((0, 0), texto, font=fo)[2]
    d.rounded_rectangle((x, y, x + tw + 48, y + 58), radius=29, fill=(*INK, 220) if img.mode == "RGBA" else INK)
    d.text((x + 24, y + 12), texto, font=fo, fill=CREAM)


def antes_despues(antes, despues, srv):
    """Post 4:5 con ANTES y DESPUÉS lado a lado, misma escala y encuadre."""
    base = Image.new("RGBA", POST, (*INK, 255))
    mitad = ((POST[0] - 12) // 2, POST[1])
    a, b = recorte(antes, mitad).convert("RGBA"), recorte(despues, mitad).convert("RGBA")
    base.paste(a, (0, 0)); base.paste(b, (mitad[0] + 12, 0))
    ImageDraw.Draw(base).rectangle((mitad[0], 0, mitad[0] + 11, POST[1] - 360), fill=GOLD)
    base = marca(base, srv, 520, POST[1] - 280)
    etiqueta(base, "ANTES", 30, 40)
    etiqueta(base, "DESPUÉS", mitad[0] + 42, 40)
    return base.convert("RGB")


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
    antes = [p for p in grupo if "antes" in norm(p.name)]
    despues = [p for p in grupo if "despues" in norm(p.name)]
    if antes and despues:   # comparación profesional antes / después
        sa = editados / f"{fecha}_{slug}_antes-despues_post.jpg"
        if not dry:
            antes_despues(mejorar(abrir(antes[0])), mejorar(abrir(despues[0])), srv).save(sa, quality=92, optimize=True)
        posts.append(str(sa))
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

"""Posts (1080x1350) e historias (1080x1920) de la línea Sanendi para Metabolic Spa CAX."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps
sys.path.insert(0, "/home/claude/spa/stories")
import make as m

U = Path("/mnt/user-data/uploads"); OUT = Path("/home/claude/spa/sanendi/piezas"); OUT.mkdir(exist_ok=True)
F = lambda s, w=500: m.font("Montserrat[wght].ttf", s, w)
C = lambda s, w=700: m.font("CormorantGaramond[wght].ttf", s, w)
GOLD, CREAM, INK = (232, 196, 120), (250, 246, 238), (20, 14, 12)

P = {
    "ultra": dict(foto="dfcdf5df-image.jpg", col=(126, 86, 196), claro=(236, 226, 252), tag="ULTRA VOLUME-L",
                  tit="Volumen y contorno", items=["Da volumen a pómulos y mentón", "Define la línea mandibular",
                  "Restaura el volumen perdido", "Resultado natural"]),
    "light": dict(foto="296683f6-image.jpg", col=(214, 84, 132), claro=(252, 228, 238), tag="LIGHT-L",
                  tit="Corrección sutil", items=["Suaviza líneas finas", "Contorno de ojos y labios",
                  "Aporta hidratación y luminosidad", "Ideal para zonas delicadas"]),
    "deep": dict(foto="ea844c22-image.jpg", col=(58, 126, 200), claro=(226, 238, 252), tag="DEEP LINE-L",
                 tit="Líneas profundas", items=["Surcos nasolabiales", "Líneas de marioneta",
                 "Pliegues medios y profundos", "Rostro más descansado"]),
    "plla": dict(foto="56fb21c5-image.jpg", col=(150, 104, 40), claro=(248, 238, 220), tag="ÁCIDO POLI-L-LÁCTICO",
                 tit="Bioestimulador de colágeno", items=["Estimula tu propio colágeno", "Mejora la flacidez leve a moderada",
                 "Más firmeza de forma progresiva", "Resultados graduales y naturales"]),
}


def foto_crop(path, w, h):
    im = ImageOps.exif_transpose(Image.open(U / path)).convert("RGB")
    im = ImageOps.fit(im, (w, h), centering=(0.5, 0.42))
    from PIL import ImageEnhance
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.05)


def check(d, x, y, col):
    d.ellipse((x, y, x + 40, y + 40), fill=col)
    d.line((x + 10, y + 21, x + 18, y + 29, x + 31, y + 12), fill="white", width=5)


def pieza(k, W, H):
    p = P[k]; foto_h = int(H * (0.50 if H == 1350 else 0.47))
    img = Image.new("RGB", (W, H), CREAM)
    img.paste(foto_crop(p["foto"], W, foto_h), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # banda superior con logo
    for y in range(230):
        d.line((0, y, W, y), fill=(15, 10, 10, int(170 * (1 - y / 230))))
    lg = m.LOGO.copy(); lg.thumbnail((120, 120)); img.paste(lg, (50, 30), lg)
    d.text((184, 52), "METABOLIC SPA CAX", font=F(32, 700), fill=GOLD)
    d.text((184, 94), "Estética avanzada a tu alcance", font=F(26), fill=CREAM)
    tw = d.textbbox((0, 0), "NUEVO INGRESO", font=F(30, 700))[2]
    d.rounded_rectangle((W - tw - 96, 44, W - 44, 104), 30, fill=GOLD)
    d.text((W - tw - 70, 56), "NUEVO INGRESO", font=F(30, 700), fill=INK)
    # panel inferior
    y = foto_h - 40
    d.rounded_rectangle((0, y, W, H + 40), 46, fill=CREAM)
    d.rounded_rectangle((60, y + 50, 60 + d.textbbox((0, 0), p["tag"], font=F(32, 700))[2] + 56, y + 108), 29, fill=p["col"])
    d.text((88, y + 58), p["tag"], font=F(32, 700), fill="white")
    d.text((330 if False else W - 300, y + 60), "SANENDI®", font=F(34, 700), fill=p["col"])
    big = H > 1350; ts, isz, ilh = (104, 46, 92) if big else (84, 38, 62)
    yt = y + (150 if big else 130)
    for ln in m.wrap(d, p["tit"], C(ts), W - 120):
        d.text((60, yt), ln, font=C(ts), fill=INK); yt += int(ts * 1.05)
    yt += 30 if big else 18
    for it in p["items"]:
        check(d, 62, yt + (8 if big else 4), p["col"]); d.text((124, yt), it, font=F(isz, 500), fill=(60, 50, 44)); yt += ilh
    # pie
    fy = H - 150
    d.rectangle((0, fy, W, H), fill=INK)
    d.text((60, fy + 26), "Aplicación por médico · evaluación previa", font=F(28), fill=(230, 215, 200))
    d.text((60, fy + 70), "987 293 339 · 931 055 214", font=F(44, 700), fill=GOLD)
    d.text((W - 260, fy + 76), "Cajamarca", font=F(34, 600), fill=CREAM)
    return img


def portada(W, H):
    img = Image.new("RGB", (W, H), INK)
    g = Image.new("RGB", (W, H)); gd = ImageDraw.Draw(g)
    for (x, y, r, c) in [(200, 300, 380, (126, 86, 196)), (900, 700, 380, (214, 84, 132)), (300, 1100, 360, (58, 126, 200))]:
        gd.ellipse((x - r, y - r, x + r, y + r), fill=c)
    img = Image.blend(img, g.filter(ImageFilter.GaussianBlur(170)), 0.65)
    ph = foto_crop("dfcdf5df-image.jpg", W - 160, int((W - 160) * 0.62))
    msk = Image.new("L", ph.size, 0); ImageDraw.Draw(msk).rounded_rectangle((0, 0, *ph.size), 40, fill=255)
    top = 330 if H == 1350 else 520
    img.paste(ph, (80, top), msk); d = ImageDraw.Draw(img)
    lg = m.LOGO.copy(); lg.thumbnail((170, 170)); img.paste(lg, ((W - lg.width) // 2, 70 if H == 1350 else 160), lg)
    d = ImageDraw.Draw(img)
    y = top + ph.height + 50
    m.center(d, "NUEVO INGRESO EN CAJAMARCA", F(38, 700), y, GOLD)
    m.center(d, "Línea Sanendi", C(110), y + 60, CREAM)
    m.center(d, "Ácido hialurónico · Bioestimulador de colágeno", F(34), y + 190, (235, 222, 210))
    m.center(d, "987 293 339 · 931 055 214", F(48, 700), H - (110 if H == 1350 else 260), GOLD)
    if H > 1350:
        m.center(d, "Escríbenos y agenda tu evaluación", F(40), H - 340, CREAM)
    return img


if __name__ == "__main__":
    portada(1080, 1350).save(OUT / "post_0_portada.jpg", quality=93)
    portada(1080, 1920).save(OUT / "historia_0_portada.jpg", quality=93)
    for i, k in enumerate(["ultra", "light", "deep", "plla"], 1):
        pieza(k, 1080, 1350).save(OUT / f"post_{i}_{k}.jpg", quality=93)
        pieza(k, 1080, 1920).save(OUT / f"historia_{i}_{k}.jpg", quality=93)
    print(sorted(p.name for p in OUT.iterdir()))

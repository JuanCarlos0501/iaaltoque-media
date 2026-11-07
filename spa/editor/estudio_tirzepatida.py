"""Versión 2, más visual: degradado vino-rosa, 'células' luminosas, tarjetas de vidrio y dorado."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import make as m

OUT = Path("/home/claude/spa/estudio"); OUT.mkdir(exist_ok=True)
WINE, DEEP, ROSE, BLUSH = (120, 22, 58), (52, 8, 26), (226, 98, 142), (255, 214, 228)
GOLD = (232, 196, 120); CREAM = m.CREAM
F = lambda s, w=500: m.font("Montserrat[wght].ttf", s, w)
C = lambda s, w=700: m.font("CormorantGaramond[wght].ttf", s, w)


def fondo(W, H, seed=0):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = (x / W) * 0.35 + (y / H) * 0.65
            c = tuple(int(DEEP[i] + (WINE[i] - DEEP[i]) * (1 - abs(t - 0.55) * 1.4)) for i in range(3))
            for k in range(4):
                if x + k < W: px[x + k, y] = c
    glow = Image.new("RGB", (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    import random; r = random.Random(seed)
    for _ in range(9):  # "células" luminosas
        x, y, rad = r.randint(-100, W + 100), r.randint(0, H), r.randint(60, 220)
        col = r.choice([ROSE, (255, 150, 185), (200, 70, 120)])
        g.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 255)), 0.45)
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dots)
    for _ in range(70):
        x, y, s = r.randint(0, W), r.randint(0, H), r.choice([2, 3, 4, 6])
        dd.ellipse((x, y, x + s, y + s), fill=(255, 220, 230, r.randint(60, 170)))
    img.paste(dots, (0, 0), dots)
    return img


def vidrio(img, box, alpha=38, radio=34):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, radio, fill=(255, 255, 255, alpha), outline=(255, 210, 225, 110), width=2)
    img.paste(lay, (0, 0), lay)


def encabezado(img, d, W, n):
    lg = m.LOGO.copy(); lg.thumbnail((120, 120)); img.paste(lg, (60, 50), lg)
    d.text((196, 72), "METABOLIC SPA CAX", font=F(30, 600), fill=GOLD)
    d.text((196, 112), "Ciencia · Prevención · Bienestar", font=F(25), fill=BLUSH)
    t = f"{n}/3"; d.rounded_rectangle((W - 150, 70, W - 56, 126), 28, outline=GOLD, width=2)
    d.text((W - 128, 78), t, font=F(30, 600), fill=GOLD)


def lineas(d, x, y, w, txt, fo, col, lh):
    for ln in m.wrap(d, txt, fo, w):
        d.text((x, y), ln, font=fo, fill=col); y += lh
    return y


def lamina1(W, H):
    img = fondo(W, H, 1); d = ImageDraw.Draw(img); encabezado(img, d, W, 1)
    d.text((60, 250), "LO QUE DICE LA CIENCIA", font=F(32, 600), fill=ROSE)
    d.line((60, 300, 220, 300), fill=GOLD, width=3)
    y = lineas(d, 56, 320, W - 110, "Tirzepatida", C(150), CREAM, 150)
    y = lineas(d, 60, y, W - 110, "y cáncer de mama", C(92, 600), BLUSH, 96) + 30
    y = lineas(d, 60, y, W - 130, "Un estudio en ratones con obesidad observó que, además de bajar de peso, frenó el crecimiento de tumores de mama.", F(42), CREAM, 58)
    vidrio(img, (60, y + 40, W - 60, y + 200)); d = ImageDraw.Draw(img)
    d.text((100, y + 66), "Hallazgo temprano", font=F(40, 700), fill=GOLD)
    d.text((100, y + 120), "Aún no está probado en personas.", font=F(38, 500), fill=CREAM)
    d.text((60, H - 90), "Desliza para saber más  →", font=F(32, 600), fill=BLUSH)
    return img


def lamina2(W, H):
    img = fondo(W, H, 2); d = ImageDraw.Draw(img); encabezado(img, d, W, 2)
    y = lineas(d, 56, 220, W - 110, "¿Qué encontraron?", C(110), CREAM, 112) + 30
    items = [("Peso y metabolismo", "Bajaron de peso y mejoraron las hormonas que la obesidad altera."),
             ("Tumores más pequeños", "Los tumores de mama crecieron menos que sin tratamiento."),
             ("La dieta también cuenta", "Reducir calorías de forma sostenida logró un efecto aún mayor.")]
    for i, (t, b) in enumerate(items, 1):
        vidrio(img, (60, y, W - 60, y + 230)); d = ImageDraw.Draw(img)
        d.ellipse((90, y + 30, 170, y + 110), fill=GOLD)
        d.text((116, y + 28), str(i), font=C(64), fill=DEEP)
        d.text((200, y + 34), t, font=F(42, 700), fill=CREAM)
        lineas(d, 200, y + 96, W - 300, b, F(36), BLUSH, 50)
        y += 260
    lineas(d, 60, H - 120, W - 120, "Fuente: Glenny E. et al., University of North Carolina at Chapel Hill · bioRxiv, 23 ene 2024 (preprint en ratones, sin revisión por pares).", F(24), BLUSH, 32)
    return img


def lamina3(W, H):
    img = fondo(W, H, 3); d = ImageDraw.Draw(img); encabezado(img, d, W, 3)
    y = lineas(d, 56, 220, W - 110, "¿Qué significa para ti?", C(96), CREAM, 100) + 24
    pts = ["El exceso de peso es un factor de riesgo de cáncer de mama.",
           "Ya hay estudios en mujeres (como TRIM-EBC) para confirmarlo.",
           "Hoy la tirzepatida NO se usa para prevenir ni tratar el cáncer de mama; siempre la indica un médico.",
           "Cuidar tu peso y tu metabolismo sí suma a tu salud."]
    for p in pts:
        d.ellipse((66, y + 16, 88, y + 38), fill=GOLD)
        y = lineas(d, 112, y, W - 180, p, F(38), CREAM, 52) + 22
    vidrio(img, (60, y + 16, W - 60, y + 230), alpha=60); d = ImageDraw.Draw(img)
    d.text((100, y + 44), "Evaluación metabólica con la", font=F(34), fill=BLUSH)
    d.text((100, y + 86), "Dra. Winifer González", font=C(60), fill=CREAM)
    d.text((100, y + 158), "987 293 339 · 931 055 214", font=F(46, 700), fill=GOLD)
    lineas(d, 60, H - 84, W - 120, "Información educativa. No reemplaza la consulta médica ni tu control mamario.", F(25), BLUSH, 32)
    return img


def historia(fn):
    st = fondo(1080, 1920, 9); card = fn(1080, 1350).resize((1000, 1250))
    msk = Image.new("L", card.size, 0); ImageDraw.Draw(msk).rounded_rectangle((0, 0, *card.size), 40, fill=255)
    st.paste(card, (40, 320), msk); d = ImageDraw.Draw(st)
    m.center(d, "METABOLIC SPA CAX", F(42, 600), 200, GOLD)
    m.center(d, "Escríbenos por WhatsApp", F(38), 1620, BLUSH)
    m.center(d, "987 293 339 · 931 055 214", F(54, 700), 1680, GOLD)
    return st


if __name__ == "__main__":
    for i, fn in enumerate((lamina1, lamina2, lamina3), 1):
        fn(1080, 1350).save(OUT / f"post_{i}.jpg", quality=93)
        historia(fn).save(OUT / f"historia_{i}.jpg", quality=93)
    print("ok")

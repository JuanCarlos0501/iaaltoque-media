"""Historia 1080x1920: sorteo VIP (rinomodelación + aumento de labios gratis) para Metabolic Spa CAX."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else D.parent / "historias" / "sorteo_vip.jpg"
W, H = 1080, 1920
GOLD, CREAM, INK = (212, 170, 80), (250, 246, 238), (20, 14, 12)
LOGO = Image.open(D / "logo.png").convert("RGBA")


def F(s, w=500):
    f = ImageFont.truetype(str(D / "fonts" / "Montserrat.ttf"), s)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


def C(s, w=700):
    f = ImageFont.truetype(str(D / "fonts" / "CormorantGaramond.ttf"), s)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


def center(d, t, fo, y, col):
    w = d.textbbox((0, 0), t, font=fo)[2]
    d.text(((W - w) // 2, y), t, font=fo, fill=col)
    return y + d.textbbox((0, 0), t, font=fo)[3]


# fondo: negro con brillos dorados suaves
img = Image.new("RGB", (W, H), INK)
g = Image.new("RGB", (W, H), INK); gd = ImageDraw.Draw(g)
for (x, y, r, c) in [(150, 250, 420, (120, 90, 30)), (980, 900, 380, (90, 60, 20)), (200, 1650, 420, (110, 80, 30))]:
    gd.ellipse((x - r, y - r, x + r, y + r), fill=c)
img = Image.blend(img, g.filter(ImageFilter.GaussianBlur(200)), 0.7)
d = ImageDraw.Draw(img, "RGBA")

# marco fino dorado
d.rounded_rectangle((44, 250, W - 44, H - 440), 36, outline=(*GOLD, 160), width=3)

# logo
lg = LOGO.copy(); lg.thumbnail((300, 300)); img.paste(lg, ((W - lg.width) // 2, 300), lg)
d = ImageDraw.Draw(img, "RGBA")

# cinta "SORTEO VIP"
y = 640
tw = d.textbbox((0, 0), "SORTEO EXCLUSIVO VIP", font=F(36, 700))[2]
d.rounded_rectangle(((W - tw) // 2 - 36, y, (W + tw) // 2 + 36, y + 70), 35, fill=GOLD)
d.text(((W - tw) // 2, y + 15), "SORTEO EXCLUSIVO VIP", font=F(36, 700), fill=INK)

# premio
y = center(d, "Rinomodelación", C(124), 750, CREAM)
y = center(d, "+", F(64, 300), y + 2, GOLD)
y = center(d, "Aumento de labios", C(124), y + 4, CREAM)
y = center(d, "TOTALMENTE GRATIS", F(54, 800), y + 26, GOLD)

# separador
d.line((W // 2 - 140, y + 46, W // 2 + 140, y + 46), fill=(*GOLD, 180), width=2)

# condiciones
y = center(d, "Participan todas nuestras clientas y clientes", F(34), y + 90, CREAM)
y = center(d, "VIP con membresía activa", F(38, 700), y + 10, GOLD)
y = center(d, "Entras automáticamente, sin hacer nada más", F(30), y + 22, (225, 212, 195))

# fecha
y = center(d, "Muy pronto anunciamos la fecha del sorteo", F(32, 600), y + 44, CREAM)

# pie
center(d, "¿Aún no eres VIP? Pregunta por tu membresía", F(32), H - 400, (225, 212, 195))
center(d, "987 293 339 · 931 055 214", F(48, 700), H - 345, GOLD)
center(d, "Metabolic Spa CAX · Cajamarca", F(30, 600), H - 270, CREAM)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, quality=94)
print(OUT)

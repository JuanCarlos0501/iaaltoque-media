"""Historias 1080x1920 de Metabolic Spa CAX (PIL)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).parent / "out"; OUT.mkdir(exist_ok=True)
FL = Path("/home/claude/spa/out")
F = "/root/.fonts/"
W, H = 1080, 1920
INK, CREAM, GOLD, GOLD2, SOFT = (21, 17, 13), (250, 246, 238), (217, 182, 110), (138, 100, 32), (216, 207, 192)
LOGO = Image.open("/home/claude/spa/assets/logo.png").convert("RGBA")


def font(name, size, w=600):
    f = ImageFont.truetype(F + name, size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


def center(d, t, fo, y, col):
    tw = d.textbbox((0, 0), t, font=fo)[2]
    d.text(((W - tw) / 2, y), t, font=fo, fill=col)


def wrap(d, text, fo, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textbbox((0, 0), t, font=fo)[2] <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def logo(img, y, size):
    lg = LOGO.copy(); lg.thumbnail((size, size)); img.paste(lg, ((W - lg.width) // 2, y), lg)


def cta(d, y, dark=True):
    col = CREAM if dark else INK
    center(d, "Escríbenos por WhatsApp", font("Montserrat[wght].ttf", 44, 500), y, col)
    center(d, "987 293 339 · 931 055 214", font("Montserrat[wght].ttf", 60, 700), y + 66, GOLD if dark else GOLD2)


def flyer_story(name, out):
    fl = Image.open(FL / f"{name}.png").convert("RGB")
    bg = fl.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), INK), 0.55)
    card = fl.resize((960, 1200))
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *card.size), 36, fill=255)
    bg.paste(card, (60, 300), m)
    d = ImageDraw.Draw(bg)
    center(d, "HOY EN METABOLIC SPA CAX", font("Montserrat[wght].ttf", 40, 600), 200, GOLD)
    cta(d, 1580)
    bg.save(out, quality=92)


TIPS = [
    ("Protector solar, todos los días", "En Cajamarca, por la altura, el sol pega más fuerte. Úsalo aunque esté nublado y renuévalo cada 2–3 horas."),
    ("Nunca duermas maquillada", "Desmaquíllate y limpia tu rostro cada noche. Tu piel se renueva mientras duermes."),
    ("Toma agua", "Una buena hidratación también se nota en la piel. Lleva tu botella contigo."),
    ("Exfolia con medida", "Una o dos veces por semana es suficiente. Exfoliar a diario puede irritar la piel."),
    ("No revientes los granitos", "Pueden dejar manchas y marcas. Mejor una limpieza profunda con profesionales."),
    ("Cambia tu funda de almohada", "Una vez por semana. Acumula grasa y bacterias que llegan a tu rostro."),
]


def tip_story(i, title, body, out):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    logo(img, 150, 170)
    center(d, "CONSEJO DE PIEL", font("Montserrat[wght].ttf", 40, 600), 420, GOLD2)
    center(d, f"#{i}", font("CormorantGaramond[wght].ttf", 120, 600), 480, GOLD2)
    ft = font("CormorantGaramond[wght].ttf", 104, 700)
    y = 680
    for ln in wrap(d, title, ft, 920):
        center(d, ln, ft, y, INK); y += 116
    y += 40
    fb = font("Montserrat[wght].ttf", 46, 500)
    for ln in wrap(d, body, fb, 880):
        center(d, ln, fb, y, (74, 63, 53)); y += 66
    d.rounded_rectangle((90, 1500, W - 90, 1760), 32, fill=INK)
    center(d, "¿Quieres cuidar tu piel con profesionales?", font("Montserrat[wght].ttf", 38, 500), 1540, CREAM)
    center(d, "987 293 339 · 931 055 214", font("Montserrat[wght].ttf", 60, 700), 1610, GOLD)
    center(d, "Escríbenos por WhatsApp", font("Montserrat[wght].ttf", 36, 500), 1690, SOFT)
    img.save(out, quality=92)


def cta_story(variant, out):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    logo(img, 330, 380)
    t1, t2 = (("¿Lista para tu cambio?", "Agenda tu evaluación hoy"), ("Tu mejor versión", "empieza con una cita"))[variant]
    center(d, t1, font("CormorantGaramond[wght].ttf", 110, 700), 860, GOLD)
    center(d, t2, font("Montserrat[wght].ttf", 52, 500), 1010, CREAM)
    center(d, "Faciales · Exonucell X · Bio-Lift · Botox · Corporal", font("Montserrat[wght].ttf", 34, 500), 1130, SOFT)
    cta(d, 1330)
    center(d, "Cajamarca", font("Montserrat[wght].ttf", 40, 500), 1520, SOFT)
    img.save(out, quality=92)


if __name__ == "__main__":
    for n in ["Main", "MenuFacial", "BioLift", "Lipoescultor", "Botox", "PdrnPrp"]:
        flyer_story(n, OUT / f"flyer_{n}.jpg")
    for i, (t, b) in enumerate(TIPS, 1):
        tip_story(i, t, b, OUT / f"tip_{i}.jpg")
    cta_story(0, OUT / "cta_0.jpg"); cta_story(1, OUT / "cta_1.jpg")
    print(sorted(p.name for p in OUT.iterdir()))

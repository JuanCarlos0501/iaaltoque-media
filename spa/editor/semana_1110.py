"""Piezas nuevas Metabolic Spa CAX, semana 10-15 nov 2026.
Formato nuevo (bloques de color, test, checklist, este-o-este) para reemplazar los posts repetidos.
Uso: python3 spa/editor/semana_1110.py  -> spa/semana_1110/*.jpg
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).parent
OUT = HERE.parent / "semana_1110"; OUT.mkdir(exist_ok=True)
W, H = 1080, 1350
INK, CREAM, GOLD, GOLD2 = (24, 19, 15), (250, 246, 238), (217, 182, 110), (138, 100, 32)
SAGE, SAGE_D = (220, 228, 214), (46, 66, 56)
LOGO = Image.open(HERE / "logo.png").convert("RGBA")
WA = "987 293 339 · 931 055 214"

SERV = {  # color de acento por servicio
    "A": dict(n="Dermadetox", p="S/ 70", d="Limpieza facial profunda", col=(47, 110, 112), claro=(219, 236, 234),
              sintoma="Poros abiertos, puntos negros o granitos"),
    "B": dict(n="Hydroglow", p="S/ 89", d="Hidrofacial avanzado", col=(52, 116, 170), claro=(222, 234, 246),
              sintoma="Piel reseca o tirante por el frío y el sol"),
    "C": dict(n="Dermasweep", p="S/ 99", d="Exfoliación y renovación", col=(186, 104, 72), claro=(248, 230, 220),
              sintoma="Piel áspera, opaca o sin brillo"),
    "D": dict(n="Radiance C-Matrix", p="S/ 99", d="Aclarante, tono más uniforme", col=(176, 128, 36), claro=(248, 236, 206),
              sintoma="Manchas o tono disparejo"),
}
DERMAPEN = dict(n="Dermapen con PDRN", p="S/ 175", d="Regeneración y textura", col=(160, 70, 104), claro=(246, 224, 232))


def font(kind, size, w=600):
    f = ImageFont.truetype(str(HERE / "fonts" / ("Montserrat.ttf" if kind == "m" else "CormorantGaramond.ttf")), size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


M = lambda s, w=500: font("m", s, w)
C = lambda s, w=700: font("c", s, w)


def tw(d, t, fo): return d.textbbox((0, 0), t, font=fo)[2]


def ctr(d, t, fo, y, col, x0=0, x1=W):
    d.text((x0 + (x1 - x0 - tw(d, t, fo)) / 2, y), t, font=fo, fill=col)


def wrap(d, text, fo, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(d, t, fo) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def lines(d, text, fo, x, y, maxw, col, lh, center=False):
    for ln in wrap(d, text, fo, maxw):
        if center: ctr(d, ln, fo, y, col, x, x + maxw)
        else: d.text((x, y), ln, font=fo, fill=col)
        y += lh
    return y


def header(img, d, dark=False, tag=None, tagcol=GOLD):
    lg = LOGO.copy(); lg.thumbnail((92, 92)); img.paste(lg, (60, 46), lg)
    d.text((166, 66), "METABOLIC SPA CAX", font=M(26, 700), fill=GOLD if dark else GOLD2)
    d.text((166, 100), "Cajamarca", font=M(24), fill=CREAM if dark else (90, 78, 66))
    if tag:
        f = M(26, 700); w = tw(d, tag, f)
        d.rounded_rectangle((W - w - 108, 58, W - 60, 112), 27, fill=tagcol)
        d.text((W - w - 84, 70), tag, font=f, fill=INK if tagcol == GOLD else CREAM)


def footer(d, dark=False, txt="Escríbenos por WhatsApp"):
    col = CREAM if dark else INK
    d.line((60, H - 150, W - 60, H - 150), fill=GOLD if dark else (220, 208, 188), width=2)
    d.text((60, H - 122), txt, font=M(28), fill=col)
    d.text((60, H - 82), WA, font=M(38, 700), fill=GOLD if dark else GOLD2)


def swipe(d, col, y=H - 120):
    t = "Desliza"; f = M(28, 600); x = W - 60 - tw(d, t, f) - 60
    d.text((x, y), t, font=f, fill=col)
    ax = W - 100; d.line((ax, y + 18, ax + 36, y + 18), fill=col, width=4)
    d.polygon([(ax + 40, y + 18), (ax + 26, y + 8), (ax + 26, y + 28)], fill=col)


def badge(d, x, y, r, letra, col, txtcol=CREAM, size=None):
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    f = M(size or int(r * 1.1), 800); w = tw(d, letra, f)
    bb = d.textbbox((0, 0), letra, font=f)
    d.text((x - w / 2, y - (bb[3] + bb[1]) / 2), letra, font=f, fill=txtcol)


def check(d, x, y, col, s=44, on=False):
    d.rounded_rectangle((x, y, x + s, y + s), 10, outline=col, width=4, fill=col if on else None)
    if on: d.line((x + 10, y + 23, x + 19, y + 32, x + 34, y + 13), fill=CREAM, width=5)


def save(img, name): img.save(OUT / name, quality=92); return name


# ---------- A. Test "¿Qué facial necesita tu piel?" (carrusel 6) ----------
def test_carrusel():
    out = []
    img = Image.new("RGB", (W, H), SAGE_D); d = ImageDraw.Draw(img)
    header(img, d, dark=True, tag="TEST DE 10 SEGUNDOS")
    d.text((60, 250), "¿Qué facial", font=C(150), fill=CREAM)
    d.text((60, 400), "necesita", font=C(150), fill=CREAM)
    d.text((60, 550), "tu piel?", font=C(150, 700), fill=GOLD)
    y = lines(d, "Elige la letra que más se parece a ti y coméntala. Te decimos cómo empezar.", M(38), 60, 760, 900, CREAM, 54)
    for i, k in enumerate("ABCD"):
        badge(d, 130 + i * 140, 1010, 52, k, SERV[k]["col"])
    swipe(d, GOLD, H - 130)
    d.text((60, H - 130), "Primera visita desde S/ 70", font=M(30, 600), fill=GOLD)
    out.append(save(img, "A1_test_portada.jpg"))
    for i, k in enumerate("ABCD", 2):
        s = SERV[k]
        img = Image.new("RGB", (W, H), s["claro"]); d = ImageDraw.Draw(img)
        header(img, d, tag=f"{i - 1} DE 4", tagcol=s["col"])
        badge(d, 200, 360, 120, k, s["col"])
        d.text((360, 270), "SI TU PIEL TIENE…", font=M(30, 700), fill=s["col"])
        lines(d, s["sintoma"], C(64, 700), 360, 320, 660, INK, 70)
        d.rounded_rectangle((60, 560, W - 60, 1130), 40, fill=CREAM)
        d.text((110, 610), "TU FACIAL ES", font=M(30, 700), fill=s["col"])
        y = lines(d, s["n"], C(110, 700), 110, 655, 860, INK, 112)
        d.text((110, y + 40), s["d"], font=M(36), fill=(90, 78, 66))
        d.text((110, 960), "Primera visita", font=M(30), fill=(90, 78, 66))
        d.text((110, 990), s["p"], font=C(88, 700), fill=s["col"])
        f = M(40, 700); t = f"Comenta  {k}"; w = tw(d, t, f)
        d.rounded_rectangle((W - 110 - w - 70, 1000, W - 110, 1080), 40, fill=s["col"])
        d.text((W - 110 - w - 35, 1016), t, font=f, fill=CREAM)
        footer(d) if i == 5 else swipe(d, s["col"], 1220)
        if i != 5: d.text((60, 1220), "Metabolic Spa CAX · Cajamarca", font=M(28), fill=(90, 78, 66))
        out.append(save(img, f"A{i}_test_{k}.jpg"))
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    header(img, d, dark=True)
    ctr(d, "¿Cuál fue tu letra?", C(110), 300, CREAM)
    for i, k in enumerate("ABCD"):
        badge(d, 255 + i * 190, 560, 70, k, SERV[k]["col"])
    lines(d, "Escríbela en los comentarios o mándanos un WhatsApp con tu letra. La Dra. Winifer te dice por dónde empezar.",
          M(40), 110, 720, 860, CREAM, 58, center=True)
    footer(d, dark=True, txt="Separa tu primera visita")
    out.append(save(img, "A6_test_cierre.jpg"))
    return out


# ---------- B. Piel cajamarquina: sol de altura + frío (carrusel 3) ----------
def cajamarca_carrusel():
    out = []
    img = Image.new("RGB", (W, H), (236, 214, 176)); d = ImageDraw.Draw(img)
    # sol + montañas simples
    d.ellipse((620, 170, 960, 510), fill=(240, 170, 70))
    d.polygon([(0, 760), (260, 470), (470, 700), (700, 420), (1080, 780), (1080, 900), (0, 900)], fill=(120, 140, 110))
    d.polygon([(0, 900), (330, 640), (620, 860), (860, 680), (1080, 860), (1080, 1350), (0, 1350)], fill=SAGE_D)
    header(img, d, tag="PIEL CAJAMARQUINA", tagcol=SAGE_D)
    d.text((60, 920), "Sol de altura", font=C(112, 700), fill=CREAM)
    d.text((60, 1035), "+ frío seco", font=C(112, 700), fill=GOLD)
    d.text((60, 1170), "Lo que tu piel vive en Cajamarca", font=M(36, 500), fill=CREAM)
    swipe(d, GOLD, 1250)
    out.append(save(img, "B1_cajamarca_portada.jpg"))
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); header(img, d)
    d.text((60, 200), "Lo que vemos en cabina", font=C(84, 700), fill=INK)
    items = [("Sol fuerte todo el año", "A más de 2,700 m la radiación UV llega a niveles extremos. Aparecen manchas y tono disparejo.", SERV["D"]),
             ("Frío y aire seco", "La piel se reseca, se pone tirante y pierde brillo.", SERV["B"]),
             ("Polvo y contaminación", "Se tapan los poros: puntos negros y granitos.", SERV["A"])]
    y = 340
    for t, b, s in items:
        d.rounded_rectangle((60, y, W - 60, y + 250), 32, fill=s["claro"])
        d.rounded_rectangle((60, y, 84, y + 250), 12, fill=s["col"])
        d.text((120, y + 34), t, font=M(40, 700), fill=INK)
        lines(d, b, M(32), 120, y + 94, 780, (74, 63, 53), 44)
        d.text((W - 110 - tw(d, s["n"], M(26, 700)), y + 200), s["n"], font=M(26, 700), fill=s["col"])
        y += 280
    swipe(d, GOLD2, 1220)
    out.append(save(img, "B2_cajamarca_problemas.jpg"))
    img = Image.new("RGB", (W, H), SAGE_D); d = ImageDraw.Draw(img); header(img, d, dark=True)
    d.text((60, 220), "Cuéntanos", font=C(120, 700), fill=CREAM)
    d.text((60, 350), "en los comentarios", font=C(84), fill=GOLD)
    for i, (q, a) in enumerate([("¿De qué barrio nos escribes?", "Queremos conocerte"),
                                 ("¿Qué te afecta más?", "Sol · Frío · Polvo")]):
        yy = 560 + i * 230
        d.rounded_rectangle((60, yy, W - 60, yy + 190), 30, outline=GOLD, width=3)
        d.text((110, yy + 40), q, font=M(42, 700), fill=CREAM)
        d.text((110, yy + 108), a, font=M(34), fill=GOLD)
    d.text((60, 1060), "Primera visita: Dermadetox S/ 70 · Hydroglow S/ 89", font=M(30, 600), fill=CREAM)
    footer(d, dark=True)
    out.append(save(img, "B3_cajamarca_comenta.jpg"))
    return out


# ---------- C. Bio-Lift: antes/después en formato "nota tú el cambio" ----------
def biolift_carrusel():
    src = Image.open(HERE.parent / "flyers" / "biolift.jpg").convert("RGB")
    antes = src.crop((80, 385, 530, 745)); despues = src.crop((550, 385, 1000, 745))
    out = []
    for n, (foto, lab, col) in enumerate([(antes, "ANTES", INK), (despues, "DESPUÉS", GOLD2)], 1):
        img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
        f = ImageOps.fit(foto, (W, 1000), centering=(0.5, 0.45))
        img.paste(f, (0, 0)); d = ImageDraw.Draw(img, "RGBA")
        d.rectangle((0, 0, W, 170), fill=(20, 15, 12, 170)); header(img, d, dark=True, tag="BIO-LIFT FACIAL")
        d.rounded_rectangle((60, 900, 60 + tw(d, lab, M(40, 800)) + 64, 970), 35, fill=col)
        d.text((92, 912), lab, font=M(40, 800), fill=CREAM)
        if n == 1:
            d.text((60, 1040), "Mira bien esta foto…", font=C(84, 700), fill=CREAM)
            d.text((60, 1150), "y desliza para ver el después", font=M(36), fill=GOLD)
            swipe(d, GOLD, 1250)
        else:
            d.text((60, 1030), "¿Qué cambio notas primero?", font=C(70, 700), fill=CREAM)
            for i, o in enumerate(["1 Luminosidad", "2 Textura", "3 Manchas"]):
                x = 60 + i * 330
                d.rounded_rectangle((x, 1130, x + 300, 1200), 35, outline=GOLD, width=3)
                ctr(d, o, M(32, 600), 1146, CREAM, x, x + 300)
            d.text((60, 1250), "Comenta tu número · Paciente real de Metabolic Spa CAX", font=M(26), fill=(200, 190, 175))
        out.append(save(img, f"C{n}_biolift_{lab.lower().replace('é', 'e')}.jpg"))
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); header(img, d)
    d.text((60, 220), "Bio-Lift Facial", font=C(120, 700), fill=INK)
    d.text((60, 360), "Lo que lleva cada sesión", font=M(36, 600), fill=GOLD2)
    pasos = ["Limpieza profunda y vapor", "Ultrasonido", "Dermapen con PDRN y GHK-Cu", "Masaje y nutrición", "Luz LED"]
    for i, p in enumerate(pasos):
        y = 460 + i * 105
        badge(d, 110, y + 30, 32, str(i + 1), GOLD2, size=34)
        d.text((170, y + 8), p, font=M(40, 600), fill=INK)
    d.rounded_rectangle((60, 1010, W - 60, 1160), 32, fill=INK)
    d.text((110, 1040), "Paquete de 4 sesiones", font=M(32), fill=CREAM)
    d.text((110, 1080), "S/ 1,500", font=C(72, 700), fill=GOLD)
    d.text((560, 1062), "S/ 375 por sesión", font=M(34, 600), fill=CREAM)
    footer(d)
    out.append(save(img, "C3_biolift_sesion.jpg"))
    return out


# ---------- D. Checklist Dermadetox ----------
def checklist_post():
    s = SERV["A"]; img = Image.new("RGB", (W, H), s["claro"]); d = ImageDraw.Draw(img)
    header(img, d, tag="¿CUÁNTAS TIENES?", tagcol=s["col"])
    d.text((60, 200), "Si marcas 2 o más,", font=C(84, 700), fill=INK)
    d.text((60, 295), "te toca una limpieza", font=C(84, 700), fill=s["col"])
    items = ["Puntos negros en la nariz", "Poros que se notan", "Granitos que van y vienen",
             "Piel opaca o cansada", "Usas maquillaje casi a diario", "Hace más de 3 meses que no te haces una"]
    for i, t in enumerate(items):
        y = 450 + i * 98
        check(d, 80, y, s["col"], on=i in (0, 1))
        d.text((150, y + 2), t, font=M(38, 500), fill=INK)
    d.rounded_rectangle((60, 1060, W - 60, 1190), 34, fill=s["col"])
    d.text((100, 1080), "Dermadetox · limpieza facial profunda", font=M(30, 600), fill=CREAM)
    d.text((100, 1120), "Primera visita S/ 70", font=M(44, 800), fill=CREAM)
    t = "Comenta cuántas"; d.text((W - 100 - tw(d, t, M(30, 700)), 1138), t, font=M(30, 700), fill=GOLD)
    d.text((60, 1240), WA, font=M(36, 700), fill=INK)
    d.text((W - 60 - tw(d, "Cajamarca", M(28)), 1246), "Cajamarca", font=M(28), fill=(90, 78, 66))
    return [save(img, "D_dermadetox_checklist.jpg")]


# ---------- E. Botox en pareja: etiqueta a tu compañera ----------
def botox_post():
    img = Image.new("RGB", (W, H), (44, 30, 40)); d = ImageDraw.Draw(img)
    header(img, d, dark=True, tag="VEN CON ALGUIEN")
    d.text((60, 210), "Etiqueta a quien", font=C(108, 700), fill=CREAM)
    d.text((60, 330), "vendría contigo", font=C(108, 700), fill=GOLD)
    for i, (who, x) in enumerate([("TÚ", 290), ("ELLA / ÉL", 790)]):
        d.ellipse((x - 170, 520, x + 170, 860), outline=GOLD, width=5)
        d.ellipse((x - 60, 590, x + 60, 710), fill=GOLD)
        d.pieslice((x - 120, 720, x + 120, 960), 180, 360, fill=GOLD)
        ctr(d, who, M(34, 700), 880, CREAM, x - 170, x + 170)
    ctr(d, "+", M(110, 300), 600, GOLD)
    d.text((60, 990), "Botox full face, aplicado por médico", font=M(34, 600), fill=CREAM)
    d.text((60, 1040), "S/ 750 c/u", font=C(100, 700), fill=GOLD)
    d.text((520, 1080), "en pareja o con tu amiga", font=M(32), fill=CREAM)
    d.text((520, 1122), "(individual S/ 850)", font=M(28), fill=(200, 190, 175))
    footer(d, dark=True, txt="Separen su evaluación")
    return [save(img, "E_botox_etiqueta.jpg")]


# ---------- F. Este o este ----------
def este_o_este():
    a, b = SERV["D"], DERMAPEN
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W // 2, H), fill=a["claro"]); d.rectangle((W // 2, 0, W, H), fill=b["claro"])
    header(img, d)
    ctr(d, "ESTE O ESTE", M(34, 800), 190, INK)
    ctr(d, "¿Qué le pide tu piel?", C(80, 700), 240, INK)
    for s, x0, q, emo in [(a, 0, "TONO", "1"), (b, W // 2, "TEXTURA", "2")]:
        cx = x0 + W // 4
        badge(d, cx, 470, 80, emo, s["col"], size=86)
        ctr(d, q, M(46, 800), 590, s["col"], x0, x0 + W // 2)
        lines(d, s["n"], C(62, 700), x0 + 40, 670, W // 2 - 80, INK, 66, center=True)
        lines(d, s["d"], M(30), x0 + 50, 820, W // 2 - 100, (74, 63, 53), 42, center=True)
        ctr(d, s["p"], C(84, 700), 930, s["col"], x0, x0 + W // 2)
        ctr(d, "primera visita", M(26), 1030, (90, 78, 66), x0, x0 + W // 2)
    d.ellipse((W // 2 - 56, 414, W // 2 + 56, 526), fill=INK)
    ctr(d, "o", C(70, 700), 425, GOLD)
    d.rounded_rectangle((160, 1090, W - 160, 1170), 40, fill=INK)
    ctr(d, "Comenta 1 o 2", M(40, 700), 1106, GOLD)
    ctr(d, f"{WA} · Cajamarca", M(30, 600), 1240, INK)
    return [save(img, "F_este_o_este.jpg")]


# ---------- Historias interactivas 1080x1920 ----------
def historias():
    out = []
    data = [("TEST", "¿Qué facial necesita tu piel?", "Respóndenos con la palabra TEST y te mandamos las 4 opciones.", SAGE_D),
            ("CAJAMARCA", "¿Sol, frío o polvo?", "¿Qué le afecta más a tu piel? Respóndenos esta historia.", (120, 90, 50)),
            ("PRIMERA VISITA", "Escribe PRECIOS", "Te mandamos el menú facial desde S/ 70 por mensaje.", (44, 30, 40))]
    for i, (tag, t1, t2, bg) in enumerate(data, 1):
        img = Image.new("RGB", (1080, 1920), bg); d = ImageDraw.Draw(img)
        lg = LOGO.copy(); lg.thumbnail((200, 200)); img.paste(lg, ((1080 - lg.width) // 2, 230), lg)
        f = M(34, 700); w = tw(d, tag, f)
        d.rounded_rectangle(((1080 - w) / 2 - 30, 520, (1080 + w) / 2 + 30, 580), 30, fill=GOLD)
        ctr(d, tag, f, 531, INK)
        y = 680
        for ln in wrap(d, t1, C(118, 700), 920): ctr(d, ln, C(118, 700), y, CREAM); y += 130
        y += 30
        for ln in wrap(d, t2, M(48), 860): ctr(d, ln, M(48), y, CREAM); y += 68
        d.rounded_rectangle((160, 1380, 920, 1500), 60, outline=GOLD, width=4)
        ctr(d, "Respóndenos aquí", M(50, 600), 1410, CREAM)
        ctr(d, "WhatsApp", M(40), 1620, CREAM); ctr(d, WA, M(58, 700), 1680, GOLD)
        out.append(save(img, f"H{i}_historia.jpg"))
    return out


if __name__ == "__main__":
    allp = test_carrusel() + cajamarca_carrusel() + biolift_carrusel() + checklist_post() + botox_post() + este_o_este() + historias()
    print("\n".join(allp))

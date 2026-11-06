"""Posts 1080x1350 (consejos y preguntas para comentar) e historias interactivas 1080x1920 de Metabolic Spa CAX."""
from pathlib import Path
from PIL import Image, ImageDraw
import make as m

OUT = Path("/home/claude/iaaltoque-media/spa")
(OUT / "posts").mkdir(parents=True, exist_ok=True)
W, H = 1080, 1350

TIPS = m.TIPS + [
    ("Limpia tu celular", "La pantalla toca tu mejilla muchas veces al día. Desinféctala seguido para evitar granitos."),
    ("Duerme bien", "Dormir 7 a 8 horas ayuda a que tu piel se vea descansada y con mejor tono."),
    ("Menos azúcar, mejor piel", "El exceso de dulces y harinas se puede notar en tu piel. Prefiere frutas y verduras."),
    ("Hidrata aunque tengas piel grasa", "La piel grasa también necesita hidratación. Busca cremas ligeras, sin aceite."),
    ("Cuida tu cuello y tus manos", "También envejecen. Aplica ahí tu crema y tu protector solar."),
    ("La constancia gana", "Los tratamientos dan su mejor resultado cuando completas todas las sesiones."),
]

PREGUNTAS = [  # (pregunta, opciones o pie)
    ("¿Qué te gustaría mejorar de tu piel?", ["1  Manchas", "2  Acné y marcas", "3  Arrugas y flacidez", "4  Poros y textura"]),
    ("¿Qué tratamiento te gustaría probar?", ["1  Limpieza facial Dermadetox", "2  Bio-Lift Facial", "3  Exonucell X", "4  Botox"]),
    ("¿Cada cuánto te haces una limpieza facial?", ["1  Una vez al mes", "2  Cada tres meses", "3  Casi nunca", "4  Nunca me hice una"]),
    ("¿Qué te preocupa más?", ["1  Mi rostro", "2  Mi abdomen", "3  Mis glúteos", "4  Todo un poco"]),
    ("Mito o verdad", ["\"El protector solar solo se usa", "cuando hay sol\"", "", "Comenta MITO o VERDAD"]),
    ("Mito o verdad", ["\"Si tengo piel grasa", "no necesito hidratarla\"", "", "Comenta MITO o VERDAD"]),
]

HISTORIAS = [
    ("¿Tienes alguna duda sobre tu piel?", "Escríbenos por mensaje y la Dra. Winifer te orienta."),
    ("¿Quieres saber qué tratamiento es para ti?", "Respóndenos esta historia con la palabra PIEL."),
    ("¿Te gustaría ver más antes y después?", "Respóndenos SÍ y te mostramos resultados reales."),
    ("Escribe PRECIOS", "y te enviamos nuestro menú completo por mensaje."),
    ("¿Primera vez en un spa?", "Pregúntanos sin compromiso. Te explicamos todo."),
    ("¿Qué día te queda mejor?", "Respóndenos y te separamos tu cita esta semana."),
]


def base(bg):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def tip_post(i, title, body):
    img, d = base(m.CREAM)
    lg = m.LOGO.copy(); lg.thumbnail((150, 150)); img.paste(lg, ((W - lg.width) // 2, 70), lg)
    ctr(d, "CONSEJO DE PIEL", m.font("Montserrat[wght].ttf", 36, 600), 250, m.GOLD2)
    ctr(d, f"#{i}", m.font("CormorantGaramond[wght].ttf", 100, 600), 300, m.GOLD2)
    ft = m.font("CormorantGaramond[wght].ttf", 96, 700); y = 450
    for ln in m.wrap(d, title, ft, 920): ctr(d, ln, ft, y, m.INK); y += 106
    y += 30; fb = m.font("Montserrat[wght].ttf", 42, 500)
    for ln in m.wrap(d, body, fb, 860): ctr(d, ln, fb, y, (74, 63, 53)); y += 60
    d.rounded_rectangle((90, 1110, W - 90, 1280), 28, fill=m.INK)
    ctr(d, "Guárdalo y compártelo con tu amiga 💛".replace(" 💛", ""), m.font("Montserrat[wght].ttf", 34, 500), 1135, m.CREAM)
    ctr(d, "987 293 339 · 931 055 214", m.font("Montserrat[wght].ttf", 52, 700), 1190, m.GOLD)
    return img


def pregunta_post(q, opts):
    img, d = base(m.INK)
    lg = m.LOGO.copy(); lg.thumbnail((150, 150)); img.paste(lg, ((W - lg.width) // 2, 70), lg)
    ctr(d, "TE LEEMOS EN LOS COMENTARIOS", m.font("Montserrat[wght].ttf", 34, 600), 250, m.GOLD)
    ft = m.font("CormorantGaramond[wght].ttf", 92, 700); y = 330
    for ln in m.wrap(d, q, ft, 940): ctr(d, ln, ft, y, m.CREAM); y += 100
    y += 40; fo = m.font("Montserrat[wght].ttf", 46, 600)
    for o in opts:
        if o and o[0].isdigit():
            d.rounded_rectangle((160, y - 12, W - 160, y + 70), 40, outline=m.GOLD, width=3)
            ctr(d, o, fo, y + 2, m.CREAM)
        elif o:
            ctr(d, o, fo, y + 2, m.GOLD if o.startswith("Comenta") else m.CREAM)
        y += 100
    ctr(d, "Metabolic Spa CAX · Cajamarca", m.font("Montserrat[wght].ttf", 34, 500), 1250, m.SOFT)
    return img


def historia(t1, t2):
    img = Image.new("RGB", (1080, 1920), m.INK); d = ImageDraw.Draw(img)
    m.logo(img, 260, 300)
    ft = m.font("CormorantGaramond[wght].ttf", 104, 700); y = 700
    for ln in m.wrap(d, t1, ft, 940): m.center(d, ln, ft, y, m.GOLD); y += 116
    y += 30; fb = m.font("Montserrat[wght].ttf", 50, 500)
    for ln in m.wrap(d, t2, fb, 900): m.center(d, ln, fb, y, m.CREAM); y += 70
    d.rounded_rectangle((140, 1400, 940, 1520), 60, outline=m.GOLD, width=4)
    m.center(d, "Respóndenos aquí 👇".replace(" 👇", ""), m.font("Montserrat[wght].ttf", 50, 600), 1430, m.CREAM)
    m.cta(d, 1620)
    return img


def ctr(d, t, fo, y, col):
    tw = d.textbbox((0, 0), t, font=fo)[2]; d.text(((W - tw) / 2, y), t, font=fo, fill=col)


if __name__ == "__main__":
    for i, (t, b) in enumerate(TIPS, 1):
        tip_post(i, t, b).save(OUT / "posts" / f"consejo_{i:02d}.jpg", quality=92)
    for i, (q, o) in enumerate(PREGUNTAS, 1):
        pregunta_post(q, o).save(OUT / "posts" / f"pregunta_{i:02d}.jpg", quality=92)
    for i, (a, b) in enumerate(HISTORIAS, 1):
        historia(a, b).save(OUT / "historias" / f"interactiva_{i}.jpg", quality=92)
    print("ok")

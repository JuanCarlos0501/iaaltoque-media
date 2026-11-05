"""Carruseles (1080x1350) e historias (1080x1920) de IA al Toque con Kusi."""
import pathlib, subprocess, sys, html
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from brand import BG, CYAN, ORANGE, WHITE, KUSI, BOLT, glow

ROOT = pathlib.Path(__file__).resolve().parent.parent
E = html.escape
FONT = "font-family='Poppins'"


def render(svg, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    s = out.with_suffix(".svg"); s.write_text(svg)
    png = out.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-o", str(png), str(s)], check=True)
    subprocess.run(["convert", str(png), "-quality", "92", str(out)], check=True)
    s.unlink(); png.unlink()


def lines(txt, x, y, size, color, weight=700, lh=1.25, anchor="start"):
    out = []
    for i, t in enumerate(txt.split("\n")):
        out.append(f"<text x='{x}' y='{y + i*size*lh:.0f}' {FONT} font-size='{size}' font-weight='{weight}' "
                   f"fill='{color}' text-anchor='{anchor}'>{E(t)}</text>")
    return "".join(out)


def frame(w, h, body, page=None, total=None):
    pg = ""
    if page:
        pg = (f"<text x='{w-70}' y='{h-60}' {FONT} font-size='30' font-weight='600' fill='#8A8FB0' "
              f"text-anchor='end'>{page}/{total}</text>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
            f"<rect width='{w}' height='{h}' fill='{BG}'/>{glow(w-120, 160, 520, CYAN, 0.18)}{glow(120, h-120, 520, ORANGE, 0.14)}"
            f"<text x='70' y='{h-60}' {FONT} font-size='30' font-weight='700' fill='{CYAN}'>@iaaltoqueoficial</text>"
            f"{pg}{body}</svg>")


def kusi(x, y, s):
    return f"<g transform='translate({x} {y}) scale({s})'>{KUSI}</g>"


def cover(title, sub, n):
    body = (kusi(600, 760, 0.95) + BOLT(90, 150, 1.4) +
            lines(title, 70, 330, 92, WHITE, 800, 1.12) +
            lines(sub, 70, 330 + 92*1.12*title.count("\n") + 120, 40, CYAN, 600) +
            f"<text x='70' y='1170' {FONT} font-size='34' font-weight='700' fill='{ORANGE}'>Desliza →</text>")
    return frame(1080, 1350, body, 1, n)


def card(num, head, text, n, total, extra=""):
    body = (f"<circle cx='140' cy='220' r='70' fill='{ORANGE}'/>"
            f"<text x='140' y='248' {FONT} font-size='80' font-weight='800' fill='{BG}' text-anchor='middle'>{E(num)}</text>"
            + lines(head, 70, 420, 76, WHITE, 800, 1.12)
            + lines(text, 70, 420 + 76*1.12*(head.count('\n')+1) + 50, 42, "#C9CCE0", 500, 1.4) + extra
            + kusi(820, 1030, 0.42))
    return frame(1080, 1350, body, n, total)


def prompt_box(p, y):
    h = 70 + 46*1.35*(p.count("\n")+1)
    return (f"<rect x='70' y='{y}' width='940' height='{h:.0f}' rx='28' fill='#1A1C33' stroke='{CYAN}' stroke-width='3'/>"
            + lines(p, 105, y + 70, 38, CYAN, 600, 1.35))


def cta(n):
    body = (kusi(340, 120, 1.0) +
            lines("¿Te sirvió?", 540, 760, 92, WHITE, 800, 1.1, "middle") +
            lines("Guárdalo para tenerlo a mano\ny compártelo con quien lo necesite", 540, 870, 40, "#C9CCE0", 500, 1.35, "middle") +
            f"<rect x='240' y='1010' width='600' height='110' rx='55' fill='{ORANGE}'/>"
            f"<text x='540' y='1080' {FONT} font-size='40' font-weight='800' fill='{BG}' text-anchor='middle'>Sígueme para más IA</text>")
    return frame(1080, 1350, body, n, n)


CARRUSELES = {
    "c01_herramientas_gratis": [
        ("cover", "3 herramientas\nde IA gratis\nque sí sirven", "Solo necesitas una cuenta de Google o un correo"),
        ("card", "1", "NotebookLM", "Sube tus PDFs, apuntes o enlaces\ny te los resume, te hace preguntas\no un podcast en audio.\n\nGratis con tu cuenta de Google:\nhasta 100 cuadernos\ny 50 fuentes en cada uno."),
        ("card", "2", "Perplexity", "Un buscador que te responde\ncon fuentes para que verifiques.\n\nEn el plan gratis las búsquedas\nbásicas no tienen límite."),
        ("card", "3", "Gemini", "El asistente de Google: redacta,\nresume, crea imágenes y hace\ninvestigación profunda.\n\nGratis con tu cuenta de Google;\nel uso se renueva cada 5 horas."),
        ("cta",),
    ],
    "c02_formula_prompt": [
        ("cover", "La fórmula\ndel prompt\nque funciona", "4 piezas: Rol + Tarea + Contexto + Formato"),
        ("card", "R", "Rol", "Dile quién debe ser.\n\n\"Actúa como profesor de primaria\"\n\"Eres un asesor de ventas\""),
        ("card", "T", "Tarea", "Una sola acción clara,\ncon un verbo al inicio.\n\n\"Escribe\", \"Resume\", \"Compara\""),
        ("card", "C", "Contexto", "Lo que la IA no sabe:\npara quién es, el objetivo\ny los límites.\n\n\"Es para clientes de Lima,\ntono cercano, sin tecnicismos\""),
        ("card", "F", "Formato", "Cómo quieres la respuesta.\n\n\"En 5 viñetas\"\n\"Tabla de 3 columnas\"\n\"Máximo 100 palabras\""),
        ("example",),
        ("cta",),
    ],
    "c03_prompts_dia": [
        ("cover", "5 prompts\npara ahorrar\ntiempo cada día", "Cópialos tal cual en tu chat de IA favorito"),
        ("prompt", "1", "Correos largos", "Resume este correo en 3 viñetas\ny dime qué me piden hacer\ny para cuándo: [pega el correo]"),
        ("prompt", "2", "Responder rápido", "Escribe una respuesta amable\ny breve a este mensaje.\nAcepto, pero pido mover la\nreunión al jueves: [mensaje]"),
        ("prompt", "3", "Ordenar tu semana", "Con estas tareas arma un plan\nde lunes a viernes, lo urgente\nprimero y bloques de 1 hora:\n[lista de tareas]"),
        ("prompt", "4", "Notas a acciones", "Convierte estas notas de reunión\nen una lista de tareas con\nresponsable y fecha: [notas]"),
        ("prompt", "5", "Entender cualquier tema", "Explícame [tema] como si\ntuviera 12 años, con un ejemplo\nde la vida diaria."),
        ("cta",),
    ],
}


def example(n, total):
    p = ("Actúa como chef peruano. Crea un\nmenú semanal económico para 4\npersonas, sin mariscos, en una\ntabla día / almuerzo / costo.")
    body = (lines("Ejemplo completo", 70, 220, 76, WHITE, 800) +
            lines("Rol + Tarea + Contexto + Formato", 70, 300, 38, ORANGE, 700) +
            prompt_box(p, 380) + kusi(820, 1030, 0.42))
    return frame(1080, 1350, body, n, total)


def build_carousels():
    for slug, slides in CARRUSELES.items():
        n = len(slides)
        for i, s in enumerate(slides, 1):
            k = s[0]
            if k == "cover": svg = cover(s[1], s[2], n)
            elif k == "card": svg = card(s[1], s[2], s[3], i, n)
            elif k == "prompt":
                svg = card(s[1], s[2], "", i, n, prompt_box(s[3], 560))
            elif k == "example": svg = example(i, n)
            else: svg = cta(n)
            render(svg, ROOT / "social/carruseles" / slug / f"{i:02d}.jpg")


HISTORIAS = [
    ("h_vie", "Viernes de IA", "Hoy hay reel nuevo"),
    ("h_sab", "Sábado práctico", "Un truco nuevo te espera"),
    ("h_dom", "Domingo de aprender", "Nuevo reel en el perfil"),
    ("h_lun", "Arranca la semana", "Con un truco de IA nuevo"),
    ("h_mar", "Martes de IA", "Hoy hay reel nuevo"),
    ("h_mie", "Mitad de semana", "Un atajo más con IA"),
]


def build_stories():
    for slug, top, sub in HISTORIAS:
        body = (f"<rect width='1080' height='1920' fill='{BG}'/>{glow(900, 300, 700, CYAN, 0.2)}{glow(150, 1700, 700, ORANGE, 0.16)}"
                + lines(top.upper(), 540, 330, 50, CYAN, 700, 1.2, "middle")
                + lines("NUEVO\nREEL", 540, 500, 190, WHITE, 800, 0.95, "middle")
                + lines(sub, 540, 820, 50, "#C9CCE0", 600, 1.2, "middle")
                + kusi(290, 900, 1.25)
                + f"<rect x='240' y='1560' width='600' height='120' rx='60' fill='{ORANGE}'/>"
                f"<text x='540' y='1637' {FONT} font-size='44' font-weight='800' fill='{BG}' text-anchor='middle'>Míralo en el perfil</text>"
                f"<text x='540' y='1790' {FONT} font-size='40' font-weight='700' fill='{CYAN}' text-anchor='middle'>@iaaltoqueoficial</text>")
        svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920'>{body}</svg>"
        render(svg, ROOT / "social/historias" / f"{slug}.jpg")


if __name__ == "__main__":
    build_carousels(); build_stories()

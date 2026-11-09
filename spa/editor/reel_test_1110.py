"""Reel 1080x1920 (~17 s): antes/después del Bio-Lift con barrido + test '¿Qué facial necesita tu piel?'.
Reutiliza la foto real del flyer biolift.jpg con formato nuevo. Salida: spa/semana_1110/reel_test.mp4
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
sys.path.insert(0, str(Path(__file__).parent))
import semana_1110 as s

W, H, FPS = 1080, 1920, 30
OUT = s.OUT / "reel_test.mp4"
src = Image.open(s.HERE.parent / "flyers" / "biolift.jpg").convert("RGB")
ANTES = ImageOps.fit(src.crop((80, 385, 530, 745)), (W, 1300), centering=(0.5, 0.45))
DESP = ImageOps.fit(src.crop((550, 385, 1000, 745)), (W, 1300), centering=(0.5, 0.45))
ease = lambda t: 1 - (1 - max(0, min(1, t))) ** 3


def logo(img, d, dark=True):
    lg = s.LOGO.copy(); lg.thumbnail((110, 110)); img.paste(lg, (60, 70), lg)
    d.text((190, 95), "METABOLIC SPA CAX", font=s.M(32, 700), fill=s.GOLD)
    d.text((190, 137), "Cajamarca", font=s.M(28), fill=s.CREAM if dark else s.INK)


def ctrw(d, t, fo, y, col): d.text(((W - s.tw(d, t, fo)) / 2, y), t, font=fo, fill=col)


def f_hook(t):  # 0-5 s: antes -> barrido -> después
    img = Image.new("RGB", (W, H), s.INK)
    z = 1 + 0.04 * t / 5
    a = ANTES.resize((int(W * z), int(1300 * z))); dd = DESP.resize(a.size)
    off = ((a.width - W) // 2, (a.height - 1300) // 2)
    img.paste(a.crop((off[0], off[1], off[0] + W, off[1] + 1300)), (0, 360))
    p = ease((t - 2.0) / 1.4); x = int(W * p)
    if x > 0:
        img.paste(dd.crop((off[0], off[1], off[0] + x, off[1] + 1300)), (0, 360))
    d = ImageDraw.Draw(img)
    if 0 < x < W: d.rectangle((x - 4, 360, x + 4, 1660), fill=s.GOLD)
    logo(img, d)
    ctrw(d, "¿Notas el cambio?", s.C(100, 700), 210, s.CREAM)
    lab, col = ("ANTES", s.INK) if p < 0.5 else ("DESPUÉS", s.GOLD2)
    f = s.M(44, 800); w = s.tw(d, lab, f)
    d.rounded_rectangle((60, 1560, 60 + w + 70, 1636), 38, fill=col); d.text((95, 1572), lab, font=f, fill=s.CREAM)
    d.text((60, 1700), "Bio-Lift Facial · paciente real", font=s.M(38, 600), fill=s.CREAM)
    d.text((60, 1756), "4 sesiones · S/ 1,500", font=s.M(38), fill=s.GOLD)
    return img


def f_pregunta(t):  # 5-7 s
    img = Image.new("RGB", (W, H), s.SAGE_D); d = ImageDraw.Draw(img); logo(img, d)
    k = ease(t / 0.6)
    d.text((60, 600 + int(60 * (1 - k))), "Y tu piel,", font=s.C(150, 700), fill=s.CREAM)
    d.text((60, 760 + int(60 * (1 - k))), "¿qué necesita?", font=s.C(130, 700), fill=s.GOLD)
    d.text((60, 1000), "Elige tu letra y coméntala", font=s.M(46, 500), fill=s.CREAM)
    for i, L in enumerate("ABCD"):
        kk = ease((t - 0.4 - i * 0.15) / 0.4)
        if kk > 0: s.badge(d, 150 + i * 190, 1250, int(75 * kk) + 1, L, s.SERV[L]["col"], size=max(10, int(80 * kk)))
    return img


def f_card(L, t):  # 1.8 s cada una
    v = s.SERV[L]; img = Image.new("RGB", (W, H), v["claro"]); d = ImageDraw.Draw(img); logo(img, d, dark=False)
    k = ease(t / 0.45); dx = int(W * (1 - k))
    s.badge(d, 200 + dx, 470, 130, L, v["col"])
    d.text((380 + dx, 380), "SI TU PIEL TIENE…", font=s.M(34, 700), fill=v["col"])
    s.lines(d, v["sintoma"], s.C(70, 700), 380 + dx, 430, 640, s.INK, 78)
    d.rounded_rectangle((60 + dx, 760, W - 60 + dx, 1420), 44, fill=s.CREAM)
    d.text((110 + dx, 820), "TU FACIAL ES", font=s.M(34, 700), fill=v["col"])
    y = s.lines(d, v["n"], s.C(120, 700), 110 + dx, 870, 860, s.INK, 122)
    d.text((110 + dx, y + 40), v["d"], font=s.M(40), fill=(90, 78, 66))
    d.text((110 + dx, 1230), "Primera visita", font=s.M(34), fill=(90, 78, 66))
    d.text((110 + dx, 1265), v["p"], font=s.C(100, 700), fill=v["col"])
    f = s.M(44, 700); tt = f"Comenta  {L}"; w = s.tw(d, tt, f)
    d.rounded_rectangle((W - 110 - w - 70 + dx, 1280, W - 110 + dx, 1366), 43, fill=v["col"])
    d.text((W - 110 - w - 35 + dx, 1296), tt, font=f, fill=s.CREAM)
    return img


def f_cta(t):  # 3 s
    img = Image.new("RGB", (W, H), s.INK); d = ImageDraw.Draw(img)
    lg = s.LOGO.copy(); lg.thumbnail((300, 300)); img.paste(lg, ((W - lg.width) // 2, 300), lg)
    ctrw(d, "Comenta tu letra", s.C(120, 700), 720, s.CREAM)
    ctrw(d, "y te decimos por dónde empezar", s.M(46), 880, s.GOLD)
    for i, L in enumerate("ABCD"): s.badge(d, 255 + i * 190, 1100, 70, L, s.SERV[L]["col"])
    ctrw(d, "Primera visita desde S/ 70", s.M(48, 700), 1300, s.CREAM)
    ctrw(d, "WhatsApp", s.M(42), 1480, s.CREAM)
    ctrw(d, s.WA, s.M(62, 800), 1545, s.GOLD)
    ctrw(d, "Cajamarca", s.M(40), 1660, (200, 190, 175))
    return img


SEG = [(5.0, f_hook), (2.0, f_pregunta)] + [(1.8, (lambda L: lambda t: f_card(L, t))(L)) for L in "ABCD"] + [(3.0, f_cta)]

if __name__ == "__main__":
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", str(OUT)],
                         stdin=subprocess.PIPE)
    for dur, fn in SEG:
        for i in range(int(dur * FPS)):
            p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print(OUT)

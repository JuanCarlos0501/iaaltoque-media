"""Arma un reel vertical de IA al Toque a partir de un guion en JSON y la voz.

Uso: python3 make_reel.py guion.json voz.mp3 salida.mp4 [voz.align.json]

guion.json:
{
  "id": "reel_02",
  "scenes": [
    {"type": "hook",  "title": ["Línea 1", "Línea 2 (cian)"], "pill": "opcional", "say": "texto que dice la voz"},
    {"type": "step",  "n": 1, "title": ["Título", "en dos líneas"], "lines": ["hasta 5 líneas", "cortas"], "say": "..."},
    {"type": "list",  "badge": "OJO", "title": ["..."], "items": ["con check", "..."], "say": "..."},
    {"type": "cta",   "title": ["Sigue a", "IA al Toque"], "say": "Sigue a IA al Toque para más trucos como este."}
  ]
}
La voz debe leer exactamente los "say" unidos con una línea en blanco (ver narration()).
Con align.json (ElevenLabs) los cortes y subtítulos son exactos; sin él se estiman con las pausas.
"""
import sys, re, json, html, subprocess, pathlib, textwrap

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from brand import KUSI, BG, CYAN, ORANGE, WHITE, grid, glow  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONT = 'font-family="Poppins"'
MUTED = "#B8BCD6"
CAP_Y = 1520          # subtítulos: por encima de la zona que tapan las apps
WORK = pathlib.Path("/tmp/iaaltoque_build")


def esc(s):
    return html.escape(s, quote=False)


def narration(spec):
    return "\n\n".join(s["say"].strip() for s in spec["scenes"])


# ---------- dibujo de escenas ----------
def base(inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{BG}"/>{grid(W, H, 90)}{glow(540, 760, 620, CYAN, 0.22)}
<text x="540" y="150" text-anchor="middle" {FONT} font-weight="700" font-size="44" fill="{WHITE}" opacity="0.85">IA <tspan fill="{CYAN}">al Toque</tspan></text>
{inner}</svg>"""


def title(lines, y, size, hi_last=True, color=WHITE):
    out = []
    for i, ln in enumerate(lines):
        c = CYAN if (hi_last and len(lines) > 1 and i == len(lines) - 1) else color
        out.append(f'<text x="540" y="{y + i * size * 1.15:.0f}" text-anchor="middle" {FONT} font-weight="700" font-size="{size}" fill="{c}">{esc(ln)}</text>')
    return "".join(out)


def fit_size(lines, maxw=960, start=104, minimum=56):
    longest = max(len(l) for l in lines)
    return max(minimum, min(start, int(maxw / (0.56 * max(longest, 1)))))


def pill(text, y, fill=ORANGE, tc=BG, size=46):
    w = int(len(text) * size * 0.6 + size * 1.6)
    return (f'<rect x="{540 - w/2:.0f}" y="{y}" width="{w}" height="{size*1.9:.0f}" rx="{size*0.95:.0f}" fill="{fill}"/>'
            f'<text x="540" y="{y + size*1.32:.0f}" text-anchor="middle" {FONT} font-weight="700" font-size="{size}" fill="{tc}">{esc(text)}</text>')


def card(lines, y, checks=False, accent=CYAN):
    wrapped = []
    for ln in lines:
        wrapped += textwrap.wrap(ln, 26 if checks else 28) or [""]
    wrapped = wrapped[:6]
    h = 70 + 78 * len(wrapped)
    out = [f'<rect x="90" y="{y}" width="900" height="{h}" rx="36" fill="#161936" stroke="{accent}" stroke-width="4"/>']
    for i, ln in enumerate(wrapped):
        ty = y + 88 + i * 78
        if checks:
            out.append(f'<circle cx="160" cy="{ty-16}" r="26" fill="#22C55E"/><path d="M147 {ty-16} l9 9 l18 -20" stroke="{BG}" stroke-width="7" fill="none" stroke-linecap="round"/>')
            out.append(f'<text x="205" y="{ty}" {FONT} font-weight="700" font-size="48" fill="{WHITE}">{esc(ln)}</text>')
        else:
            out.append(f'<text x="140" y="{ty}" {FONT} font-weight="700" font-size="48" fill="{WHITE}">{esc(ln)}</text>')
    return "".join(out), y + h


def draw(scene):
    t = scene["type"]
    if t == "hook":
        size = fit_size(scene["title"])
        inner = title(scene["title"], 430, size)
        if scene.get("pill"):
            inner += pill(scene["pill"], 430 + int(size * 1.15 * len(scene["title"])) + 20)
        return base(inner), (310, 860, 1.15)
    if t == "cta":
        inner = title(scene.get("title", ["Sigue a", "IA al Toque"]), 470, 120)
        inner += pill("@IAalToqueOficial", 760, size=48)
        inner += f'<text x="540" y="950" text-anchor="middle" {FONT} font-weight="700" font-size="52" fill="{MUTED}">Un truco nuevo cada día</text>'
        return base(inner), (340, 1020, 1.0)
    if t in ("step", "list"):
        badge = f"PASO {scene['n']}" if t == "step" else scene.get("badge", "OJO")
        bfill = CYAN if t == "step" else ORANGE
        size = fit_size(scene["title"], start=78, minimum=54)
        inner = pill(badge, 330, fill=bfill, size=44)
        inner += title(scene["title"], 560, size, hi_last=(t == "list"))
        top = 560 + int(size * 1.15 * len(scene["title"])) + 40
        items = scene.get("lines") or scene.get("items") or []
        if items:
            c, _ = card(items, top, checks=(t == "list"), accent=(CYAN if t == "step" else ORANGE))
            inner += c
        return base(inner), (40, 1270, 0.55)
    raise ValueError(f"tipo de escena desconocido: {t}")


# ---------- utilidades ----------
def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def svg2png(svg, path):
    p = path.with_suffix(".svg")
    p.write_text(svg, encoding="utf-8")
    run(["rsvg-convert", "-o", str(path), str(p)])


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())


def word_times_from_alignment(text, align):
    """Devuelve (inicio, fin) por carácter del texto narrado."""
    chars = align["characters"]
    st, en = align["character_start_times_seconds"], align["character_end_times_seconds"]
    if "".join(chars) != text:  # el servicio a veces normaliza; alineamos por posición aproximada
        n = min(len(chars), len(text))
        return [(st[min(i, n - 1)], en[min(i, n - 1)]) for i in range(len(text))]
    return list(zip(st, en))


def estimate_char_times(text, audio):
    """Sin alineación: reparte el tiempo por letras y ajusta los cortes de párrafo a las pausas largas."""
    total = duration(audio)
    log = subprocess.run(["ffmpeg", "-i", audio, "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sil = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)],
                   [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]))
    t0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    t1 = sil[-1][0] if sil and sil[-1][1] >= total - 0.05 else total
    paras = text.split("\n\n")
    lens = [len(p) for p in paras]
    tot = sum(lens)
    gaps = [((a + b) / 2, b - a) for a, b in sil if t0 < a and b < t1]
    bounds, acc = [t0], 0
    for L in lens[:-1]:
        acc += L
        guess = t0 + (t1 - t0) * acc / tot
        near = [g for g in gaps if abs(g[0] - guess) < 1.5]
        bounds.append(max(near, key=lambda g: g[1])[0] if near else guess)
    bounds.append(t1)
    times = []
    for i, p in enumerate(paras):
        a, b = bounds[i], bounds[i + 1]
        for j in range(len(p)):
            times.append((a + (b - a) * j / len(p), a + (b - a) * (j + 1) / len(p)))
        if i < len(paras) - 1:
            times += [(b, b), (b, b)]  # los dos "\n"
    return times


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    audio, out = sys.argv[2], sys.argv[3]
    align = json.load(open(sys.argv[4]))["alignment"] if len(sys.argv) > 4 else None
    text = narration(spec)
    ct = word_times_from_alignment(text, align) if align else estimate_char_times(text, audio)
    total = duration(audio)

    WORK.mkdir(parents=True, exist_ok=True)
    for f in WORK.glob("*"):
        f.unlink()
    svg2png(f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="480" viewBox="0 0 400 480">{KUSI}</svg>', WORK / "kusi.png")

    # inicio de cada escena = tiempo del primer carácter de su "say"
    starts, pos = [], 0
    for s in spec["scenes"]:
        starts.append(ct[pos][0])
        pos += len(s["say"].strip()) + 2
    starts[0] = 0.0
    ends = starts[1:] + [total + 0.6]

    # subtítulos: trozos de hasta 4 palabras con su tiempo real
    caps, pos = [], 0
    for s in spec["scenes"]:
        say = s["say"].strip()
        for m in re.finditer(r"\S+", say):
            caps.append([pos + m.start(), pos + m.end(), m.group()])
        pos += len(say) + 2
    chunks, cur = [], []
    for c in caps:
        cur.append(c)
        if len(cur) == 4 or c[2].endswith((".", ",", ":", "?", "!")):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    cap_list = []
    for i, ch in enumerate(chunks):
        a = ct[ch[0][0]][0]
        b = ct[chunks[i + 1][0][0]][0] if i + 1 < len(chunks) else ct[ch[-1][1] - 1][1] + 0.3
        txt = " ".join(c[2] for c in ch).rstrip(".,:")
        cap_list.append((a, b, txt))

    cap_png = []
    for i, (_, _, txt) in enumerate(cap_list):
        fs = min(62, int(62 * 25 / max(len(txt), 1)))  # subtítulos largos: letra más chica para no salir del cuadro
        w = min(980, max(300, int(len(txt) * 33 * fs / 62 + 90)))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="150" viewBox="0 0 1000 150">'
               f'<rect x="{500 - w/2:.0f}" y="15" width="{w}" height="120" rx="30" fill="#000" opacity="0.72"/>'
               f'<text x="500" y="{75 + fs * 0.37:.0f}" text-anchor="middle" {FONT} font-weight="700" font-size="{fs}" fill="{WHITE}">{esc(txt)}</text></svg>')
        p = WORK / f"c{i:03d}.png"; svg2png(svg, p); cap_png.append(p)

    parts = []
    for si, s in enumerate(spec["scenes"]):
        svg, (kx, ky, ks) = draw(s)
        bg = WORK / f"s{si}.png"; svg2png(svg, bg)
        t0, t1 = starts[si], ends[si]
        dur = t1 - t0
        mine = [(j, c) for j, c in enumerate(cap_list) if c[0] < t1 and c[1] > t0]
        inputs = ["-framerate", str(FPS), "-i", str(bg), "-i", str(WORK / "kusi.png")]
        for j, _ in mine:
            inputs += ["-i", str(cap_png[j])]
        fade = "fade=t=in:st=0:d=0.25," if si else ""
        fc = [f"[0]format=yuv420p,loop=-1:1,trim=duration={dur:.3f},setpts=PTS-STARTPTS,{fade}format=rgba[bg]",
              f"[1]scale={int(400 * ks)}:-1[k]",
              f"[bg][k]overlay=x={kx}:y='{ky}+12*sin(2*PI*t/1.6)':format=auto[v0]"]
        last = "v0"
        for n, (j, (a, b, _)) in enumerate(mine):
            fc.append(f"[{last}][{n+2}]overlay=x=40:y={CAP_Y}:enable='between(t,{max(0, a-t0):.3f},{min(dur, b-t0):.3f})'[v{n+1}]")
            last = f"v{n+1}"
        fc.append(f"[{last}]format=yuv420p[out]")
        tmp = WORK / f"p{si}.tmp.mp4"
        run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[out]", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(tmp)])
        final = WORK / f"p{si}.mp4"; tmp.rename(final); parts.append(final)

    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(WORK / "video.mp4")])
    run(["ffmpeg", "-y", "-i", str(WORK / "video.mp4"), "-i", audio, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", out])
    print("escenas:", [round(x, 2) for x in starts], "duración:", round(duration(out), 2))


if __name__ == "__main__":
    main()

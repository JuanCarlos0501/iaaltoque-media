"""Reel 'Nuevo ingreso Sanendi' para Metabolic Spa CAX (1080x1920, 30 fps)."""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/claude/spa/stories")
import make as m

U = Path("/mnt/user-data/uploads")
D = Path("/home/claude/spa/sanendi"); T = D / "tmp"; T.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
GOLD, CREAM, INK = (232, 196, 120), (250, 246, 238), (18, 12, 10)
F = lambda s, w=500: m.font("Montserrat[wght].ttf", s, w)
C = lambda s, w=700: m.font("CormorantGaramond[wght].ttf", s, w)
FOTOS = {"ultra": U / "dfcdf5df-image.jpg", "light": U / "296683f6-image.jpg",
         "deep": U / "ea844c22-image.jpg", "plla": U / "56fb21c5-image.jpg"}
MOV = U / "3e01eb3c-IMG_1809.mov"


def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-1500:])


def ctr(d, t, fo, y, col, shadow=True):
    tw = d.textbbox((0, 0), t, font=fo)[2]; x = (W - tw) / 2
    if shadow: d.text((x + 2, y + 3), t, font=fo, fill=(0, 0, 0, 150))
    d.text((x, y), t, font=fo, fill=col)


def overlay(nombre, sup=None, titulo=None, sub=None, acento=GOLD, logo=True):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # degradados para legibilidad
    for y in range(420):
        a = int(170 * (1 - y / 420)); d.line((0, y, W, y), fill=(10, 6, 6, a))
    for y in range(H - 640, H):
        a = int(215 * ((y - (H - 640)) / 640)); d.line((0, y, W, y), fill=(10, 6, 6, a))
    if logo:
        lg = m.LOGO.copy(); lg.thumbnail((150, 150)); img.paste(lg, ((W - lg.width) // 2, 230), lg)
        d = ImageDraw.Draw(img)
        ctr(d, "METABOLIC SPA CAX", F(34, 600), 395, GOLD)
    y = H - 520
    if sup:
        fo = F(38, 700); tw = d.textbbox((0, 0), sup, font=fo)[2]
        d.rounded_rectangle(((W - tw) / 2 - 34, y - 12, (W + tw) / 2 + 34, y + 56), 34, fill=(15, 10, 10, 200), outline=acento, width=3)
        ctr(d, sup, fo, y, acento, shadow=False); y += 84
    if titulo:
        for ln in titulo.split("\n"): ctr(d, ln, C(104), y, CREAM); y += 108
    if sub:
        y += 10
        for ln in sub.split("\n"): ctr(d, ln, F(42, 500), y, (245, 232, 220)); y += 58
    img.save(T / f"{nombre}.png")


def tarjeta(nombre, lineas, fondo=None):
    """Tarjeta completa (intro/cierre) sobre fondo oscuro con brillo dorado."""
    img = Image.new("RGB", (W, H), INK)
    g = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(g)
    for (x, y, r, c) in [(200, 500, 380, (140, 90, 40)), (900, 1300, 420, (120, 50, 90)), (540, 950, 300, (90, 60, 30))]:
        gd.ellipse((x - r, y - r, x + r, y + r), fill=c)
    img = Image.blend(img, g.filter(ImageFilter.GaussianBlur(160)), 0.8).convert("RGBA")
    d = ImageDraw.Draw(img)
    lg = m.LOGO.copy(); lg.thumbnail((360, 360)); img.paste(lg, ((W - lg.width) // 2, 300), lg)
    d = ImageDraw.Draw(img)
    for (txt, fo, col, y) in lineas: ctr(d, txt, fo, y, col)
    img.convert("RGB").save(T / f"{nombre}.jpg", quality=95)


def seg_foto(nombre, foto, dur, ov, zoom_in=True):
    # fondo desenfocado + foto completa con zoom lento (Ken Burns)
    n = dur * FPS
    z = "1+0.0010*on" if zoom_in else "1.12-0.0010*on"
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.08[bg];"
          f"[0:v]scale={W*2}:-2,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{int(W*4/3)}:fps={FPS}[fg];"
          f"[bg][fg]overlay=0:(H-h)/2-60:shortest=1,format=yuv420p[v];[v][1:v]overlay=0:0,fade=t=in:d=0.35,fade=t=out:st={dur-0.35}:d=0.35")
    sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(dur), "-i", str(foto), "-i", str(T / f"{ov}.png"),
       "-filter_complex", fc, "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
       "-pix_fmt", "yuv420p", "-an", str(T / f"{nombre}.mp4"))


def seg_video(nombre, ini, dur, ov):
    fc = (f"[0:v]zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
          f"zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"fps={FPS},eq=contrast=1.05:saturation=1.1[v];[v][1:v]overlay=0:0,fade=t=in:d=0.35,fade=t=out:st={dur-0.35}:d=0.35")
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", str(dur), "-i", str(MOV), "-i", str(T / f"{ov}.png"),
       "-filter_complex", fc, "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
       "-an", str(T / f"{nombre}.mp4"))


def seg_tarjeta(nombre, dur):
    n = dur * FPS
    sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(dur), "-i", str(T / f"{nombre}.jpg"),
       "-vf", f"scale={W*2}:-2,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
              f"format=yuv420p,fade=t=in:d=0.4,fade=t=out:st={dur-0.4}:d=0.4",
       "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-an", str(T / f"{nombre}.mp4"))


def musica(dur):
    # pad suave y elegante (acordes generados, sin derechos de autor)
    acordes = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
    partes = []
    for i, ac in enumerate(acordes):
        expr = "+".join(f"0.06*sin(2*PI*{f}*t)+0.03*sin(2*PI*{f*2}*t)" for f in ac)
        partes.append(expr)
    seg = dur / 4
    e = "+".join(f"if(between(t,{i*seg},{(i+1)*seg}),{p},0)" for i, p in enumerate(partes))
    sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='{e}':s=48000:d={dur}",
       "-af", f"lowpass=f=2500,aecho=0.8:0.7:60|120:0.3|0.2,afade=t=in:d=1.5,afade=t=out:st={dur-2.5}:d=2.5,"
              "loudnorm=I=-18:TP=-2,aresample=48000", "-ac", "2", str(T / "musica.wav"))


if __name__ == "__main__":
    tarjeta("intro", [("NUEVO INGRESO", F(46, 600), GOLD, 760), ("Sanendi", C(170), CREAM, 830),
                      ("Ácido hialurónico y", F(44), (240, 225, 210), 1050), ("bioestimulador de colágeno", F(44), (240, 225, 210), 1110),
                      ("Ahora en Cajamarca", C(84), GOLD, 1260)])
    tarjeta("cierre", [("Agenda tu evaluación", C(96), CREAM, 760), ("Aplicación por médico", F(42), (240, 225, 210), 880),
                       ("Escríbenos por WhatsApp", F(44), (240, 225, 210), 1080), ("987 293 339", F(84, 700), GOLD, 1150),
                       ("931 055 214", F(84, 700), GOLD, 1260), ("Metabolic Spa CAX · Cajamarca", F(38, 500), (225, 210, 195), 1440)])
    overlay("ov_mov1", "RECIÉN LLEGADO", "Línea Sanendi", "a Metabolic Spa CAX")
    overlay("ov_ultra", "ULTRA VOLUME-L", "Volumen y\ncontorno", "Pómulos · mentón · línea mandibular", (200, 170, 255))
    overlay("ov_light", "LIGHT-L", "Corrección sutil", "Líneas finas · contorno de ojos · labios", (255, 160, 190))
    overlay("ov_deep", "DEEP LINE-L", "Líneas profundas", "Surcos nasolabiales · líneas de marioneta", (150, 200, 255))
    overlay("ov_plla", "ÁCIDO POLI-L-LÁCTICO (PLLA)", "Bioestimulador\nde colágeno", "Firmeza y volumen de forma progresiva")
    overlay("ov_mov2", "RESULTADOS NATURALES", "Tu cambio también\nes posible", None)
    segs = [("intro", "t", 3), ("mov1", "v", (0.5, 4)), ("ultra", "f", 3), ("light", "f", 3), ("deep", "f", 3),
            ("plla", "f", 3), ("mov2", "v", (6, 4)), ("cierre", "t", 4)]
    for nombre, tipo, x in segs:
        if tipo == "t": seg_tarjeta(nombre, x)
        elif tipo == "v": seg_video(nombre, x[0], x[1], f"ov_{nombre}")
        else: seg_foto(nombre, FOTOS[nombre], x, f"ov_{nombre}", zoom_in=nombre in ("ultra", "deep"))
    total = sum(x if isinstance(x, (int, float)) else x[1] for _, _, x in segs)
    musica(total)
    (T / "lista.txt").write_text("".join(f"file '{n}.mp4'\n" for n, _, _ in segs))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(T / "lista.txt"), "-i", str(T / "musica.wav"),
       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(D / "sanendi_nuevo_ingreso.mp4"))
    print("ok", total)

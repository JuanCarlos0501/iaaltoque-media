"""Identidad visual de IA al Toque: colores, Kusi y utilidades SVG."""

import subprocess, pathlib

BG = "#0F1020"
CYAN = "#22D3EE"
ORANGE = "#FF7A1A"
WHITE = "#F5F5F7"
SHADE = "#D9DCE6"

# Kusi en una caja de 400 x 480 (origen arriba a la izquierda)
KUSI = f"""
<g>
  <!-- cola de la bufanda -->
  <path d="M232 340 q18 34 6 92 l-30 -6 q10 -44 -6 -80 z" fill="{ORANGE}"/>
  <path d="M214 398 l26 6 M217 386 l26 6" stroke="#C85A0C" stroke-width="5" stroke-linecap="round"/>
  <!-- cuello / cuerpo -->
  <rect x="142" y="250" width="116" height="215" rx="56" fill="{WHITE}" stroke="{SHADE}" stroke-width="6"/>
  <g fill="{WHITE}" stroke="{SHADE}" stroke-width="5">
    <circle cx="172" cy="372" r="20"/><circle cx="228" cy="372" r="20"/><circle cx="200" cy="380" r="22"/>
  </g>
  <rect x="178" y="414" width="44" height="26" rx="10" fill="{SHADE}"/>
  <circle cx="200" cy="427" r="7" fill="{CYAN}"/>
  <!-- orejas -->
  <g transform="rotate(-48 104 140)">
    <path d="M104 172 C80 150 84 104 104 82 C124 104 128 150 104 172 Z" fill="{WHITE}" stroke="{SHADE}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M104 160 C92 146 94 116 104 102 C114 116 116 146 104 160 Z" fill="{ORANGE}"/>
  </g>
  <g transform="rotate(48 296 140)">
    <path d="M296 172 C272 150 276 104 296 82 C316 104 320 150 296 172 Z" fill="{WHITE}" stroke="{SHADE}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M296 160 C284 146 286 116 296 102 C306 116 308 146 296 160 Z" fill="{ORANGE}"/>
  </g>
  <!-- cabeza -->
  <rect x="84" y="118" width="232" height="176" rx="84" fill="{WHITE}" stroke="{SHADE}" stroke-width="6"/>
  <!-- antena con rayo -->
  <line x1="200" y1="96" x2="200" y2="52" stroke="{SHADE}" stroke-width="8" stroke-linecap="round"/>
  <path d="M206 6 L184 40 L198 40 L190 66 L216 28 L202 28 Z" fill="{CYAN}" stroke="{BG}" stroke-width="3" stroke-linejoin="round"/>
  <!-- copete de lana -->
  <g fill="{WHITE}" stroke="{SHADE}" stroke-width="6">
    <circle cx="156" cy="124" r="30"/>
    <circle cx="244" cy="124" r="30"/>
    <circle cx="200" cy="110" r="36"/>
  </g>
  <g fill="{WHITE}">
    <circle cx="156" cy="128" r="26"/><circle cx="244" cy="128" r="26"/><circle cx="200" cy="116" r="31"/>
    <rect x="140" y="130" width="120" height="30"/>
  </g>
  <!-- visor -->
  <rect x="108" y="160" width="184" height="96" rx="46" fill="{BG}"/>
  <rect x="108" y="160" width="184" height="96" rx="46" fill="none" stroke="#2A2D4A" stroke-width="4"/>
  <!-- ojos -->
  <g fill="{CYAN}">
    <ellipse cx="164" cy="206" rx="17" ry="21"/>
    <ellipse cx="236" cy="206" rx="17" ry="21"/>
  </g>
  <g fill="{WHITE}">
    <circle cx="170" cy="198" r="6"/><circle cx="242" cy="198" r="6"/>
  </g>
  <!-- hocico -->
  <ellipse cx="200" cy="284" rx="50" ry="30" fill="{WHITE}" stroke="{SHADE}" stroke-width="6"/>
  <ellipse cx="200" cy="276" rx="10" ry="6" fill="#3A3D5C"/>
  <path d="M200 282 v8 M200 290 q-10 8 -18 2 M200 290 q10 8 18 2" fill="none" stroke="#3A3D5C" stroke-width="4" stroke-linecap="round"/>
  <!-- mejillas -->
  <ellipse cx="98" cy="236" rx="10" ry="7" fill="{ORANGE}" opacity="0.8"/>
  <ellipse cx="302" cy="236" rx="10" ry="7" fill="{ORANGE}" opacity="0.8"/>
  <!-- bufanda -->
  <rect x="130" y="314" width="140" height="36" rx="18" fill="{ORANGE}"/>
  <path d="M150 322 v20 M175 322 v20 M200 322 v20 M225 322 v20 M250 322 v20" stroke="#C85A0C" stroke-width="4" stroke-linecap="round"/>
</g>
"""

BOLT = lambda x, y, s: (f'<path transform="translate({x} {y}) scale({s})" '
                        f'd="M22 0 L0 34 L14 34 L6 60 L32 22 L18 22 Z" fill="{ORANGE}"/>')


def glow(cx, cy, r, color, op):
    return (f'<radialGradient id="g{cx}{cy}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#g{cx}{cy})"/>')




def grid(w, h, step):
    lines = [f'<path d="M{x} 0 V{h}" />' for x in range(0, w + 1, step)]
    lines += [f'<path d="M0 {y} H{w}" />' for y in range(0, h + 1, step)]
    return f'<g stroke="#1C1F38" stroke-width="2">{"".join(lines)}</g>'

from PIL import Image, ImageDraw, ImageFont
import os, shutil

W, H = 1000, 540
FPS = 20
DUR = 5.0
N = int(FPS * DUR)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f_term = ImageFont.truetype(MONO, 22)
f_small = ImageFont.truetype(MONO, 19)
f_title = ImageFont.truetype(MONO_B, 22)
f_key = ImageFont.truetype(MONO_B, 30)
f_cap = ImageFont.truetype(MONO, 20)

BG = (18, 20, 28)
PANEL = (26, 29, 40)
BAR = (36, 40, 54)
FG = (225, 230, 240)
DIM = (92, 98, 118)
GREEN = (120, 220, 140)
BLUE = (110, 170, 255)
ACCENT = (255, 196, 80)
KEY_BG = (44, 48, 66)

history = [
    "cd ~/projects",
    "sudo systemctl status sshd",
    "git status",
    "sudo systemctl restart NetworkManager",
    "ls -la",
    "sudo dnf update",
    "g++ main.cpp -o main",
]
matches = [i for i, h in enumerate(history) if h.startswith("su")]
newest_first = list(reversed(matches))  # sudo dnf update, restart NM, status sshd

# timeline: (time, event)
events = [
    (0.45, "type", "s"),
    (0.85, "type", "u"),
    (1.50, "up", None),
    (2.35, "up", None),
    (3.20, "up", None),
    (4.05, "down", None),
]

def state(t):
    typed = ""
    idx = -1          # -1 = no history selection
    pressed = None
    for (et, kind, val) in events:
        if t >= et:
            if kind == "type":
                typed += val
            elif kind == "up":
                idx = min(idx + 1, len(newest_first) - 1)
                if t - et < 0.22: pressed = "up"
            elif kind == "down":
                idx = max(idx - 1, -1) if idx > 0 else idx
                if t - et < 0.22: pressed = "down"
    if idx >= 0:
        line = history[newest_first[idx]]
        sel = newest_first[idx]
    else:
        line, sel = typed, None
    return typed, line, sel, pressed

def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def render(i):
    t = i / FPS
    typed, line, sel, pressed = state(t)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- terminal window
    tx0, ty0, tx1, ty1 = 30, 30, 610, 420
    rounded(d, (tx0, ty0, tx1, ty1), 14, PANEL)
    d.rounded_rectangle((tx0, ty0, tx1, ty0 + 44), 14, fill=BAR)
    d.rectangle((tx0, ty0 + 24, tx1, ty0 + 44), fill=BAR)
    for k, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((tx0 + 18 + k * 26, ty0 + 14, tx0 + 32 + k * 26, ty0 + 28), fill=c)
    d.text((tx0 + 130, ty0 + 10), "bash", font=f_title, fill=DIM)

    # prompt line
    px, py = tx0 + 24, ty0 + 90
    d.text((px, py), "$ ", font=f_term, fill=GREEN)
    pw = d.textlength("$ ", font=f_term)
    cw = d.textlength("M", font=f_term)
    # typed prefix highlighted, rest normal
    n = len(typed)
    shown_prefix = line[:n] if sel is not None else line
    rest = line[n:] if sel is not None else ""
    d.text((px + pw, py), shown_prefix, font=f_term, fill=ACCENT if n else FG)
    d.text((px + pw + cw * len(shown_prefix), py), rest, font=f_term, fill=FG)
    # blinking cursor
    if int(t * 2.5) % 2 == 0:
        cx = px + pw + cw * len(line)
        d.rectangle((cx + 2, py + 3, cx + 13, py + 28), fill=FG)

    # hint under prompt
    if sel is None and typed:
        hint = "now press  ↑"
        hc = ACCENT
    elif sel is not None:
        hint = "matches in history: %d of %d" % (newest_first.index(sel) + 1, len(newest_first))
        hc = BLUE
    else:
        hint = "type a command prefix..."
        hc = DIM
    d.text((px, py + 70), hint, font=f_small, fill=hc)

    # ---- history panel
    hx0, hy0, hx1, hy1 = 640, 30, 970, 420
    rounded(d, (hx0, hy0, hx1, hy1), 14, PANEL)
    d.text((hx0 + 20, hy0 + 14), "history", font=f_title, fill=DIM)
    d.text((hx1 - 100, hy0 + 17), "oldest→", font=f_small, fill=DIM)
    for r, h in enumerate(history):
        ry = hy0 + 64 + r * 44
        is_match = typed and h.startswith(typed)
        if sel == r:
            rounded(d, (hx0 + 10, ry - 6, hx1 - 10, ry + 32), 8, (60, 52, 24), outline=ACCENT, width=2)
            col = ACCENT
        else:
            col = FG if (is_match or not typed) else (62, 66, 84)
        txt = h if len(h) <= 24 else h[:23] + "…"
        d.text((hx0 + 22, ry), txt, font=f_small, fill=col)

    # ---- keycaps
    kx = 30
    ky = 440
    for name, glyph, x in (("up", "↑", 640), ("down", "↓", 720)):
        on = pressed == name
        rounded(d, (x, ky, x + 64, ky + 64), 12, ACCENT if on else KEY_BG,
                outline=(255, 230, 150) if on else (70, 76, 100), width=2)
        gw = d.textlength(glyph, font=f_key)
        d.text((x + 32 - gw / 2, ky + 12), glyph, font=f_key, fill=(20, 20, 20) if on else FG)

    # ---- caption
    d.text((kx, 448), "history-prefix-search", font=f_title, fill=FG)
    d.text((kx, 482), "type a prefix, then press ↑", font=f_cap, fill=DIM)
    return img

frames_dir = "frames"
shutil.rmtree(frames_dir, ignore_errors=True)
os.makedirs(frames_dir)
frames = []
for i in range(N):
    im = render(i)
    im.save(f"{frames_dir}/f{i:03d}.png")
    frames.append(im)

# GIF (for README)
pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
pal[0].save("history-prefix-search-demo.gif", save_all=True, append_images=pal[1:],
            duration=int(1000 / FPS), loop=0, optimize=True)
print("frames", N)

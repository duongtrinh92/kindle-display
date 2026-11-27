import json, sys
from PIL import Image, ImageDraw, ImageFont
W, H, M = 1072, 1448, 48
D = "/usr/share/fonts/opentype/inter/"
def F(w, s): return ImageFont.truetype(D + f"Inter-{w}.otf", s)
data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "data.json", encoding="utf-8"))
out = sys.argv[2] if len(sys.argv) > 2 else "kindle.png"
im = Image.new("L", (W, H), 255); d = ImageDraw.Draw(im)
def fit(t, f, mw):
    if d.textlength(t, font=f) <= mw: return t
    while t and d.textlength(t + "…", font=f) > mw: t = t[:-1]
    return t + "…"
def rtext(x, y, t, f, fill=0): d.text((x - d.textlength(t, font=f), y), t, font=f, fill=fill)
def rule(y, w=4): d.rectangle([M, y, W - M, y + w - 1], fill=0)
def bar(x, y, w, h, pct, ticks=0):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, outline=0, width=4, fill=255)
    fw = max(h, int(w * pct / 100)) if pct else 0
    if pct is not None and fw: d.rounded_rectangle([x, y, x + fw, y + h], radius=h // 2, fill=0)
    for i in range(1, ticks + 1):
        tx = x + w * i // (ticks + 1); d.line([tx, y + h + 6, tx, y + h + 22], fill=120, width=3)
def head(y, title, right=""):
    d.text((M, y), title, font=F("Bold", 30), fill=0)
    if right: rtext(W - M, y + 4, right, F("Regular", 26), 110)
    rule(y + 46, 3); return y + 62
u = data["usage"]
d.text((M, 34), "Claude", font=F("Black", 64), fill=0)
rtext(W - M, 34, f"CẬP NHẬT · {data['updated']}", F("Bold", 28))
wx = data["weather"]; rtext(W - M, 74, f"Trời {wx['temp']} · {wx['desc']} · AQI {wx['aqi']}", F("Regular", 24), 90)
rule(120, 6)
d.text((M - 4, 118), f"{u['week_pct']:02d}%", font=F("Black", 230), fill=0)
x2 = 640
d.text((x2, 160), "TUẦN NÀY", font=F("Black", 40), fill=0)
d.text((x2, 216), u["week_label"], font=F("Bold", 38), fill=70)
d.text((x2, 270), u["week_reset"], font=F("Regular", 28), fill=70)
bar(M, 345, W - 2 * M, 38, u["week_pct"], 3)
rtext(W - M, 402, f"đã trôi {u['week_elapsed_pct']}% thời gian ▲", F("Regular", 24), 110)
y = 448; half = (W - 2 * M - 40) // 2
d.text((M, y), "Phiên 5 giờ", font=F("Bold", 32), fill=0); rtext(M + half, y - 4, f"{u['session_pct']}%", F("Black", 40))
bar(M, y + 50, half, 24, u["session_pct"]); d.text((M, y + 92), u["session_reset"], font=F("Regular", 23), fill=110)
x3 = M + half + 40
d.text((x3, y), "Fable", font=F("Bold", 32), fill=0)
fp = u["fable_pct"]; rtext(x3 + half, y - 4, "--" if fp is None else f"{fp}%", F("Black", 40))
bar(x3, y + 50, half, 24, fp or 0); d.text((x3, y + 92), "chưa có số liệu Fable" if fp is None else "", font=F("Regular", 23), fill=110)
y = 584
# Claude jobs
s = data["sessions"]; jobs = data["claude_jobs"]
bad = sum(1 for j in jobs if j["state"] != "ok")
y = head(y, "CLAUDE ĐANG LÀM", f"{len(jobs)} tác vụ · {s['running']} phiên chạy · {bad} lỗi")
for j in jobs:
    ok = j["state"] == "ok"
    d.ellipse([M, y + 12, M + 24, y + 36], fill=0 if ok else 255, outline=0, width=4)
    d.text((M + 42, y + 4), fit(j["name"], F("Medium", 30), 520), font=F("Medium", 30), fill=0)
    rtext(W - M, y + 8, f"xong {j['last']} · tiếp {j['next']}" if ok else f"LỖI · {j['last']}", F("Regular", 24), 90)
    y += 46
y += 10
un = data["unread"]
y = head(y, "BẢN TIN CHƯA ĐỌC", f"{len(un)} thư")
for n in un[:3]:
    d.rectangle([M, y + 12, M + 22, y + 34], fill=0)
    d.text((M + 42, y + 2), fit(n["title"], F("Medium", 28), 700), font=F("Medium", 28), fill=0)
    rtext(W - M, y + 8, n["from"], F("Regular", 22), 110); y += 44
y += 10
y = head(y, "VIỆC CẦN LÀM", f"{len(data['tasks']) + data['tasks_more']} việc")
for t in data["tasks"][:3]:
    d.rounded_rectangle([M, y + 6, M + 30, y + 36], radius=6, outline=0, width=4)
    d.text((M + 48, y + 4), fit(t["t"], F("Regular", 28), 640), font=F("Regular", 28), fill=0)
    f = F("Bold", 22); tw = d.textlength(t["tag"], font=f) + 30; hot = t["tag"] in ("Quá hạn", "Hôm nay")
    d.rounded_rectangle([W - M - tw, y + 6, W - M, y + 38], radius=16, fill=0 if hot else 255, outline=0, width=3)
    d.text((W - M - tw + 15, y + 9), t["tag"], font=f, fill=255 if hot else 0); y += 44
if data["tasks_more"]: d.text((M, y), f"+ {data['tasks_more'] + len(data['tasks']) - 3} việc nữa", font=F("Regular", 24), fill=110); y += 38
y += 10
# calendar two columns
col = (W - 2 * M - 30) // 2
for i, (title, ev) in enumerate((("HÔM NAY", data["today"]), ("NGÀY MAI", data["tomorrow"]))):
    x = M + i * (col + 30); yy = y
    d.text((x, yy), title, font=F("Bold", 26), fill=0); d.rectangle([x, yy + 38, x + col, yy + 40], fill=0); yy += 50
    for e in ev[:2]:
        d.text((x, yy), e["time"], font=F("Bold", 22), fill=0)
        d.text((x + 70, yy), fit(e["t"], F("Regular", 22), col - 74), font=F("Regular", 22), fill=40); yy += 34
    if not ev: d.text((x, yy), "Không có sự kiện", font=F("Regular", 22), fill=120)
w = data["weather"]
im.save(out); print("ok", out)

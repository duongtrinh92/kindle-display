# Tạo phone.png (1080x2400) từ kindle.png: đặt dưới đồng hồ màn hình khóa
import sys
from PIL import Image
src = Image.open(sys.argv[1] if len(sys.argv) > 1 else "kindle.png").convert("L")
W, H, top = 1080, 2400, 560
card_w = 1000
card = src.resize((card_w, int(src.height * card_w / src.width)), Image.LANCZOS)
im = Image.new("L", (W, H), 255)
im.paste(card, ((W - card_w) // 2, top))
im.save(sys.argv[2] if len(sys.argv) > 2 else "phone.png"); print("ok")

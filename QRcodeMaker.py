import qrcode

img = qrcode.make ("https://youtu.be/6rmErwU5E-k")
img.save("SolderingQRcode.png")
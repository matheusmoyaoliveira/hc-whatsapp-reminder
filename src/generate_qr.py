import qrcode

data = "https://prototipo-challenge-hc-2025.vercel.app/"

img = qrcode.make(data)

output_file = "qrcode_demo.png"
img.save(output_file)

print(f"✅ QR Code gerado: {output_file}")
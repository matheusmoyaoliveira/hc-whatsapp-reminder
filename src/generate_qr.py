import qrcode

data = "https://hcclinicas.org/teleconsulta/demo"

img = qrcode.make(data)

output_file = "qrcode_demo.png"
img.save(output_file)

print(f"✅ QR Code gerado: {output_file}")
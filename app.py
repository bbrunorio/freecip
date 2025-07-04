# Fonte com tamanho fixo grande (visível) e compatível com Streamlit Cloud
try:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 60  # Fixado para garantir legibilidade
    font = ImageFont.truetype(font_path, font_size)
except:
    font = ImageFont.load_default()

for i, pct in enumerate(percentages):
    x = i * sector_w
    draw.line([(x, 0), (x, h)], fill="red", width=1)
    text = f"{pct}%"
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except:
        text_w, text_h = draw.textsize(text, font=font)
    draw.text((x + (sector_w - text_w) // 2, h - text_h - 10), text, fill="blue", font=font)

# Substituir a linha abaixo:
# st.image(out, caption="Resultado com setores e porcentagens", use_column_width=True)
# Por esta:
st.image(out, caption="Resultado com setores e porcentagens", use_container_width=True)

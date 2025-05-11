from PIL import Image
import os

def hide_gif_in_image(gif_path, cover_image_path, output_image_path):
    # Otvori sliku
    cover_image = Image.open(cover_image_path)
    cover_image = cover_image.convert('RGB')
    width, height = cover_image.size

    # Otvori GIF datoteku
    with open(gif_path, 'rb') as gif_file:
        gif_data = gif_file.read()

    # Provjeri je li veličina GIF datoteke prevelika za sliku
    max_bytes_available = (width * height * 3) // 8
    if len(gif_data) > max_bytes_available:
        raise ValueError("GIF datoteka je prevelika za skrivanje u sliku.")

    # Dodaj veličinu GIF datoteke na početak GIF podataka
    gif_size = len(gif_data)
    gif_data = gif_size.to_bytes(4, byteorder='big') + gif_data

    # Pretvori binarne podatke u binarni niz
    binary_data = ''.join(format(byte, '08b') for byte in gif_data)

    # Upiši binarne podatke u piksele slike (LSB zamjena)
    pixels = cover_image.load()
    index = 0
    for x in range(width):
        for y in range(height):
            if index >= len(binary_data):
                break
            r, g, b = pixels[x, y]
            if index < len(binary_data):
                r = (r & ~1) | int(binary_data[index])
                index += 1
            if index < len(binary_data):
                g = (g & ~1) | int(binary_data[index])
                index += 1
            if index < len(binary_data):
                b = (b & ~1) | int(binary_data[index])
                index += 1
            pixels[x, y] = (r, g, b)
        if index >= len(binary_data):
            break

    # Spremi kodiranu sliku
    cover_image.save(output_image_path)
    print(f"GIF datoteka '{os.path.basename(gif_path)}' skrivena u slici '{os.path.basename(cover_image_path)}' i spremljena kao '{os.path.basename(output_image_path)}'.")

def extract_gif_from_image(encoded_image_path, output_gif_path):
    # Otvori kodiranu sliku
    encoded_image = Image.open(encoded_image_path)
    encoded_image = encoded_image.convert('RGB')
    width, height = encoded_image.size

    # Izvuci binarne podatke iz piksela slike (LSB ekstrakcija)
    binary_data = []
    for x in range(width):
        for y in range(height):
            r, g, b = encoded_image.getpixel((x, y))
            binary_data.append(r & 1)
            binary_data.append(g & 1)
            binary_data.append(b & 1)

    # Pretvori binarne podatke u bajtove
    binary_data = ''.join(map(str, binary_data))
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    gif_data = bytes([int(byte, 2) for byte in byte_data])

    # Dobavi originalnu veličinu GIF datoteke iz prva 4 bajta
    gif_size = int.from_bytes(gif_data[:4], byteorder='big')

    # Spremi izdvojene binarne podatke kao GIF
    with open(output_gif_path, 'wb') as gif_file:
        gif_file.write(gif_data[4:4 + gif_size])
    
    print(f"GIF datoteka izdvojena iz '{os.path.basename(encoded_image_path)}' i spremljena kao '{os.path.basename(output_gif_path)}'.")

#Podaci za kodiranje i dekodiranje
gif_path = '13.gif'  # Putanja do GIF datoteke
cover_image_path = '3.png'  # Putanja do slike za skrivanje GIF datoteke
output_image_path = 'slika_sa_porukom.png'  # Naziv za spremljenu kodiranu sliku

hide_gif_in_image(gif_path, cover_image_path, output_image_path)

encoded_image_path = 'slika_sa_porukom.png'  # Putanja do kodirane slike
output_gif_path = 'dekodirani_gif.gif'  # Naziv za spremljeni dekodirani GIF

extract_gif_from_image(encoded_image_path, output_gif_path)

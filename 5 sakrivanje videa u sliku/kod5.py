from PIL import Image
import os

def hide_video_in_image(video_path, cover_image_path, output_image_path):
    # Otvori sliku
    cover_image = Image.open(cover_image_path)

    # Pretvori sliku u RGB (ako već nije)
    cover_image = cover_image.convert('RGB')

    # Uzmi veličinu slike u pikselima
    width, height = cover_image.size

    # Otvori video datoteku koju treba sakriti
    with open(video_path, 'rb') as video_file:
        video_data = video_file.read()

    # Provjeri je li veličina video datoteke prevelika za sliku
    max_bytes_available = (width * height * 3) // 8
    if len(video_data) > max_bytes_available:
        raise ValueError("Veličina video datoteke je prevelika za sakrivanje u slici.")

    # Dodaj veličinu video datoteke na početak video podataka (da bi se znalo gdje stati prilikom vađenja)
    video_size = len(video_data)
    video_data = video_size.to_bytes(4, byteorder='big') + video_data

    # Pretvori video podatke u binarni oblik
    video_binary_data = ''.join(format(byte, '08b') for byte in video_data)

    # Upiši video podatke u piksele slike (LSB zamjena)
    pixels = cover_image.load()
    index = 0
    for x in range(width):
        for y in range(height):
            # Dobavi RGB vrijednosti piksela
            r, g, b = pixels[x, y]

            # Promijeni najmanje značajni bit (LSB) svake komponente boje
            if index < len(video_binary_data):
                r = r & ~1 | int(video_binary_data[index])
                index += 1
            if index < len(video_binary_data):
                g = g & ~1 | int(video_binary_data[index])
                index += 1
            if index < len(video_binary_data):
                b = b & ~1 | int(video_binary_data[index])
                index += 1

            # Ažuriraj piksel sa modificiranim RGB vrijednostima
            pixels[x, y] = (r, g, b)

            # Prekini kodiranje kada su svi podaci kodirani
            if index >= len(video_binary_data):
                break
        else:
            continue
        break

    # Spremi kodiranu sliku
    cover_image.save(output_image_path)

    print(f"Video datoteka '{os.path.basename(video_path)}' skrivena u slici '{os.path.basename(cover_image_path)}' i spremljena kao '{os.path.basename(output_image_path)}'.")

def extract_video_from_image(encoded_image_path, output_video_path):
    # Otvori kodiranu sliku
    encoded_image = Image.open(encoded_image_path)

    # Pretvori kodiranu sliku u RGB (ako već nije u tom modu)
    encoded_image = encoded_image.convert('RGB')

    # Dobavi veličinu slike u pikselima
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
    binary_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    binary_data = bytes([int(byte, 2) for byte in binary_data])

    # Dobavi originalnu veličinu video datoteke iz prvih 4 bajta
    video_size = int.from_bytes(binary_data[:4], byteorder='big')

    # Spremi izdvojene video podatke
    with open(output_video_path, 'wb') as video_file:
        video_file.write(binary_data[4:4 + video_size])

    print(f"Video datoteka izdvojena iz '{os.path.basename(encoded_image_path)}' i spremljena kao '{os.path.basename(output_video_path)}'.")

# Podaci za kodiranje i dekodiranje
video_path = '12.mp4'  # Putanja do video datoteke
cover_image_path = '3.png'  # Putanja do slike za skrivanje video datoteke
output_image_path = 'slika_sa_porukom.png'  # Naziv za spremljenu kodiranu sliku

hide_video_in_image(video_path, cover_image_path, output_image_path)

encoded_image_path = 'slika_sa_porukom.png'  # Putanja do kodirane slike
output_video_path = 'dekodirani_video.mp4'  # Naziv za spremljeni dekodirani video

extract_video_from_image(encoded_image_path, output_video_path)

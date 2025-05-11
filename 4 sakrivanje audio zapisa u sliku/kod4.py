from PIL import Image
import os

def hide_audio_in_image(audio_file_path, cover_image_path, output_image_path):
    # Otvori sliku
    cover_image = Image.open(cover_image_path)

    # Pretvori sliku u RGB (ako već nije)
    cover_image = cover_image.convert('RGB')

    # Dobij veličinu slike u pikselima
    width, height = cover_image.size

    # Otvori audio datoteku koju treba sakriti
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    # Provjeri je li veličina audio datoteke prevelika za sliku
    max_bytes_available = (width * height * 3) // 8
    if len(audio_data) > max_bytes_available:
        raise ValueError("Audio datoteka je prevelika za sakriti u sliku.")

    # Dodaj veličinu audio datoteke na početak podataka (kako bi se znalo gdje stati prilikom ekstrakcije)
    audio_size = len(audio_data)
    audio_data = audio_size.to_bytes(4, byteorder='big') + audio_data

    # Pretvori podatke audio datoteke u binarni oblik
    audio_binary_data = ''.join(format(byte, '08b') for byte in audio_data)

    # Kodiraj podatke audio datoteke u piksele slike (LSB zamjena)
    pixels = cover_image.load()
    index = 0
    for x in range(width):
        for y in range(height):
            # Dobij RGB vrijednosti piksela
            r, g, b = pixels[x, y]

            # Modificiraj najmanje značajan bit (LSB) svake komponente boje
            if index < len(audio_binary_data):
                r = r & ~1 | int(audio_binary_data[index])
                index += 1
            if index < len(audio_binary_data):
                g = g & ~1 | int(audio_binary_data[index])
                index += 1
            if index < len(audio_binary_data):
                b = b & ~1 | int(audio_binary_data[index])
                index += 1

            # Ažuriraj piksel s modificiranim RGB vrijednostima
            pixels[x, y] = (r, g, b)

            # Prestani kodirati kada su svi podaci kodirani
            if index >= len(audio_binary_data):
                break
        else:
            continue
        break

    # Spremi kodiranu sliku
    cover_image.save(output_image_path)

    print(f"Audio datoteka '{os.path.basename(audio_file_path)}' skrivena u slici '{os.path.basename(cover_image_path)}' i spremljena kao '{os.path.basename(output_image_path)}'.")

def extract_audio_from_image(encoded_image_path, output_audio_path):
    # Otvori kodiranu sliku
    encoded_image = Image.open(encoded_image_path)

    # Pretvori kodiranu sliku u RGB (ako već nije)
    encoded_image = encoded_image.convert('RGB')

    # Dobij veličinu slike u pikselima
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

    # Dobij originalnu veličinu audio datoteke iz prvih 4 bajta
    audio_size = int.from_bytes(binary_data[:4], byteorder='big')

    # Spremi izvučene podatke audio datoteke
    with open(output_audio_path, 'wb') as audio_file:
        audio_file.write(binary_data[4:4 + audio_size])

    print(f"Audio datoteka izvučena iz '{os.path.basename(encoded_image_path)}' i spremljena kao '{os.path.basename(output_audio_path)}'.")

# Glavna funkcija za kodiranje i dekodiranje
if __name__ == "__main__":
    # Sakrij audio datoteku u slici
    hide_audio_in_image('1.wav', '3.png', 'slika_sa_porukom.png')

    # Izvuci audio datoteku iz kodirane slike
    extract_audio_from_image('slika_sa_porukom.png', 'dekodirani_audio.wav')

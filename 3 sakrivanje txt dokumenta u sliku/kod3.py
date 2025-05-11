from PIL import Image
import os

def hide_file_in_image(file_path, cover_image_path, output_image_path):
    # Otvori sliku
    cover_image = Image.open(cover_image_path)

    # Pretvori sliku u RGB (ako već nije)
    cover_image = cover_image.convert('RGB')

    # Dobij veličinu slike u pikselima
    width, height = cover_image.size

    # Otvori datoteku koju treba sakriti
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Dodaj veličinu datoteke na početak podataka datoteke (kako bi se znalo gdje stati prilikom ekstrakcije)
    file_size = len(file_data)
    file_data = file_size.to_bytes(4, byteorder='big') + file_data

    # Provjeri je li veličina datoteke prevelika za sliku
    max_bytes_available = (width * height * 3) // 8
    if len(file_data) > max_bytes_available:
        raise ValueError("Datoteka je prevelika za sakriti u sliku.")

    # Pretvori podatke datoteke u binarni oblik
    file_binary_data = ''.join(format(byte, '08b') for byte in file_data)

    # Kodiraj podatke datoteke u piksele slike (LSB zamjena)
    pixels = cover_image.load()
    index = 0
    for x in range(width):
        for y in range(height):
            # Dobij RGB vrijednosti piksela
            r, g, b = pixels[x, y]

            # Modificiraj najmanje značajan bit svake komponente boje
            if index < len(file_binary_data):
                r = r & ~1 | int(file_binary_data[index])
                index += 1
            if index < len(file_binary_data):
                g = g & ~1 | int(file_binary_data[index])
                index += 1
            if index < len(file_binary_data):
                b = b & ~1 | int(file_binary_data[index])
                index += 1

            # Ažuriraj piksel s modificiranim RGB vrijednostima
            pixels[x, y] = (r, g, b)

            # Prestani kodirati kada su svi podaci kodirani
            if index >= len(file_binary_data):
                break
        else:
            continue
        break

    # Spremi kodiranu sliku
    cover_image.save(output_image_path)

    print(f"Datoteka '{os.path.basename(file_path)}' skrivena u slici '{os.path.basename(cover_image_path)}' i spremljena kao '{os.path.basename(output_image_path)}'.")

def extract_file_from_image(encoded_image_path, output_file_path):
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

    # Dobij originalnu veličinu datoteke iz prva 4 bajta
    file_size = int.from_bytes(binary_data[:4], byteorder='big')

    # Spremi izvucene podatke datoteke
    with open(output_file_path, 'wb') as file:
        file.write(binary_data[4:4 + file_size])

    print(f"Datoteka dekodirana iz '{os.path.basename(encoded_image_path)}' i spremljena kao '{os.path.basename(output_file_path)}'.")

# Glavna funkcija za kodiranje i dekodiranje
if __name__ == "__main__":
    # Sakrij datoteku u sliku
    hide_file_in_image('prvi.txt', '1.png', 'slika_sa_porukom.png')

    # Dekodiraj datoteku iz kodirane slike
    extract_file_from_image('slika_sa_porukom.png', 'dekodirana_datoteka.txt')

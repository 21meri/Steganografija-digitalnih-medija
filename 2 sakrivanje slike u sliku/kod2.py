from PIL import Image

def encode_image(cover_image_path, secret_image_path, output_image_path):
    # Otvara slike
    cover_image = Image.open(cover_image_path)
    secret_image = Image.open(secret_image_path)

    # Pretvara slike u RGB (ako već nisu)
    cover_image = cover_image.convert('RGB')
    secret_image = secret_image.convert('RGB')

    # Mijenja veličinu tajne slike da odgovara glavnoj slici, ako je potrebno
    secret_image = secret_image.resize(cover_image.size)

    # Stvara izlaznu sliku iste veličine i načina kao i glavna slika
    encoded_image = Image.new('RGB', cover_image.size)

    # Iterira kroz svaki piksel glavne i tajne slike
    for x in range(cover_image.width):
        for y in range(cover_image.height):
            # Dobiva RGB vrijednosti piksela
            cover_pixel = cover_image.getpixel((x, y))
            secret_pixel = secret_image.getpixel((x, y))

            # Stvara novu vrijednost piksela koristeći najmanje značajne bitove glavne slike i RGB vrijednosti tajne slike
            new_pixel = (
                cover_pixel[0] & 0b11111110 | (secret_pixel[0] >> 7),
                cover_pixel[1] & 0b11111110 | (secret_pixel[1] >> 7),
                cover_pixel[2] & 0b11111110 | (secret_pixel[2] >> 7)
            )

            # Postavlja piksel u izlaznu sliku
            encoded_image.putpixel((x, y), new_pixel)

    # Sprema kodiranu sliku
    encoded_image.save(output_image_path)

    print(f"Enkodirana slika je spremljena kao: {output_image_path}")

def decode_image(encoded_image_path, output_secret_image_path):
    # Otvara kodiranu sliku
    encoded_image = Image.open(encoded_image_path)

    # Stvara novu sliku za pohranu izdvojene tajne slike
    secret_image = Image.new('RGB', encoded_image.size)

    # Iterira kroz svaki piksel kodirane slike
    for x in range(encoded_image.width):
        for y in range(encoded_image.height):
            # Dobiva RGB vrijednost piksela
            encoded_pixel = encoded_image.getpixel((x, y))

            # Izdvaja najmanje značajne bitove za rekonstrukciju piksela tajne slike
            secret_pixel = (
                (encoded_pixel[0] & 0b00000001) << 7,
                (encoded_pixel[1] & 0b00000001) << 7,
                (encoded_pixel[2] & 0b00000001) << 7
            )

            # Postavlja piksel u tajnu sliku
            secret_image.putpixel((x, y), secret_pixel)

    # Sprema izdvojenu tajnu sliku
    secret_image.save(output_secret_image_path)

    print(f"Dekodirana skrivena slika je spremljena kao: {output_secret_image_path}")

# Glavna funkcija za kodiranje i dekodiranje
def main():
    encode_image('2.png', '1.png', 'slika_sa_porukom.png')  # Kodira tajnu sliku u glavnu sliku
    decode_image('slika_sa_porukom.png', 'skrivena_slika_iz_slike.png')  # Dekodira tajnu sliku iz kodirane slike

if __name__ == "__main__":
    main()

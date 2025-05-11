from PIL import Image, ImageSequence
import numpy as np

def image_to_binary(image_path):
    # Otvaranje slike i pretvorba u RGB format
    img = Image.open(image_path).convert('RGB')
    
    # Pretvaranje piksela slike u binarni niz
    pixels = np.array(img)
    binary_data = ''.join(format(pixel, '08b') for pixel in pixels.flatten())
    
    # Vraćanje binarnih podataka i veličine slike
    return binary_data, img.size

def binary_to_image(binary_data, size):
    # Pretvaranje binarnih podataka u vrijednosti piksela
    pixel_data = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    
    # Kreiranje numpy arraya od podataka piksela i pretvaranje natrag u sliku
    pixel_array = np.array(pixel_data, dtype=np.uint8).reshape((size[1], size[0], 3))
    return Image.fromarray(pixel_array)

def encode_image(gif_path, image_path, output_path):
    # Pretvorba slike u binarni oblik i dobivanje veličine slike
    binary_data, size = image_to_binary(image_path)
    
    # Zapisivanje duljine podataka i dimenzija slike u binarnom obliku
    data_length = format(len(binary_data), '032b')  # 32-bitna duljina podataka
    binary_data = data_length + format(size[0], '016b') + format(size[1], '016b') + binary_data

    # Otvaranje GIF slike
    img = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
    modified_frames = []

    # Provjera može li GIF slika pohraniti binarne podatke
    total_pixels = sum(frame.size[0] * frame.size[1] * 3 for frame in frames)  # RGB ima 3 kanala
    if len(binary_data) > total_pixels:
        raise ValueError("Slika je prevelika za sakriti u ovom GIF-u.")

    binary_index = 0
    for frame in frames:
        pixels = np.array(frame)
        
        # Ako je slika u grayscale formatu (2D array)
        if pixels.ndim == 2:
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    if binary_index < len(binary_data):
                        # Postavljanje LSB-a piksela prema binarnim podacima
                        pixels[row, col] = (pixels[row, col] & 0xFE) | int(binary_data[binary_index])
                        binary_index += 1
                        
        # Ako je slika u RGB formatu (3D array)
        elif pixels.ndim == 3:
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        if binary_index < len(binary_data):
                            # Postavljanje LSB-a kanala prema binarnim podacima
                            pixels[row, col, color] = (pixels[row, col, color] & 0xFE) | int(binary_data[binary_index])
                            binary_index += 1
        else:
            raise ValueError("Nepodržani format slike")

        # Dodavanje modificiranog framea u listu frameova
        modified_frame = Image.fromarray(pixels)
        modified_frames.append(modified_frame)

    # Spremanje novog GIF-a s skrivenom slikom
    modified_frames[0].save(output_path, save_all=True, append_images=modified_frames[1:], loop=img.info['loop'], duration=img.info['duration'])

def decode_image(gif_path):
    # Otvaranje GIF slike za dekodiranje
    img = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

    binary_data = ''  # Varijabla za pohranu izvučenih binarnih podataka
    for frame in frames:
        pixels = np.array(frame)
        
        # Ako je slika u grayscale formatu (2D array)
        if pixels.ndim == 2:
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    # Izvlačenje LSB-a iz svakog piksela
                    binary_data += str(pixels[row, col] & 1)
                    
        # Ako je slika u RGB formatu (3D array)
        elif pixels.ndim == 3:
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        # Izvlačenje LSB-a iz svakog kanala
                        binary_data += str(pixels[row, col, color] & 1)
        else:
            raise ValueError("Nepodržani format slike")

    # Izvlačenje duljine podataka
    data_length = int(binary_data[:32], 2)
    width = int(binary_data[32:48], 2)
    height = int(binary_data[48:64], 2)
    
    # Dobivanje podataka slike iz binarnih podataka
    image_data = binary_data[64:64+data_length]

    # Vraćanje slike iz binarnih podataka
    return binary_to_image(image_data, (width, height))

# Primjer korištenja za kodiranje slike u GIF
gif_path = '3.gif'
secret_image_path = '1.png'
output_gif_path = 'gif_sa_porukom.gif'

encode_image(gif_path, secret_image_path, output_gif_path)
print(f'Skrivena slika kodirana i spremljena u {output_gif_path}')

# Primjer korištenja za dekodiranje slike iz GIF-a
encoded_gif_path = 'gif_sa_porukom.gif'

decoded_image = decode_image(encoded_gif_path)
decoded_image.save('dekodirana_slika.png')  # Spremanje dekodirane slike
print(f'Skrivena slika dekodirana i spremljena kao dekodirana_slika.png')

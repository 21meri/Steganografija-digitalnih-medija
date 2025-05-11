from PIL import Image, ImageSequence
import numpy as np

def encode_message(image_path, message, output_path):
    # Pretvaranje poruke u binarni oblik
    # Svako slovo iz poruke pretvara se u 8-bitni binarni broj
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    
    # Dodavanje duljine poruke na početak binarnog niza
    # Duljina poruke je zapisana kao 32-bitni binarni broj
    message_length = format(len(binary_message), '032b')
    binary_message = message_length + binary_message

    # Otvaranje GIF-a
    img = Image.open(image_path)
    
    # Pretvorba svih frameova iz GIF-a u listu
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
    modified_frames = []

    # Provjera može li gif pohraniti cijelu poruku
    # Ukupni broj piksela pomnožen s 3 (za svaki RGB kanal) mora biti veći od duljine poruke
    total_pixels = sum(frame.size[0] * frame.size[1] * 3 for frame in frames)
    if len(binary_message) > total_pixels:
        raise ValueError("Poruka je preduga za sakriti u ovom GIF-u.")

    binary_index = 0  # Indeks koji prati trenutnu poziciju u binarnoj poruci
    for frame in frames:
        pixels = np.array(frame)
        
        # Ako je slika u grayscale formatu (2D array)
        if pixels.ndim == 2:
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    if binary_index < len(binary_message):
                        # Postavljanje LSB (najmanje značajnog bita) piksela prema poruci
                        pixels[row, col] = (pixels[row, col] & 0xFE) | int(binary_message[binary_index])
                        binary_index += 1
        
        # Ako je slika u RGB formatu (3D array)
        elif pixels.ndim == 3:
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        if binary_index < len(binary_message):
                            # Postavljanje LSB-a trenutnog kanala prema poruci
                            pixels[row, col, color] = (pixels[row, col, color] & 0xFE) | int(binary_message[binary_index])
                            binary_index += 1
        
        else:
            raise ValueError("Nepodržan format GIF-a.")

        # Dodavanje modificiranog framea u listu frameova
        modified_frame = Image.fromarray(pixels)
        modified_frames.append(modified_frame)

    # Spremanje novog GIF-a s sakrivenom porukom
    modified_frames[0].save(output_path, save_all=True, append_images=modified_frames[1:], loop=img.info['loop'], duration=img.info['duration'])

def decode_message(image_path):
    # Otvaranje GIF-a za dekodiranje
    img = Image.open(image_path)
    
    # Pretvorba svih frameova iz GIF-a u listu
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

    binary_message = ''  # Varijabla za pohranu izvučene binarne poruke
    for frame in frames:
        pixels = np.array(frame)
        
        # Ako je slika u grayscale formatu (2D array)
        if pixels.ndim == 2:
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    # Izvlačenje LSB-a iz svakog piksela
                    binary_message += str(pixels[row, col] & 1)
        
        # Ako je slika u RGB formatu (3D array)
        elif pixels.ndim == 3:
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        # Izvlačenje LSB-a iz svakog kanala
                        binary_message += str(pixels[row, col, color] & 1)
        
        else:
            raise ValueError("Nepodržani format GIF-a.")

    # Izvlačenje duljine poruke (prvih 32 bita)
    message_length = int(binary_message[:32], 2)
    
    # Dobivanje poruke pomoću dekodiranja preostalih bitova u znakove
    binary_message = binary_message[32:32 + message_length]
    chars = [chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)]
    message = ''.join(chars)

    return message

# Primjer korištenja za kodiranje poruke u GIF
input_gif_path = '6.gif'
secret_message = 'Ovo je skrivena poruka!'
output_gif_path = 'gif_sa_porukom.gif'

encode_message(input_gif_path, secret_message, output_gif_path)
print(f'Poruka je kodirana i spremljena u {output_gif_path}')

# Primjer korištenja za dekodiranje poruke iz GIF-a
encoded_gif_path = 'gif_sa_porukom.gif'

decoded_message = decode_message(encoded_gif_path)
print(f'Dekodirana poruka: {decoded_message}')

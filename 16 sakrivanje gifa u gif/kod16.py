from PIL import Image, ImageSequence
import numpy as np

def gif_to_binary(gif_path):
    #Pretvori GIF u binarne podatke.
    with Image.open(gif_path) as img:
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        binary_data = ''
        for frame in frames:
            frame = frame.convert('RGB')  # Konvertiranje svakog okvira u RGB format
            pixels = np.array(frame)
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Obrada svih RGB kanala
                        binary_data += str(pixels[row, col, color] & 1)  # Ekstrakcija najmanje značajnog bita svakog kanala
        return binary_data

def binary_to_gif(binary_data, output_path, frame_size, duration):
    #Pretvori binarne podatke natrag u GIF.
    num_frames = len(binary_data) // (frame_size[0] * frame_size[1] * 3)
    frames = []
    index = 0
    for _ in range(num_frames):
        frame_data = binary_data[index:index + (frame_size[0] * frame_size[1] * 3)]
        index += (frame_size[0] * frame_size[1] * 3)
        frame_array = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)  # Inicijalizacija matrice za piksele
        for row in range(frame_size[1]):
            for col in range(frame_size[0]):
                for color in range(3):
                    frame_array[row, col, color] = int(frame_data[(row * frame_size[0] + col) * 3 + color], 2) * 255  # Rekonstrukcija piksela iz binarnih podataka
        frames.append(Image.fromarray(frame_array, 'RGB'))  # Kreiranje slike iz matrice piksela
    
    # Spremanje okvira kao GIF
    frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=duration)

def encode_gif(outer_gif_path, inner_gif_path, output_gif_path):
    #Kodiraj jedan GIF unutar drugog.
    binary_data = gif_to_binary(inner_gif_path)  # Pretvori unutarnji GIF u binarne podatke
    img = Image.open(outer_gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

    frame_size = frames[0].size
    total_pixels = frame_size[0] * frame_size[1] * 3 * len(frames)
    if len(binary_data) > total_pixels:
        raise ValueError("Unutarnji GIF je prevelik da bi bio sakriven u ovom vanjskom GIF-u.")

    binary_index = 0
    modified_frames = []
    for frame in frames:
        frame = frame.convert('RGB')  # Konvertiranje svakog okvira u RGB format
        pixels = np.array(frame)
        height, width, _ = pixels.shape
        for row in range(height):
            for col in range(width):
                if binary_index < len(binary_data):
                    for color in range(3):
                        if binary_index < len(binary_data):
                            pixels[row, col, color] = (pixels[row, col, color] & 0xFE) | int(binary_data[binary_index])  # Zamjena najmanje značajnog bita
                            binary_index += 1
                else:
                    break
            if binary_index >= len(binary_data):
                break

        modified_frames.append(Image.fromarray(pixels, 'RGB'))  # Kreiranje okvira iz modificiranih piksela

    # Spremanje novog GIF-a s skrivenim GIF-om
    modified_frames[0].save(output_gif_path, save_all=True, append_images=modified_frames[1:], loop=img.info.get('loop', 0), duration=img.info.get('duration', 100))

def decode_gif(gif_path, output_inner_gif_path):
    #Dekodiraj skriveni GIF iz drugog GIF-a.
    img = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

    binary_data = ''
    for frame in frames:
        frame = frame.convert('RGB')  # Konvertiranje svakog okvira u RGB format
        pixels = np.array(frame)
        height, width, _ = pixels.shape
        for row in range(height):
            for col in range(width):
                for color in range(3):
                    binary_data += str(pixels[row, col, color] & 1)  # Ekstrakcija najmanje značajnog bita svakog kanala

    frame_size = frames[0].size
    duration = img.info.get('duration', 100)

    binary_to_gif(binary_data, output_inner_gif_path, frame_size, duration)  # Rekonstrukcija GIF-a iz binarnih podataka

# Primjer korištenja za kodiranje jednog GIF-a unutar drugog
outer_gif_path = '3.gif'
inner_gif_path = '6.gif'
output_gif_path = 'gif_sa_porukom.gif'

encode_gif(outer_gif_path, inner_gif_path, output_gif_path)
print(f'Skriveni GIF je kodiran i spremljen u {output_gif_path}')

# Primjer korištenja za dekodiranje GIF-a iz drugog GIF-a
encoded_gif_path = 'gif_sa_porukom.gif'
output_inner_gif_path = 'dekodirani_gif.gif'

decode_gif(encoded_gif_path, output_inner_gif_path)
print(f'Skriveni GIF je dekodiran i spremljen kao {output_inner_gif_path}')

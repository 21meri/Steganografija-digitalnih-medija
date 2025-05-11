from PIL import Image, ImageSequence
import numpy as np
import wave

def wav_to_binary(audio_path):
    # Otvaranje WAV datoteke i pretvaranje audio podataka u binarni oblik
    with wave.open(audio_path, 'rb') as wav_file:
        params = wav_file.getparams()  # Dohvatanje parametara audio datoteke (broj kanala, širina sample-a, itd.)
        frames = wav_file.readframes(params.nframes)  # Čitanje svih frame-ova iz audio datoteke
        binary_data = ''.join(format(byte, '08b') for byte in frames)  # Pretvorba frame-ova u binarni niz
    return binary_data, params

def binary_to_wav(binary_data, params, output_path):
    # Pretvaranje binarnih podataka natrag u audio frame-ove
    byte_data = bytearray(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setparams(params)  # Postavljanje parametara audio datoteke
        wav_file.writeframes(byte_data)  # Zapisivanje frame-ova u WAV datoteku

def encode_audio(gif_path, audio_path, output_path):
    # Pretvorba audio datoteke u binarni oblik
    binary_data, params = wav_to_binary(audio_path)
    data_length = format(len(binary_data), '032b')  # 32-bitni zapis duljine binarnih podataka
    binary_data = data_length + binary_data  # Dodavanje duljine podataka na početak binarnog niza

    # Otvaranje GIF slike
    img = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
    modified_frames = []

    # Provjera može li GIF slika pohraniti binarne podatke
    total_pixels = sum(frame.size[0] * frame.size[1] * 3 for frame in frames)  # RGB ima 3 kanala
    if len(data_length + binary_data) > total_pixels:
        raise ValueError("Audio datoteka je prevelika za sakriti u ovom GIF-u.")

    binary_index = 0
    for frame in frames:
        pixels = np.array(frame)
        if pixels.ndim == 2:  # Ako je slika u grayscale formatu (2D array)
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    if binary_index < len(binary_data):
                        # Postavljanje LSB-a piksela prema binarnim podacima
                        pixels[row, col] = (pixels[row, col] & 0xFE) | int(binary_data[binary_index])
                        binary_index += 1
        elif pixels.ndim == 3:  # Ako je slika u RGB formatu (3D array)
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        if binary_index < len(binary_data):
                            # Postavljanje LSB-a kanala prema binarnim podacima
                            pixels[row, col, color] = (pixels[row, col, color] & 0xFE) | int(binary_data[binary_index])
                            binary_index += 1
        else:
            raise ValueError("Nepodržani format GIF-a")

        # Dodavanje modificiranog frame-a u listu frame-ova
        modified_frame = Image.fromarray(pixels)
        modified_frames.append(modified_frame)

    # Spremanje novog GIF-a s skrivenim audio zapisom
    modified_frames[0].save(output_path, save_all=True, append_images=modified_frames[1:], loop=img.info['loop'], duration=img.info['duration'])

def decode_audio(gif_path, output_audio_path):
    # Otvaranje GIF slike za dekodiranje
    img = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

    binary_data = ''  # Varijabla za pohranu izvučenih binarnih podataka
    for frame in frames:
        pixels = np.array(frame)
        if pixels.ndim == 2:  # Ako je slika u grayscale formatu (2D array)
            height, width = pixels.shape
            for row in range(height):
                for col in range(width):
                    # Izvlačenje LSB-a iz svakog piksela
                    binary_data += str(pixels[row, col] & 1)
        elif pixels.ndim == 3:  # Ako je slika u RGB formatu (3D array)
            height, width, _ = pixels.shape
            for row in range(height):
                for col in range(width):
                    for color in range(3):  # Za svaki RGB kanal
                        # Izvlačenje LSB-a iz svakog kanala
                        binary_data += str(pixels[row, col, color] & 1)
        else:
            raise ValueError("Nepodržani format GIF-a")

    # Izvlačenje duljine podataka
    data_length = int(binary_data[:32], 2)
    audio_data = binary_data[32:32 + data_length]

    # Postavljanje audio parametara iz GIF metapodataka ili ručno
    params = (1, 1, 44100, len(audio_data) // 8, 'NONE', 'not compressed')
    binary_to_wav(audio_data, params, output_audio_path)

    return output_audio_path

# Primjer korištenja za kodiranje audio datoteke u GIF
gif_path = '3.gif'
audio_path = '1.wav'
output_gif_path = 'gif_sa_porukom.gif'

encode_audio(gif_path, audio_path, output_gif_path)
print(f'Skriveni audio kodiran i spremljen u {output_gif_path}')

# Primjer korištenja za dekodiranje audio datoteke iz GIF-a
encoded_gif_path = 'gif_sa_porukom.gif'
output_audio_path = 'dekodirani_audio.wav'

decode_audio(encoded_gif_path, output_audio_path)
print(f'Skriveni audio dekodiran i spremljen kao {output_audio_path}')

import wave
import numpy as np

# Funkcija za pretvaranje teksta u binarni oblik
# Svako slovo teksta pretvara se u odgovarajući 8-bitni binarni kod koristeći ASCII vrijednost
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

# Funkcija za skrivanje teksta u audio datoteci koristeći LSB (Least Significant Bit) metodu
def hide_text_in_audio(audio_file, output_audio_file, text):
    try:
        # Otvara originalnu audio datoteku u načinu za čitanje bita (rb)
        audio = wave.open(audio_file, mode='rb')
        
        # Čita sve okvire (frames) iz audio datoteke i pretvara ih u niz bajtova
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        
        # Zatvara audio datoteku nakon čitanja
        audio.close()

        # Pretvara tekst u binarni niz i dodaje terminacijski niz '111111111111' koji označava kraj poruke
        binary_text = text_to_binary(text) + '111111111111'

        # Provjerava može li tekst stati u audio datoteku
        # Ako je binarni tekst predug da stane u audio okvire, ispisuje grešku
        if len(binary_text) > len(frame_bytes) * 8:
            raise ValueError("Tekst je predug da stane u audio datoteku.")

        # Stavlja binarni tekst u okvire audio datoteke koristeći LSB metodu
        index = 0
        for bit in binary_text:
            # Zamjenjuje posljednji bit trenutnog bajta bitom iz binarnog teksta
            frame_bytes[index] = (frame_bytes[index] & 254) | int(bit)
            index += 1

        # Piše modificirane okvire u izlaznu audio datoteku
        with wave.open(output_audio_file, 'wb') as fd:
            fd.setparams(audio.getparams())  # Kopira parametre iz originalne audio datoteke
            fd.writeframes(frame_bytes)  # Piše nove okvire u izlaznu datoteku

        print(f"Tekst je uspješno skriven u {output_audio_file}")

    except Exception as e:
        # Hvata bilo kakve greške i ispisuje poruku o grešci
        print(f"Greška pri skrivanju teksta: {e}")

# Funkcija za izdvajanje skrivenog teksta iz audio datoteke koristeći LSB metodu
def extract_text_from_audio(audio_file):
    try:
        # Otvara audio datoteku u načinu za čitanje bita (rb)
        audio = wave.open(audio_file, mode='rb')
        
        # Čita sve okvire iz audio datoteke i pretvara ih u bajtni niz
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        
        # Zatvara audio datoteku nakon čitanja
        audio.close()

        # Izvlači binarni tekst iz audio okvira koristeći LSB metodu
        extracted_binary = ''.join([str(frame_bytes[i] & 1) for i in range(len(frame_bytes))])

        # Pronalazi terminacijski niz i izdvaja binarni tekst do tog mjesta
        end_index = extracted_binary.find('111111111111')
        if end_index != -1:
            extracted_binary = extracted_binary[:end_index]

        # Pretvara binarni tekst natrag u ASCII znakove
        extracted_text = ''.join(chr(int(extracted_binary[i:i+8], 2)) for i in range(0, len(extracted_binary), 8))

        # Ispisuje izdvojeni tekst
        print(f"Izdvojeni tekst: {extracted_text}")

    except Exception as e:
        # Hvata bilo kakve greške i ispisuje poruku o grešci
        print(f"Greška pri izdavanju teksta: {e}")

# Automatsko kodiranje i dekodiranje
input_audio_file = '1.wav'  # Ulazna audio datoteka
output_audio_file = 'audio_sa_porukom.wav'  # Izlazna audio datoteka sa skrivenim tekstom
secret_text = 'Skrivena poruka! '  # Tajna poruka koja će biti skrivena

# Skriva tajni tekst u audio datoteci
hide_text_in_audio(input_audio_file, output_audio_file, secret_text)

# Izvlači skriveni tekst iz audio datoteke
extract_text_from_audio(output_audio_file)

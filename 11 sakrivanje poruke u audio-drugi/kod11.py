import wave

def checkFlip(data, a, b):
    # Provjerava zadnja dva bita (bitovi 2 i 3) u byte podatka
    store = data & 12  # Maskiranje za dobivanje samo bitova 2 i 3

    # Provjera kombinacije bita u "store" i "a, b" vrijednosti
    if store == 0 and (a == 0 and b == 0):
        return data  # Nema potrebe za promjenom
    elif store == 4 and (a == 0 and b == 1):
        return data  # Nema potrebe za promjenom
    elif store == 8 and (a == 1 and b == 0):
        return data  # Nema potrebe za promjenom
    elif store == 12 and (a == 1 and b == 1):
        return data  # Nema potrebe za promjenom
    else:
        return data ^ 3  # Ako se podaci ne podudaraju, mijenjamo zadnja dva bita

def encode():
    print("\nEnkodiranje pocinje..")
    audio = wave.open("1.wav", mode="rb")  # Otvaranje originalne audio datoteke
    frame_bytes = bytearray(audio.readframes(audio.getnframes()))  # Čitanje svih okvira

    # Predefinirani tajni tekst za skrivanje
    secret_text = "Skrivena pouka."
    print("Skivena poruka glasi:", secret_text)

    # Dodavanje # znakova da popuni ostatak okvira audio datoteke
    secret_text = secret_text + int(((2 * len(frame_bytes)) - (len(secret_text) * 8 * 8)) / 8) * '#'

    # Pretvaranje teksta u bitove
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in secret_text])))

    j = 0
    for i in range(0, len(bits), 2):
        a = bits[i]
        b = bits[i + 1]

        # Provjera i prilagodba bita u okvirima
        frame_bytes[j] = checkFlip(frame_bytes[j], a, b)
        frame_bytes[j] = frame_bytes[j] & 243  # Postavljanje zadnja dva bita na 00

        if a == 0 and b == 1:
            frame_bytes[j] = frame_bytes[j] + 4  # Postavljanje na 01
        elif a == 1 and b == 0:
            frame_bytes[j] = frame_bytes[j] + 8  # Postavljanje na 10
        elif a == 1 and b == 1:
            frame_bytes[j] = frame_bytes[j] + 12  # Postavljanje na 11

        j = j + 1

    frame_modified = bytes(frame_bytes)  # Pretvaranje u bytes format

    # Spremanje novog audio s embedded tajnom porukom
    new_audio = wave.open('audio_sa_porukom.wav', 'wb')
    new_audio.setparams(audio.getparams())  # Kopiranje parametara iz originalne datoteke
    new_audio.writeframes(frame_modified)  # Pisanje novih okvira u datoteku
    new_audio.close()
    audio.close()

    print("Enkodiranje uspjesno u datoteku audio_sa_porukom")

def decode():
    print("\nDekodiranje pocinje..")
    audio = wave.open("audio_sa_porukom.wav", mode='rb')  # Otvaranje audio datoteke sa skrivenom porukom
    frame_bytes = bytearray(audio.readframes(audio.getnframes()))  # Čitanje svih okvira

    extracted = []
    for i in range(len(frame_bytes)):
        # Izdvajanje zadnja dva bita iz svakog okvira
        frame_bytes[i] = frame_bytes[i] & 12  # Maskiranje za zadnja dva bita

        if frame_bytes[i] == 0:
            extracted.append(0)
            extracted.append(0)
        elif frame_bytes[i] == 4:
            extracted.append(0)
            extracted.append(1)
        elif frame_bytes[i] == 8:
            extracted.append(1)
            extracted.append(0)
        elif frame_bytes[i] == 12:
            extracted.append(1)
            extracted.append(1)

    # Pretvaranje niza bitova natrag u tekstualni oblik
    extracted_str = "".join(chr(int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))

    # Izdvajanje poruke prije pojave ### (koji označava kraj poruke)
    decoded_message = extracted_str.split("###")[0]

    print("Dekodirana poruka glasi:", decoded_message)
    audio.close()

# Automatsko pokretanje funkcij
encode()  # Kodiranje poruke u audio datoteku
decode()  # Dekodiranje poruke iz audio datoteke

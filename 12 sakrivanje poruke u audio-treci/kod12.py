import wave

def encode():
    print("\nEncoding Starts..")

    # Otvaranje audio datoteke u načinu za čitanje u binarnom formatu
    audio = wave.open("1.wav", mode="rb")
    
    # Pretvaranje svih audio okvira u niz bajtova
    frame_bytes = bytearray(audio.readframes(audio.getnframes()))

    # Predefinirani tajni tekst za kodiranje
    secret_text = "Skrivena poruka!"
    print("Poruka za enkodiranje:", secret_text)

    # Dodavanje popunjujućih znakova '#' kako bi se poruka uskladila s duljinom audio okvira
    secret_text = secret_text + int(((2 * len(frame_bytes)) - (len(secret_text) * 8 * 8)) / 8) * '#'

    # Pretvaranje svakog znaka tajnog teksta u njegov binarni prikaz (8 bitova za svaki znak)
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in secret_text])))

    # Kodiranje bitova poruke u audio okvire
    for i in range(0, len(bits), 2):
        if i < len(frame_bytes):
            # Postavljanje zadnja dva bita u bajtu okvira na bitove tajne poruke
            frame_bytes[i] = (frame_bytes[i] & 252) | bits[i]  # Prva dva bita
            if i + 1 < len(frame_bytes):
                frame_bytes[i + 1] = (frame_bytes[i + 1] & 252) | bits[i + 1]  # Sljedeća dva bita

    # Pretvaranje izmijenjenih okvira natrag u bajtove
    frame_modified = bytes(frame_bytes)

    # Stvaranje nove audio datoteke koja sadrži skriveni tekst
    new_audio = wave.open('audio_sa_porukom.wav', 'wb')
    new_audio.setparams(audio.getparams())  # Kopiranje parametara iz originalne audio datoteke
    new_audio.writeframes(frame_modified)  # Pisanje modificiranih okvira u novu datoteku

    # Zatvaranje novih i originalnih audio datoteka
    new_audio.close()
    audio.close()
    
    print("Enkodiranje uspjesno u audio_sa_porukom.wav")

def decode():
    print("\nDekodiranje pocinje..")

    # Otvaranje audio datoteke sa skrivenom porukom u načinu za čitanje
    audio = wave.open("audio_sa_porukom.wav", mode='rb')
    
    # Pretvaranje svih audio okvira u niz bajtova
    frame_bytes = bytearray(audio.readframes(audio.getnframes()))
    
    extracted = []
    
    # Izdvajanje zadnja dva bita iz svakog okvira kako bi se rekonstruirala poruka
    for byte in frame_bytes:
        extracted.append(byte & 3)  # Izdvajanje zadnja dva bita

    # Spajanje izvađenih bitova u string binarnih brojeva
    extracted_bits = ''.join(map(str, extracted))
    
    # Grupiranje bitova u skupine od 8 za pretvaranje natrag u znakove
    message_bits = [extracted_bits[i:i + 8] for i in range(0, len(extracted_bits), 8)]
    
    # Pretvaranje binarnih skupina u odgovarajuće znakove ASCII koda
    decoded_message = ''.join([chr(int(bits, 2)) for bits in message_bits])
    
    # Prekid dekodirane poruke na mjestu gdje se pojavljuje '###' (označava kraj poruke)
    decoded_message = decoded_message.split("###")[0]
    
    print("Dekodirana poruka glasi:", decoded_message)
    
    # Zatvaranje audio datoteke
    audio.close()

# Automatsko pokretanje funkcija 
encode()  # Kodiranje tajne poruke u audio datoteku
decode()  # Dekodiranje tajne poruke iz audio datoteke

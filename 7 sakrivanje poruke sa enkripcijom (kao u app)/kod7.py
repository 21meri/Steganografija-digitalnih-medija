from PIL import Image
from Crypto.Cipher import AES
import base64
import binascii

def rgb2hex(r, g, b):
    """Pretvori RGB vrijednosti u heksadecimalni kod boje."""
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex2rgb(hexcode):
    """Pretvori heksadecimalni kod boje u RGB vrijednosti."""
    return tuple(int(hexcode[i:i+2], 16) for i in (1, 3, 5))

def str2bin(message):
    """Pretvori string poruku u binarni string."""
    binary = bin(int(binascii.hexlify(message.encode()), 16))
    return binary[2:]

def bin2str(binary):
    """Pretvori binarni string u običnu string poruku."""
    message = binascii.unhexlify('%x' % (int('0b' + binary, 2)))
    return message.decode()

def encode(hexcode, digit):
    """Kodiraj binarni broj u najmanje značajni bit heksadecimalnog koda boje."""
    if hexcode[-1] in ('0', '1', '2', '3', '4', '5'):
        hexcode = hexcode[:-1] + digit
        return hexcode
    else:
        return None

def decode(hexcode):
    """Dekodiraj najmanje značajni bit heksadecimalnog koda boje da bi dobio binarni broj."""
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None

def hide(filename, message, output_filename):
    """Sakrij binarno kodiranu poruku u slici koristeći LSB substituciju."""
    img = Image.open(filename)
    binary = str2bin(message) + '1111111111111110'  # Dodaj delimiter na binarnu poruku
    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        datas = img.getdata()

        newData = []
        digit = 0

        for item in datas:
            if digit < len(binary):
                newpix = encode(rgb2hex(item[0], item[1], item[2]), binary[digit])
                if newpix is None:
                    newData.append(item)
                else:
                    r, g, b = hex2rgb(newpix)
                    newData.append((r, g, b, 255))
                    digit += 1
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(output_filename, "PNG")
        return "Zavrseno!"
    return "Nemoguce sakriti u sliku!"

def retr(filename):
    """Izvuci skrivenu poruku iz slike koristeći LSB ekstrakciju."""
    img = Image.open(filename)
    binary = ''

    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        datas = img.getdata()

        for item in datas:
            digit = decode(rgb2hex(item[0], item[1], item[2]))
            if digit is None:
                pass
            else:
                binary += digit
                if binary[-16:] == '1111111111111110':  # Provjeri delimiter
                    return bin2str(binary[:-16])

        return bin2str(binary)
    return "Nemoguce dekodirati skliku!"

def encrypt_message(message, password):
    """Šifriraj poruku koristeći AES enkripciju s danom lozinkom."""
    cipher = AES.new(password.rjust(16).encode('utf-8'), AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(message.rjust(32).encode('utf-8')))
    return encoded

def decrypt_message(encoded_message, password):
    """Dešifriraj šifriranu poruku koristeći AES dekripciju s danom lozinkom."""
    cipher = AES.new(password.rjust(16).encode('utf-8'), AES.MODE_ECB)
    try:
        decoded = cipher.decrypt(base64.b64decode(encoded_message)).decode('utf-8').strip()
        return decoded
    except:
        return None

# Nazivi datoteka i podaci
image_to_hide_in = '3.png'  # Slika u kojoj će biti skrivena poruka
secret_message = 'Ovo je skrivena poruka'  # Poruka koja će biti skrivena
password = 'Lozinka'  # Lozinka za enkripciju
output_image = 'slika_sa_porukom.png'  # Naziv slike u kojoj će biti spremljena skrivena poruka

# Šifriraj i sakrij poruku
encrypted_message = encrypt_message(secret_message, password)
hide(image_to_hide_in, encrypted_message.decode('utf-8'), output_image)
print(f"Slika spremljena kao {output_image}")

# Izvuci i dešifriraj poruku
extracted_message = retr(output_image)
decrypted_message = decrypt_message(extracted_message.encode('utf-8'), password)

if decrypted_message:
    print(f"Dekodirana poruka: {decrypted_message}")
else:
    print("Nema poruke u slici")

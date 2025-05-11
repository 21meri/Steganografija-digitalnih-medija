from PIL import Image

# Pretvara svaki znak ulaznih podataka u 8-bitni binarni oblik 
def genData(data):
    newd = []
    for i in data:
        newd.append(format(ord(i), '08b'))  # Pretvara svaki znak u binarni oblik i pohranjuje u listu
    return newd

# Mijenja vrijednosti piksela na temelju binarnih podataka i priprema ih za kodiranje
def modPix(pix, data):
    datalist = genData(data)  # Generira binarne podatke iz ulazne poruke
    lendata = len(datalist)   # Duzina binarnih podataka
    imdata = iter(pix)        # Iterator za podatke o pikselima

    for i in range(lendata):
        # Izvlači 9 uzastopnih piksela (3 piksela odjednom, svaki piksel ima 3 vrijednosti: R, G, B)
        pix = [value for value in imdata.__next__()[:3] +
               imdata.__next__()[:3] +
               imdata.__next__()[:3]]

        # Mijenja prvih 8 vrijednosti piksela prema binarnim podacima
        for j in range(8):
            if (datalist[i][j] == '0'and pix[j] % 2 != 0): # Ako je binarni podatak '0' i piksel je neparan, vrijednost je parna
                pix[j] -= 1
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0): # Ako je binarni podatak '1' i piksel je paran, vrijednost je neparna
                if pix[j] != 0:
                    pix[j] -= 1
                else:
                    pix[j] += 1

        # 9. vrijednost piksela (indeks 8) koristi se kao graničnik za označavanje kraja poruke
        if i == lendata - 1:  # Za posljednji set binarnih podataka
            if pix[-1] % 2 == 0:  # Osigurava da zadnja vrijednost piksela bude neparna kako bi označila kraj podataka
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:  # Za ostale setove binarnih podataka
            if pix[-1] % 2 != 0:  # Osigurava da piksel bude paran kako bi označio nastavak
                pix[-1] -= 1

        pix = tuple(pix)  # Pretvara modificirani popis vrijednosti piksela natrag u tuple
        yield pix[0:3]    # Vraća prve 3 vrijednosti piksela
        yield pix[3:6]    # Vraća sljedeće 3 vrijednosti piksela
        yield pix[6:9]    # Vraća zadnje 3 vrijednosti piksela

# Kodira binarne podatke u sliku mijenjanjem njezinih piksela
def encode_enc(newimg, data):
    w = newimg.size[0]  # Sirina slike
    (x, y) = (0, 0)     # Početni položaj piksela

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)  # Postavlja modificirani piksel u sliku
        if x == w - 1:  # Prijelaz na sljedeći red ako se dosegne kraj trenutnog reda
            x = 0
            y += 1
        else:
            x += 1  # Prijelaz na sljedeću kolonu

# Funkcija za kodiranje podataka u sliku i spremanje nove slike
def encode(data_to_encode, output_image_name):
    image = Image.open('1.png', 'r')  # Otvara sliku '1.png'

    if len(data_to_encode) == 0:
        raise ValueError('Podaci su prazni')  # Generira grešku ako nema podataka

    newimg = image.copy()  # Stvara kopiju slike za izmjenu
    encode_enc(newimg, data_to_encode)  # Kodira podatke u sliku
    newimg.save(output_image_name, "PNG")  # Sprema novu sliku s danim imenom
    print(f"Slika je spremljena kao {output_image_name}")

# Dekodira skrivene podatke iz slike čitanjem vrijednosti piksela
def decode(image_name):
    image = Image.open(image_name, 'r')  # Otvara sliku za dekodiranje

    data = ''  # String za pohranu dekodiranih podataka
    imgdata = iter(image.getdata())  # Stvara iterator za podatke o pikselima

    while True:
        # Izvlači 9 uzastopnih piksela (3 piksela odjednom, svaki piksel ima 3 vrijednosti: R, G, B)
        pixels = [value for value in imgdata.__next__()[:3] +
                  imgdata.__next__()[:3] +
                  imgdata.__next__()[:3]]

        binstr = ''

        for i in pixels[:8]:  # Čita prvih 8 vrijednosti piksela za konstrukciju binarnog niza
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))  # Pretvara binarni niz u znak
        if pixels[-1] % 2 != 0:  # Ako je 9. vrijednost piksela neparna, to označava kraj poruke
            return data

# Glavna funkcija za kodiranje i dekodiranje
def main():
    data_to_encode = "Ovo je skrivena poruka!"  # Poruka za kodiranje
    output_image_name = "slika_sa_porukom.png"  # Naziv izlazne slike
    encode(data_to_encode, output_image_name)  # Kodira poruku u sliku
    decoded_message = decode(output_image_name)  # Dekodira poruku iz slike
    print(f"Dekodirana poruka: {decoded_message}")  # Ispisuje dekodiranu poruku

if __name__ == '__main__':
    main()  # Pokreće glavnu funkciju

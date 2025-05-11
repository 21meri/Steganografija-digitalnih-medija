import cv2
import numpy as np
import itertools

# Kvantizacijska tablica za DCT
quant = np.array([[16,11,10,16,24,40,51,61],
                   [12,12,14,19,26,58,60,55],
                   [14,13,16,24,40,57,69,56],
                   [14,17,22,29,51,87,80,62],
                   [18,22,37,56,68,109,103,77],
                   [24,35,55,64,81,104,113,92],
                   [49,64,78,87,103,121,120,101],
                   [72,92,95,98,112,100,103,99]])

class DCT():
    def __init__(self):
        self.message = None
        self.bitMess = None
        self.oriCol = 0
        self.oriRow = 0
        self.numBits = 0

    def encode_image(self, img, secret_msg):
        secret = secret_msg
        self.message = str(len(secret)) + '*' + secret
        self.bitMess = self.toBits()

        row, col = img.shape[:2]
        if (col // 8) * (row // 8) < len(secret):
            print("Error: Poruka je prevelika da bi se kodirala u slici")
            return False

        if row % 8 != 0 or col % 8 != 0:
            img = self.addPadd(img, row, col)

        row, col = img.shape[:2]
        bImg, gImg, rImg = cv2.split(img)
        bImg = np.float32(bImg)

        # Razdvajanje slike na blokove od 8x8 piksela
        imgBlocks = [np.round(bImg[j:j+8, i:i+8] - 128) for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]
        dctBlocks = [np.round(cv2.dct(img_Block)) for img_Block in imgBlocks]
        quantizedDCT = [np.round(dct_Block / quant) for dct_Block in dctBlocks]

        messIndex = 0
        letterIndex = 0
        for quantizedBlock in quantizedDCT:
            DC = quantizedBlock[0][0]
            DC = np.round(DC)  # Osiguraj da je DC skalar
            DC = np.uint8(DC)
            DC = np.unpackbits(DC)
            if messIndex < len(self.bitMess):
                DC[7] = int(self.bitMess[messIndex][letterIndex])
            DC = np.packbits(DC)
            DC = np.float32(DC)
            DC = DC - 255
            quantizedBlock[0][0] = DC.item()  # Osiguraj da je DC skalar

            letterIndex += 1
            if letterIndex == 8:
                letterIndex = 0
                messIndex += 1
                if messIndex == len(self.message):
                    break

        # Rekonstrukcija slike nakon enkodiranja
        sImgBlocks = [quantizedBlock * quant + 128 for quantizedBlock in quantizedDCT]
        sImg = []
        for chunkRowBlocks in self.chunks(sImgBlocks, col // 8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    sImg.extend(block[rowBlockNum])
        sImg = np.array(sImg).reshape(row, col)
        sImg = np.uint8(sImg)
        sImg = cv2.merge((sImg, gImg, rImg))
        return sImg

    def decode_image(self, img):
        row, col = img.shape[:2]
        messageBits = []
        buff = 0
        messSize = None  # Inicijaliziraj messSize

        bImg, gImg, rImg = cv2.split(img)
        bImg = np.float32(bImg)
        imgBlocks = [bImg[j:j+8, i:i+8] - 128 for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]
        quantizedDCT = [img_Block / quant for img_Block in imgBlocks]

        i = 0
        for quantizedBlock in quantizedDCT:
            DC = quantizedBlock[0][0]
            DC = np.round(DC)  # Osiguraj da je DC skalar
            DC = np.uint8(DC)
            DC = np.unpackbits(DC)
            if DC[7] == 1:
                buff += (0 & 1) << (7 - i)
            elif DC[7] == 0:
                buff += (1 & 1) << (7 - i)
            i += 1
            if i == 8:
                messageBits.append(chr(buff))
                buff = 0
                i = 0
                if messageBits[-1] == '*' and messSize is None:
                    try:
                        messSize = int(''.join(messageBits[:-1]))
                    except:
                        pass
            if messSize is not None and len(messageBits) - len(str(messSize)) - 1 == messSize:
                return ''.join(messageBits)[len(str(messSize)) + 1:]

        # Rekonstrukcija slike nakon dekodiranja
        sImgBlocks = [quantizedBlock * quant + 128 for quantizedBlock in quantizedDCT]
        sImg = []
        for chunkRowBlocks in self.chunks(sImgBlocks, col // 8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    sImg.extend(block[rowBlockNum])
        sImg = np.array(sImg).reshape(row, col)
        sImg = np.uint8(sImg)
        sImg = cv2.merge((sImg, gImg, rImg))
        return ''

    def chunks(self, l, n):
        m = int(n)
        for i in range(0, len(l), m):
            yield l[i:i + m]

    def addPadd(self, img, row, col):
        """Dodaj padding slici da bi dimenzije bile višeugao 8."""
        img = cv2.resize(img, (col + (8 - col % 8), row + (8 - row % 8)))
        return img

    def toBits(self):
        """Pretvori poruku u binarne bitove."""
        bits = []
        for char in self.message:
            binval = bin(ord(char))[2:].rjust(8, '0')
            bits.append(binval)
        self.numBits = bin(len(bits))[2:].rjust(8, '0')
        return bits

# Primjer korištenja:
dct = DCT()

# Učitaj sliku
input_image = cv2.imread('3.png')

# Enkodiraj tajnu poruku
encoded_img = dct.encode_image(input_image, "Skrivena poruka")

# Spremi enkodiranu sliku
cv2.imwrite('slika_sa_porukom.png', encoded_img)

# Dekodiraj poruku
decoded_message = dct.decode_image(encoded_img)
print("Dekodirana poruka:", decoded_message)

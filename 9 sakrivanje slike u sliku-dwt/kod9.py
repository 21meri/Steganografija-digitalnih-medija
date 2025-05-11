import cv2
import numpy as np
import pywt

def embed_image(cover_img_path, secret_img_path, output_img_path):
    # Učitaj glavnu sliku i tajne slike
    cover_img = cv2.imread(cover_img_path, cv2.IMREAD_COLOR)
    secret_img = cv2.imread(secret_img_path, cv2.IMREAD_COLOR)
    
    if cover_img is None or secret_img is None:
        print("Error: Could not load cover or secret image.")
        return

    # Pretvori slike u sivu skalu
    cover_img_gray = cv2.cvtColor(cover_img, cv2.COLOR_BGR2GRAY)
    secret_img_gray = cv2.cvtColor(secret_img, cv2.COLOR_BGR2GRAY)
    
    # Promijeni veličinu tajne slike da stane u glavnu sliku
    secret_img_gray = cv2.resize(secret_img_gray, (cover_img_gray.shape[1], cover_img_gray.shape[0]))

    # Primijeni DWT na glavnu sliku
    coeffs_cover = pywt.dwt2(cover_img_gray, 'haar')
    LL, (LH, HL, HH) = coeffs_cover

    # Primijeni DWT na tajnu sliku
    coeffs_secret = pywt.dwt2(secret_img_gray, 'haar')
    LL_secret, (_, _, _) = coeffs_secret
    
    # Umetni tajnu sliku u LL komponentu glavne slike
    LL_embedded = LL + 0.1 * LL_secret

    # Primijeni inverznu DWT za dobivanje stego slike
    stego_coeffs = (LL_embedded, (LH, HL, HH))
    stego_img = pywt.idwt2(stego_coeffs, 'haar')

    # Provjeri da li je stego slika valjana
    if stego_img is None:
        print("Error: DWT or IDWT failed.")
        return

    # Spremi stego sliku
    stego_img = np.uint8(np.clip(stego_img, 0, 255))  # Osiguraj da su svi pikseli u opsegu [0, 255]
    cv2.imwrite(output_img_path, stego_img)

def extract_image(stego_img_path, cover_img_path, output_img_path):
    # Učitaj stego i glavnu sliku
    stego_img = cv2.imread(stego_img_path, cv2.IMREAD_GRAYSCALE)
    cover_img = cv2.imread(cover_img_path, cv2.IMREAD_GRAYSCALE)

    if stego_img is None or cover_img is None:
        print("Error: Could not load stego or cover image.")
        return

    # Primijeni DWT na stego i glavnu sliku
    coeffs_stego = pywt.dwt2(stego_img, 'haar')
    LL_stego, (LH_stego, HL_stego, HH_stego) = coeffs_stego

    coeffs_cover = pywt.dwt2(cover_img, 'haar')
    LL_cover, (LH_cover, HL_cover, HH_cover) = coeffs_cover

    # Izdvoji tajnu sliku iz LL komponente
    LL_secret = (LL_stego - LL_cover) / 0.1

    # Primijeni inverznu DWT za dobivanje tajne slike
    secret_coeffs = (LL_secret, (LH_cover, HL_cover, HH_cover))
    secret_img = pywt.idwt2(secret_coeffs, 'haar')

    # Provjeri da li je tajna slika valjana
    if secret_img is None:
        print("Error: DWT or IDWT failed.")
        return

    # Spremi tajnu sliku
    secret_img = np.uint8(np.clip(secret_img, 0, 255))  # Osiguraj da su svi pikseli u opsegu [0, 255]
    cv2.imwrite(output_img_path, secret_img)

# Datoteke korištenja
embed_image('3.png', '1.png', 'slika_sa_porukom.png')
extract_image('slika_sa_porukom.png', '3.png', 'dekodirana_slika.png')

import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog

import termcolor
from termcolor import colored
from pyfiglet import figlet_format

def msgtobinary(msg):
    if type(msg) == str:
        result= ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result= [format(i, "08b") for i in msg]
    elif type(msg) == int or type(msg) == np.uint8:
        result=format(msg, "08b")
    else:
        raise TypeError("Nepodržan unos")
    return result

def KSA(key):
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def PRGA(S, n):
    i = 0
    j = 0
    key = []
    while n > 0:
        n -= 1
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        key.append(K)
    return key

def preparing_key_array(s):
    return [ord(c) for c in s]

def encryption(plaintext, key):
    key = preparing_key_array(key)
    S = KSA(key)
    keystream = np.array(PRGA(S, len(plaintext)))
    plaintext = np.array([ord(i) for i in plaintext])
    cipher = keystream ^ plaintext
    ctext = ''
    for c in cipher:
        ctext += chr(c)
    return ctext

def decryption(ciphertext, key):
    key = preparing_key_array(key)
    S = KSA(key)
    keystream = np.array(PRGA(S, len(ciphertext)))
    ciphertext = np.array([ord(i) for i in ciphertext])
    decoded = keystream ^ ciphertext
    dtext = ''
    for c in decoded:
        dtext += chr(c)
    return dtext

def embed(frame, data, key):
    data = encryption(data, key)
    if len(data) == 0: 
        raise ValueError('Unešeno prazno polje za enkodiranje')
    data += '*^*^*'
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    index_data = 0
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
        return frame

def extract(frame, key):
    data_binary = ""
    final_decoded_msg = ""
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [data_binary[i: i+8] for i in range(0, len(data_binary), 8)]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*": 
                    for i in range(0, len(decoded_data)-5):
                        final_decoded_msg += decoded_data[i]
                    final_decoded_msg = decryption(final_decoded_msg, key)
                    print("\n\nEnkodirana poruka je: ", final_decoded_msg)
                    return 

def decode_vid_data(frame_, key):
    root = tk.Tk()
    root.withdraw()
    print("\tIzaberi video")
    root.attributes('-alpha', 0.0)
    root.attributes('-topmost', True)
    video_path = filedialog.askopenfilename(title="Izaberi video za dekodiranje poruke")

    if video_path:
        cap = cv2.VideoCapture(video_path)
        max_frame = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        print("Ukupan broj frame-ova koji su odabrani u videu:", max_frame)
        print("Unesite tajni broj frame-a iz kkog želite otkriti poruku: ", end='')
        n = int(input())
        vidcap = cv2.VideoCapture(video_path)
        frame_number = 0
        while(vidcap.isOpened()):
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                extract(frame_, key)
                return

def encode_vid_data():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-alpha', 0.0)
    root.attributes('-topmost', True)
    video_path = filedialog.askopenfilename(title="Izaberite video")

    if video_path:
        cap = cv2.VideoCapture(video_path)
        vidcap = cv2.VideoCapture(video_path)    
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))

        size = (frame_width, frame_height)
        filename = os.path.splitext(os.path.basename(video_path))[0]
        
        # Specify the directory where the result files will be saved
        result_dir = 'C:/Users/Korisnik/Desktop/Kodovi/18 sakrivanje poruke u video/Result_files'
        
        # Ensure the directory exists
        if not os.path.exists(result_dir):
            try:
                os.makedirs(result_dir)
                print(f"Folder {result_dir} je kreiran uspješno.")
            except OSError as e:
                print(f"Greška pri kreiranju foldera {result_dir}: {e}")
                return

        output_filename = os.path.join(result_dir, f'{filename}_video_sa_porukom.mp4')

        out = cv2.VideoWriter(output_filename, fourcc, 25.0, size)
        max_frame = 0
        print("\n\t Broje se frame-ovi, pričekajte ...\n")
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        cap.release()
        print("Ukupan broj frame-ova u videu je: ", max_frame)
        print("Unesite broj frame-a u koji želite sakriti poruku: ", end='')
        n = int(input())
        frame_number = 0
        while vidcap.isOpened():
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                data = input("Unesite poruku koju želite sakriti: ")
                key = input("Unesite šifru: ")
                change_frame_with = embed(frame, data, key)
                frame_ = change_frame_with
                frame = change_frame_with
            out.write(frame)
        
        npy_path = os.path.join(result_dir, f'{filename}_embedded_frame.npy')
        np.save(npy_path, frame_)
        print("\nPoruka je uspješno enkodirana.")
        print(f"\nSkriveni frame je spremljen kao .npy u: {npy_path}")
        return frame_
    else: 
        print("\n\tOtvaranje otkazano\n")

def vid_steg():
    
    while(True):
        print("\nIZABERITE OPCIJU\n") 
        print("1. Enkodiraj poruku")  
        print("2. Dekodiraj poruku")  
        print("3. Izađi")  
        choice1 = int(input("Unesi broj opcije: "))   
        if choice1 == 1:
            print("\tIzaberi video")
            a = encode_vid_data()
        elif choice1 == 2:
            keys = input("\tUnesi šifru: ")
            root = tk.Tk()
            root.withdraw()
            root.attributes('-alpha', 0.0)
            root.attributes('-topmost', True)
            a_path = filedialog.askopenfilename(title="Odaberite skriveni frame <.npy_file>", filetypes=[("Numpy files", "*.npy")])
    
            if a_path:
                a = np.load(a_path, allow_pickle=True)
                decode_vid_data(a, keys)
            else:
                print("Nije odabrano.")
        elif choice1 == 3:
            break
        else:
            print("Pogrešna opcija")
        print("\n")

if __name__ == "__main__":
    vid_steg()

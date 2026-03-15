import tkinter as tk
from tkinter import scrolledtext, PanedWindow
from collections import defaultdict
import math

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

# --------------------------------
# Очистка текста
# --------------------------------
def clean_text(text):
    letters=[]
    positions=[]
    for i,c in enumerate(text.lower()):
        if c in ALPHABET:
            letters.append(c)
            positions.append(i)
    return "".join(letters),positions

# --------------------------------
# Тест Касиски
# --------------------------------
def kasiski_test(text):
    trigram_pos=defaultdict(list)
    for i in range(len(text)-2):
        tri=text[i:i+3]
        trigram_pos[tri].append(i)
    repeated={k:v for k,v in trigram_pos.items() if len(v)>1}

    distances=[]
    for tri,pos in repeated.items():
        for i in range(len(pos)-1):
            d=pos[i+1]-pos[i]
            distances.append(d)

    if len(distances)==0:
        gcd_val=0
    else:
        gcd_val=distances[0]
        for d in distances[1:]:
            gcd_val=math.gcd(gcd_val,d)

    return repeated,distances,gcd_val

# --------------------------------
# Дешифровка текста
# --------------------------------
def decrypt(cipher,key):
    res=""
    k=len(key)
    for i,c in enumerate(cipher):
        ci=ALPHABET.index(c)
        ki=ALPHABET.index(key[i%k])
        pi=(ci-ki)%M
        res+=ALPHABET[pi]
    return res

# --------------------------------
# Восстановление текста с пробелами
# --------------------------------
def restore_text(original,decrypted):
    result=list(original)
    j=0
    for i,c in enumerate(original.lower()):
        if c in ALPHABET:
            result[i]=decrypted[j]
            j+=1
    return "".join(result)

# --------------------------------
# Анализ
# --------------------------------
def analyze():
    original=input_text.get("1.0",tk.END)
    cipher,_=clean_text(original)

    if len(cipher)==0:
        return

    # --- Касиски
    trigrams,distances,gcd_val=kasiski_test(cipher)

    kasiski_field.delete(1.0,tk.END)
    kasiski_field.insert(tk.END,"Повторяющиеся триграммы:\n")
    for tri,pos in trigrams.items():
        kasiski_field.insert(tk.END,f"{tri} -> {pos}\n")
    kasiski_field.insert(tk.END,"\nРасстояния:\n")
    kasiski_field.insert(tk.END,str(distances)+"\n")
    kasiski_field.insert(tk.END,"\nПредполагаемый период (НОД расстояний):\n")
    kasiski_field.insert(tk.END,str(gcd_val))

    # --- формируем ключ (временно используем все 'а' для наглядности)
    key = "а" * gcd_val if gcd_val>0 else ""
    key_field.delete(1.0,tk.END)
    key_field.insert(tk.END,key)

    # --- дешифровка
    decrypted = decrypt(cipher,key) if key else ""
    full = restore_text(original,decrypted) if decrypted else ""
    decrypted_text.delete(1.0,tk.END)
    decrypted_text.insert(tk.END,full)

# --------------------------------
# Очистка
# --------------------------------
def clear_fields():
    for field in [input_text,key_field,decrypted_text,kasiski_field]:
        field.delete(1.0,tk.END)

# --------------------------------
# GUI
# --------------------------------
root=tk.Tk()
root.title("Криптоанализ шифра Виженера (Касиски)")
root.geometry("1100x700")

main=PanedWindow(root,orient=tk.VERTICAL)
main.pack(fill=tk.BOTH,expand=1)

# --- ввод
frame_input=tk.Frame(main)
tk.Label(frame_input,text="Шифротекст").pack()
input_text=scrolledtext.ScrolledText(frame_input, height=8)
input_text.pack(fill=tk.BOTH,expand=True)
main.add(frame_input)

# --- кнопки
btn_frame=tk.Frame(root)
btn_frame.pack(pady=5)
tk.Button(btn_frame,text="Анализ",command=analyze,width=12).pack(side=tk.LEFT,padx=3)
tk.Button(btn_frame,text="Очистить",command=clear_fields,width=12).pack(side=tk.LEFT,padx=3)

# --- результаты
middle=PanedWindow(main,orient=tk.HORIZONTAL)
main.add(middle)

# ключ
frame_key=tk.Frame(middle)
tk.Label(frame_key,text="Ключ (прибл.)").pack()
key_field=scrolledtext.ScrolledText(frame_key,height=2)
key_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_key)

# касиски
frame_kasiski=tk.Frame(middle)
tk.Label(frame_kasiski,text="Тест Касиски").pack()
kasiski_field=scrolledtext.ScrolledText(frame_kasiski,height=12)
kasiski_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_kasiski)

# дешифровка
frame_dec=tk.Frame(main)
tk.Label(frame_dec,text="Расшифрованный текст").pack()
decrypted_text=scrolledtext.ScrolledText(frame_dec,height=10)
decrypted_text.pack(fill=tk.BOTH,expand=True)
main.add(frame_dec)

root.mainloop()
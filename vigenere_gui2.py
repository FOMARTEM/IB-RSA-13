import tkinter as tk
from tkinter import scrolledtext, PanedWindow
from collections import Counter, defaultdict
import math

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

RUS_FREQ = {
'о':0.1097,'е':0.0845,'а':0.0801,'и':0.0735,'н':0.0670,'т':0.0626,'с':0.0547,
'р':0.0473,'в':0.0454,'л':0.0440,'к':0.0349,'м':0.0321,'д':0.0298,'п':0.0281,
'у':0.0262,'я':0.0201,'ы':0.0190,'ь':0.0174,'г':0.0170,'з':0.0165,'б':0.0159,
'ч':0.0144,'й':0.0121,'х':0.0097,'ж':0.0094,'ш':0.0073,'ю':0.0064,'ц':0.0048,
'щ':0.0036,'э':0.0032,'ф':0.0026,'ъ':0.0004
}

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
# Индекс совпадения
# --------------------------------

def index_of_coincidence(text):

    N=len(text)
    freq=Counter(text)

    s=0
    for f in freq.values():
        s+=f*(f-1)

    if N<2:
        return 0

    return s/(N*(N-1))


# --------------------------------
# Разбивка на столбцы
# --------------------------------

def split_columns(text,m):

    cols=[""]*m

    for i,c in enumerate(text):
        cols[i%m]+=c

    return cols


# --------------------------------
# Поиск периода
# --------------------------------

def find_key_length(cipher):

    best_len=1
    best_ic=0

    results=[]

    for m in range(1,11):

        cols=split_columns(cipher,m)

        ic=sum(index_of_coincidence(c) for c in cols)/m

        results.append((m,ic))

        if ic>best_ic:
            best_ic=ic
            best_len=m

    return best_len,results


# --------------------------------
# Chi-square
# --------------------------------

def chi_square(text):

    freq=Counter(text)
    N=len(text)

    score=0

    for l in ALPHABET:

        observed=freq[l]
        expected=RUS_FREQ.get(l,0)*N

        score+=(observed-expected)**2/(expected+0.0001)

    return score


# --------------------------------
# Поиск ключа
# --------------------------------

def find_key(cipher,key_len):

    cols=split_columns(cipher,key_len)

    key=""

    for col in cols:

        best_shift=0
        best_score=10**12

        for shift in range(M):

            decrypted=""

            for c in col:
                pi=(ALPHABET.index(c)-shift)%M
                decrypted+=ALPHABET[pi]

            score=chi_square(decrypted)

            if score<best_score:
                best_score=score
                best_shift=shift

        key+=ALPHABET[best_shift]

    return key


# --------------------------------
# Дешифрование
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
# Возврат пробелов
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

    kasiski_field.insert(tk.END,"\nНОД расстояний:\n")
    kasiski_field.insert(tk.END,str(gcd_val))

    # --- Индексы совпадения
    key_len,results=find_key_length(cipher)

    indexes_field.delete(1.0,tk.END)

    for m,ic in results:
        indexes_field.insert(tk.END,f"{m} -> {ic:.4f}\n")

    period_field.delete(1.0,tk.END)
    period_field.insert(tk.END,str(key_len))

    # --- Ключ
    key=find_key(cipher,key_len)

    key_field.delete(1.0,tk.END)
    key_field.insert(tk.END,key)

    # --- Расшифровка
    decrypted=decrypt(cipher,key)

    full=restore_text(original,decrypted)

    decrypted_text.delete(1.0,tk.END)
    decrypted_text.insert(tk.END,full)


# --------------------------------
# Очистка
# --------------------------------

def clear_fields():

    for field in [input_text,key_field,period_field,indexes_field,decrypted_text,kasiski_field]:
        field.delete(1.0,tk.END)


# --------------------------------
# GUI
# --------------------------------

root=tk.Tk()
root.title("Криптоанализ шифра Виженера")
root.geometry("1100x750")

main=PanedWindow(root,orient=tk.VERTICAL)
main.pack(fill=tk.BOTH,expand=1)

# --- ввод
frame_input=tk.Frame(main)
tk.Label(frame_input,text="Шифротекст").pack()
input_text=scrolledtext.ScrolledText(frame_input)
input_text.pack(fill=tk.BOTH,expand=True)
main.add(frame_input)

# --- кнопки
btn_frame=tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame,text="Анализ",command=analyze,width=15).pack(side=tk.LEFT,padx=5)
tk.Button(btn_frame,text="Очистить",command=clear_fields,width=15).pack(side=tk.LEFT,padx=5)

# --- результаты
middle=PanedWindow(main,orient=tk.HORIZONTAL)
main.add(middle)

# ключ
frame_key=tk.Frame(middle)
tk.Label(frame_key,text="Ключ").pack()
key_field=scrolledtext.ScrolledText(frame_key,height=3)
key_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_key)

# период
frame_period=tk.Frame(middle)
tk.Label(frame_period,text="Период").pack()
period_field=scrolledtext.ScrolledText(frame_period,height=3)
period_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_period)

# индексы
frame_indexes=tk.Frame(middle)
tk.Label(frame_indexes,text="Индексы совпадения").pack()
indexes_field=scrolledtext.ScrolledText(frame_indexes)
indexes_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_indexes)

# касиски
frame_kasiski=tk.Frame(middle)
tk.Label(frame_kasiski,text="Тест Касиски").pack()
kasiski_field=scrolledtext.ScrolledText(frame_kasiski)
kasiski_field.pack(fill=tk.BOTH,expand=True)
middle.add(frame_kasiski)

# дешифровка
frame_dec=tk.Frame(main)
tk.Label(frame_dec,text="Расшифрованный текст").pack()
decrypted_text=scrolledtext.ScrolledText(frame_dec)
decrypted_text.pack(fill=tk.BOTH,expand=True)
main.add(frame_dec)

root.mainloop()
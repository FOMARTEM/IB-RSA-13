import tkinter as tk
from tkinter import messagebox
import re
from collections import defaultdict

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ALPHABET_SIZE = 32

RU_FREQ = [
    0.080,0.016,0.045,0.014,0.072,0.076,0.007,0.016,0.062,0.010,
    0.035,0.028,0.026,0.065,0.090,0.023,0.014,0.054,0.063,0.053,
    0.014,0.038,0.004,0.045,0.014,0.006,0.016,0.016,0.003,0.018,
    0.018,0.020
]

current_keys = []
clean_text = ""
original_text = ""


# -------------------------------------------------
# Криптоаналитическая логика (БЕЗ КЛАССОВ)
# -------------------------------------------------

def find_distances(text, n):
    m = defaultdict(list)

    for i in range(len(text)-n+1):
        s = text[i:i+n]
        m[s].append(i)

    res = []

    for v in m.values():
        if len(v) > 1:
            for i in range(len(v)-1):
                res.append(v[i+1]-v[i])

    return res


def calculate_ic(text):

    n = len(text)

    if n <= 1:
        return 0

    f = [0]*ALPHABET_SIZE

    for c in text:
        idx = ALPHABET.find(c)
        if idx != -1:
            f[idx]+=1

    s = 0
    for x in f:
        s += x*(x-1)

    return s/(n*(n-1))


def calculate_average_ic(text, key_len):

    total = 0

    for i in range(key_len):

        col = []

        for j in range(i,len(text),key_len):
            col.append(text[j])

        if len(col) > 1:
            total += calculate_ic("".join(col))

    return total/key_len


def find_key_length(text):

    distances = find_distances(text,3)
    best_mu = -1

    if distances:

        votes = {}

        for length in range(2,11):

            count = 0
            for d in distances:
                if d % length == 0:
                    count += 1

            votes[length] = count

        top3 = sorted(votes, key=votes.get, reverse=True)[:3]

        min_diff = 999

        for length in top3:

            ic = calculate_average_ic(text,length)
            diff = abs(ic - 0.055)

            if diff < min_diff and diff < 0.025:
                min_diff = diff
                best_mu = length

    if best_mu == -1:

        max_ic = -1

        for length in range(1,11):

            ic = calculate_average_ic(text,length)

            if ic > max_ic:
                max_ic = ic
                best_mu = length

    return best_mu if best_mu!=-1 else 1


def get_top_shifts(col,n):

    counts=[0]*ALPHABET_SIZE
    total=0

    for c in col:

        idx=ALPHABET.find(c)

        if idx!=-1:
            counts[idx]+=1
            total+=1

    if total==0:
        return ['А']

    scores=[]

    for shift in range(ALPHABET_SIZE):

        err=0

        for i in range(ALPHABET_SIZE):

            orig=(i-shift+ALPHABET_SIZE)%ALPHABET_SIZE
            obs=counts[i]/total

            err+=(obs-RU_FREQ[orig])**2

        scores.append((shift,err))

    scores.sort(key=lambda x:x[1])

    res=[]

    for i in range(min(n,len(scores))):
        res.append(ALPHABET[scores[i][0]])

    return res


def decrypt_vigenere(text,key):

    res=[]

    for i,c in enumerate(text):

        cIdx=ALPHABET.find(c)
        kIdx=ALPHABET.find(key[i%len(key)])

        if cIdx==-1 or kIdx==-1:
            continue

        res.append(ALPHABET[(cIdx-kIdx)%ALPHABET_SIZE])

    return "".join(res)


def decrypt_preserve(original,key):

    res=[]
    key_index=0

    for c in original:

        upper=c.upper()

        if upper=='Ё':
            upper='Е'

        cIdx=ALPHABET.find(upper)

        if cIdx!=-1:

            kIdx=ALPHABET.find(key[key_index%len(key)])

            dec=(cIdx-kIdx)%ALPHABET_SIZE
            ch=ALPHABET[dec]

            if c.islower():
                res.append(ch.lower())
            else:
                res.append(ch)

            key_index+=1

        else:
            res.append(c)

    return "".join(res)


# -------------------------------------------------
# GUI (КЛАСС МОЖНО)
# -------------------------------------------------

class App:

    def __init__(self,root):

        self.root=root
        root.title("Криптоанализ Виженера")

        frame1=tk.LabelFrame(root,text="Введите текст")
        frame1.pack(fill="both",expand=True,padx=5,pady=5)

        self.input_text=tk.Text(frame1,height=8)
        self.input_text.pack(fill="both",expand=True)

        btn=tk.Button(root,text="Анализировать",command=self.analyze)
        btn.pack(pady=5)

        frame2=tk.LabelFrame(root,text="Варианты ключа")
        frame2.pack(fill="both",expand=True,padx=5,pady=5)

        self.listbox=tk.Listbox(frame2)
        self.listbox.pack(fill="both",expand=True)

        self.listbox.bind("<<ListboxSelect>>",self.select_key)

        frame3=tk.LabelFrame(root,text="Расшифровка")
        frame3.pack(fill="both",expand=True,padx=5,pady=5)

        self.result=tk.Text(frame3,height=10)
        self.result.pack(fill="both",expand=True)


    def analyze(self):

        global clean_text,original_text,current_keys

        original_text=self.input_text.get("1.0",tk.END)

        if not original_text.strip():

            messagebox.showwarning("Ошибка","Введите текст")
            return

        clean_text=original_text.upper()
        clean_text=clean_text.replace("Ё","Е")
        clean_text=re.sub("[^А-Я]","",clean_text)

        if len(clean_text)<20:

            messagebox.showerror("Ошибка","Минимум 20 букв")
            return

        mu=find_key_length(clean_text)

        base_key=""

        for i in range(mu):

            col=""

            for j in range(i,len(clean_text),mu):
                col+=clean_text[j]

            base_key+=get_top_shifts(col,1)[0]

        current_keys=[]
        self.listbox.delete(0,tk.END)

        for i in range(mu):

            shifted=base_key[i:]+base_key[:i]

            current_keys.append(shifted)

            preview=decrypt_vigenere(clean_text,shifted)[:50]

            self.listbox.insert(tk.END,f"{shifted} -> {preview}")

        if current_keys:
            self.listbox.select_set(0)
            self.show_decrypt(current_keys[0])


    def select_key(self,event):

        if not self.listbox.curselection():
            return

        idx=self.listbox.curselection()[0]

        key=current_keys[idx]

        self.show_decrypt(key)


    def show_decrypt(self,key):

        text=decrypt_preserve(original_text,key)

        self.result.delete("1.0",tk.END)
        self.result.insert(tk.END,text)


# -------------------------------------------------

root=tk.Tk()
app=App(root)
root.mainloop()
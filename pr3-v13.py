import tkinter as tk
from tkinter import ttk, messagebox
import re
from collections import defaultdict

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ALPHABET_SIZE = 32

# https://studfile.net/preview/1725830/page:36/
RU_FREQ = [
0.080,0.016,0.045,0.014,0.072,0.076,0.007,0.016,0.062,0.010,
0.035,0.028,0.026,0.065,0.090,0.023,0.014,0.054,0.063,0.053,
0.014,0.038,0.004,0.045,0.014,0.006,0.016,0.016,0.003,0.018,
0.018,0.020
]

current_keys=[]
clean_text=""
original_text=""



# ищет повторяющийся текст заданной длины
def find_distances(text,n):

    m=defaultdict(list)

    for i in range(len(text)-n+1):
        m[text[i:i+n]].append(i)

    res=[]

    for v in m.values():
        if len(v)>1:
            for i in range(len(v)-1):
                res.append(v[i+1]-v[i])

    return res

# Индекс совпадений
def calculate_ic(text):

    n=len(text)

    if n<=1:
        return 0

    f=[0]*ALPHABET_SIZE

    for c in text:
        idx=ALPHABET.find(c)
        if idx!=-1:
            f[idx]+=1

    s=0
    for x in f:
        s+=x*(x-1)

    return s/(n*(n-1))


def calculate_average_ic(text,key_len):

    total=0

    for i in range(key_len):

        col=""

        for j in range(i,len(text),key_len):
            col+=text[j]

        if len(col)>1:
            total+=calculate_ic(col)

    return total/key_len

# Поиск длины ключа 
def find_key_length(text):

    distances=find_distances(text,3)
    best_mu=-1

    if distances:

        votes={}

        for length in range(2,11):

            count=0

            for d in distances:
                if d%length==0:
                    count+=1

            votes[length]=count

        top3=sorted(votes,key=votes.get,reverse=True)[:3]

        min_diff=999

        for length in top3:

            ic=calculate_average_ic(text,length)
            diff=abs(ic-0.055)

            if diff<min_diff and diff<0.025:
                min_diff=diff
                best_mu=length

    if best_mu==-1:

        max_ic=-1

        for length in range(1,11):

            ic=calculate_average_ic(text,length)

            if ic>max_ic:
                max_ic=ic
                best_mu=length

    return best_mu if best_mu!=-1 else 1

# Частотный анализ
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

            err+=(obs-RU_FREQ[orig])**2 # Метод наименьших квадратов

        scores.append((shift,err))

    scores.sort(key=lambda x:x[1])

    res=[]

    for i in range(min(n,len(scores))):
        res.append(ALPHABET[scores[i][0]])

    return res

# Расшифровка Виженера

def decrypt_preserve(original,key):

    res=[]
    key_index=0

    for c in original:

        # переводим весь текст в верхний регистр
        upper=c.upper()

        # ё = Е
        if upper=="Ё": 
            upper="Е"

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


# ---------------- GUI ----------------

class App:

    def __init__(self,root):

        self.root=root
        root.title("Криптоанализ Виженера")

        frame1=tk.LabelFrame(root,text="Введите текст")
        frame1.pack(fill="both",expand=True,padx=5,pady=5)

        self.input_text=tk.Text(frame1,height=8)
        self.input_text.pack(fill="both",expand=True)

        btn_frame=tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame,text="Анализировать",
                  command=self.analyze).grid(row=0,column=0,padx=5)

        tk.Button(btn_frame,text="Расшифровать",
                  command=self.decrypt).grid(row=0,column=1,padx=5)

        tk.Button(btn_frame,text="Очистить поля",
                  command=self.clear_fields).grid(row=0,column=2,padx=5)

        frame2=tk.LabelFrame(root,text="Выберите ключ")
        frame2.pack(fill="x",padx=5,pady=5)

        self.combo=ttk.Combobox(frame2,state="readonly")
        self.combo.pack(fill="x",padx=5,pady=5)

        frame3=tk.LabelFrame(root,text="Расшифрованный текст")
        frame3.pack(fill="both",expand=True,padx=5,pady=5)

        self.result=tk.Text(frame3)
        self.result.pack(fill="both",expand=True)


    def analyze(self):

        global clean_text,original_text,current_keys

        original_text=self.input_text.get("1.0",tk.END)

        if not original_text.strip():
            messagebox.showwarning("Ошибка","Введите текст")
            return

        # убираем всякую всячину
        clean_text=original_text.upper()
        clean_text=clean_text.replace("Ё","Е")
        clean_text=re.sub("[^А-Я]","",clean_text) 

        if len(clean_text)<20:
            messagebox.showerror("Ошибка","Минимум 20 букв")
            return

        # ищем длину ключа
        mu=find_key_length(clean_text)

        base_key=""

        # находим ключи
        for i in range(mu):

            col=""

            for j in range(i,len(clean_text),mu):
                col+=clean_text[j]

            base_key+=get_top_shifts(col,1)[0]

        current_keys=[]

        for i in range(mu):

            shifted=base_key[i:]+base_key[:i]
            current_keys.append(shifted)

        self.combo["values"]=current_keys

        if current_keys:
            self.combo.current(0)


    def decrypt(self):

        key=self.combo.get()

        if not key:
            messagebox.showwarning("Ошибка","Выберите ключ")
            return

        # переводим текст 
        text=decrypt_preserve(original_text,key)

        self.result.delete("1.0",tk.END)
        self.result.insert(tk.END,text)


    def clear_fields(self):

        global current_keys,clean_text,original_text

        self.input_text.delete("1.0",tk.END)
        self.result.delete("1.0",tk.END)

        self.combo.set("")
        self.combo["values"]=[]

        current_keys=[]
        clean_text=""
        original_text=""

root=tk.Tk()
app=App(root)
root.mainloop()
import os
import time
from tkinter import * 
import pyaudio
from array import array
import threading
from tkinter.filedialog import asksaveasfilename
import wave
# import soundfile as sf

# from PILLOW import Image, ImageTk
font = "courier"
fontsize = 15

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
record_on = False
frames = []

p = pyaudio.PyAudio()
stream = None


counter = 0 

def play(stream, p, wf):
    global CHUNK
    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.close()
    p.terminate()

def play_queue(q):
    global CHUNK
    p = pyaudio.PyAudio()

    for file_name in q:
        print(f"inside threading...... filename: {file_name}")
        wf = wave.open(file_name, 'rb')

        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)
        data = wf.readframes(CHUNK)
        while True:
            if data != '':
                stream.write(data)
                data = wf.readframes(CHUNK)
                
            if data == b'':
                print("Inside data check....")
                break
        
        # print("Above soundfile..")
        # f = sf.SoundFile(file_name)
        # delay = len(f)/f.samplerate
        # print(delay)
        stream.close()
    p.terminate()

def play_letter():
    file_name = (textValue.get().lower().strip())
    if len(file_name) < 1:
        return
    
    print(file_name)

    queue = []
    
    for letter in file_name:
        f = "./letters/"+letter+".wav"
        print(f"filename inside for loop: "+f)
        if os.path.isfile(f):
            print("Inside file exists...")
            queue.append(f)
            error_text.config(text="")
        else:
            error_text.config(text="filename does not exixts for: "+ f)
            return

    t = threading.Thread(target= play_queue, args=(queue,))
    t.daemon = True
    t.start()
            
        
        
        
def play_audio():
    global CHUNK

    file_name = (textValue.get().lower().strip())
    if len(file_name) < 1:
        return

    print(f"Initial Filename is: {file_name}")
    file_name = "./words/"+file_name+ ".wav"
    print(file_name)
    if not os.path.isfile(file_name):
        error_text.config(text="filename does not exixts for: "+ file_name)
        return
    error_text.config(text="")
    wf = wave.open(file_name, 'rb')

    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)

    t = threading.Thread(target= play, args=(stream, p, wf,))
    t.start()


def start_counter(label):
  counter = 0
  def count():
    global counter
    if not record_on:
        return
    counter += 1
    label.config(text="Recording: " + str(counter)+ " sec")
    label.after(1000, count)
  count()

def start_rec():
    global record_on, frames, counter_label, counter
    counter = 0
    start_counter(counter_label)

    while record_on:
        data = stream.read(CHUNK)
        data_chunk = array('h',data)
        vol=max(data_chunk)
        if(vol>=500):
            print("something said")
            frames.append(data)
        else:
            print("nothing")
        print("\n")

def record():
    # WAVE_OUTPUT_FILENAME = "output.wav"
    global record_on,p, stream, counter_label
    if record_on:
        return

    frames.clear()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    frames_per_buffer=CHUNK,
                    input=True
                    )

    print("* recording.........")

    record_on = True
    if len(frames) > 0:
        frames.clear()

    t = threading.Thread(target = start_rec)
    t.start()
    
        
    print("* done recording")
    
    
def save_audio():
    global p, CHANNELS, FORMAT, RATE, frames, record_on, counter_label, record_type
    if len(frames) < 1:
        return
    initia_dir = "./words" if record_type.get() == "W" else "./letters"
    filename = asksaveasfilename(initialdir=initia_dir, title="Save as",
            filetypes=(("audio file", "*.wav"), ("all files", "*.*")),
            defaultextension=".wav")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    frames.clear()
    counter_label.config(text="Recording: 0 sec")
    record_on = False

def stop_record():
    global record_on, counter, stream, counter_label,p
    if not record_on:
        print("Recording has not initiated...")
        return
    record_on = False
    # counter_label.destroy()
    stream.stop_stream()
    stream.close()
    # p.terminate()
    stream = None
    print("Recording stopped.....")

# def clear_entry(event, entry):
#     entry.delete(0, END)
#     if entry == text1:
#         if text.get() != "Type something...":
#             text.delete(0, END)
#             text.insert(0, "Type something...")
#         if text2.get() != "Enter file name to save...":
#             text2.delete(0, END)
#             text2.insert(0, "Enter file name to save...")
#     elif entry == text2:
#         if text.get() != "Type something...":
#             text.delete(0, END)
#             text.insert(0, "Type something...")
#         if text1.get() != "Enter file name to save...":
#             text1.delete(0, END)
#             text1.insert(0, "Enter file name to save...")
#     else:
#         if text1.get() != "Enter file name to save...":
#             text1.delete(0, END)
#             text1.insert(0, "Enter file name to save...")
#         if text2.get() != "Enter file name to save...":
#             text2.delete(0, END)
#             text2.insert(0, "Enter file name to save...")

def empty_entry(text):
    text.delete(0, END)  

root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry(f'{width}x{height}')
root.minsize(int(width/2), int(height/2))
root.title("Data Collector")

error_text = Label(root, font=(font, 12, 'bold'))
error_text.place(relx=0.12, rely=(0.1,),)

frame1 = Frame(root, bg='green')
frame1.place(relx=0.12, rely=(0.2,), relwidth=0.8, relheight=0.085)
textValue = StringVar()

text = Entry(frame1, textvariable=textValue, relief=FLAT, bg="#444444", fg="white", justify=CENTER, font=(font, fontsize, 'bold'))
text.place(relx=0, relwidth=0.5, relheight=1)
text.insert(0, "Type something...")
text.bind("<Button-1>", lambda event: empty_entry(text))
# text.pack(side=LEFT, expand=True, fill=BOTH)

# text.grid(row=1, column=0, columnspan=10, pady=50, padx=(200, 40))

playLetBtn = Button(frame1, text="Play Letter", command=play_letter, relief=FLAT, padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
playLetBtn.place(relx=0.53, relwidth=0.2, relheight=1)
# recLetBtn.pack(side=LEFT, fill=BOTH)


playWrdBtn = Button(frame1, text="Play Word", command=play_audio, relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
playWrdBtn.place(relx=0.74, relwidth=0.2, relheight=1)
# recWrdBtn.pack(side=LEFT, fill=BOTH)

label_record_choice = Label(root, text="Please select the type of recording.", font=(font, fontsize, 'bold'))
label_record_choice.place(relx=0.3, rely=0.35)

record_type = StringVar()
record_type.set('W')
Radiobutton(root, text="Record Letter", padx=20, variable=record_type, font=(font, 14, 'bold'), value='L').place(relx=0.3, rely=0.41)
Radiobutton(root, text="Record Word", padx=20, variable=record_type, font=(font, 14, 'bold'), value='W').place(relx=0.3, rely=0.38)

frame2 = Frame(root, bg='green')
frame2.place(relx=0.3, rely=(0.5,), relwidth=0.4, relheight=0.4)

start = Button(frame2, text="Record",relief=FLAT, command=record, padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
start.place(relx=0, rely=0.3, relwidth=0.48, relheight=0.2)

stop = Button(frame2, text="Stop",relief=FLAT, command=stop_record, padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
stop.place(relx=0.52, rely=0.3, relwidth=0.48, relheight=0.2)

saveBtn = Button(frame2, text="Save",relief=FLAT, command=save_audio, padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
saveBtn.place(relx=0.1, rely=0.7, relwidth=0.8, relheight=0.2)

counter_label = Label(frame2, font=(font, fontsize, 'bold'))
counter_label.place(relx=0.3, rely=0.1)

##############################################################################
############################################
# frame21 = Frame(frame2, bg="grey")
# # frame21.pack(side=LEFT, fill=BOTH, expand=True)
# frame21.place(relx=0, rely=0, relwidth=0.45, relheight=1)

# start1 = Button(frame21, text="Start1",relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# start1.place(relx=0, rely=0, relwidth=0.48, relheight=0.2)

# stop1 = Button(frame21, text="Stop1",relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# stop1.place(relx=0.52, relwidth=0.48, relheight=0.2)

# word1text = StringVar()
# text1 = Entry(frame21, textvariable=word1text, relief=FLAT, bg="#444444", fg="white", justify=CENTER, font=(font, fontsize, 'bold'))
# text1.place(relx=0.2, rely=0.4, relwidth=0.6, relheight=0.2)
# text1.insert(0, "Enter file name to save...")
# text1.bind("<Button-1>", lambda event: clear_entry(event, text1))

# saveLetBtn = Button(frame21, text="Save",relief=FLAT, padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# saveLetBtn.place(relx=0.1, rely=0.7, relwidth=0.8, relheight=0.2)

#########################################

# frame22 = Frame(frame2, bg='grey')
# # frame22.pack(side=RIGHT, fill=BOTH, expand=True)
# frame22.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)

# start2 = Button(frame22, text="Start2",relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# start2.place(relx=0, relwidth=0.48, relheight=0.2)

# stop2 = Button(frame22, text="Stop2",relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# stop2.place(relx=0.52, relwidth=0.48, relheight=0.2)

# word2text = StringVar()
# text2 = Entry(frame22, textvariable=word2text, relief=FLAT, bg="#444444", fg="white", justify=CENTER, font=(font, fontsize, 'bold'))
# text2.place(relx=0.2, rely=0.4, relwidth=0.6, relheight=0.2)
# text2.insert(0, "Enter file name to save...")
# text2.bind("<Button-1>", lambda event: clear_entry(event, text2))

# saveWrdBtn = Button(frame22, text="Save",relief=FLAT,padx=10, pady=5, fg="white", bg="blue", font=(font, fontsize, 'bold'))
# saveWrdBtn.place(relx=0.1, rely=0.7, relwidth=0.8, relheight=0.2)

# recLetBtn.pack(side=LEFT, fill=BOTH)

root.mainloop()



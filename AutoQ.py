import base64
import os
import sys
import warnings
from tkinter import NORMAL, DISABLED
import psutil

import requests
from customtkinter import CTk, CTkLabel, CTkButton, set_appearance_mode
from urllib3.exceptions import InsecureRequestWarning

status = False
auth = ''
port = ''
encoded_auth = ''
app = CTk()
app.geometry("300x200")
app.title("Auto Q")
app.resizable(False, False)

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

refresh_timer = 3000
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


app.iconbitmap(resource_path("icon.ico"))
set_appearance_mode("dark")

n = 0
blink = 0

def check_league_client():
    for proc in psutil.process_iter():
        try:
            if "LeagueClient.exe" in proc.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_and_close_app():
    if not check_league_client():
        app.quit()
    else:
        app.after(5000,check_and_close_app)

def get_data(label_status, button):
    global port, auth, encoded_auth, n, blink

    try:
        n += 1
        blink += 1
        file = open("C:/Riot Games/League of Legends/lockfile")
        text = file.readline()
        splitted_array = text.split(':')
        port = splitted_array[2]
        auth = splitted_array[3]
        encoded_auth = base64.b64encode(f"riot:{auth}".encode()).decode()
        label_status.configure(text="status: OFF", text_color="red")
        label_status.place(x=80, y=20)
        button.configure(state=NORMAL, text="toggle")
        check_and_close_app()
    except (IndentationError, FileNotFoundError, UnboundLocalError) as error:
        if blink == 1:
            label_status.configure(text="Client not running.", text_color="red", justify="center")
            label_status.place(x=60, y=20)
        else:
            label_status.configure(text="", text_color="red", justify="center")
            blink = 0
        button.configure(state=DISABLED)

        if n > 5:
            n = 0
        button.configure(text=f"Retrying.{'.' * n}")
        app.after(1000, lambda: get_data(label_status, button))


def toggle():
    global status
    status = not status  # Toggle status
    update_label()
    if status:
        autoaccept()



def update_label():
    if status:
        label_status.configure(text="status: ON", text_color="green")

    else:
        label_status.configure(text="status: OFF", text_color="red")


label_status = CTkLabel(master=app, text="status: OFF", text_color="RED", font=("Ariel", 25))
label_status.place(x=80, y=20)

button = CTkButton(master=app, width=250, height=100, text="toggle", hover_color="black", border_color="yellow",
                   border_width=1, corner_radius=20, fg_color="transparent", text_color="white", font=("Ariel", 20),
                   command=toggle)
button.place(x=25, y=70)
get_data(label_status, button)

old_labels = []



def rm():
    if len(old_labels) > 0:
        for x in old_labels:
            x.destroy()


def autoaccept():

    global status, old_labels, refresh_timer

    get_queue = f"https://127.0.0.1:{port}/lol-matchmaking/v1/ready-check/accept"
    ingame = f'https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase'
    ## vseki ot 0.9 - 2 se da proverqva za q pop
    response_ingame = requests.get(ingame, auth=('riot', auth), verify=False)
    if status:

        refresh_timer=2000
        try:


            print(response_ingame.json())

            if response_ingame.json() == "Matchmaking":

                rm()
                labelQ = CTkLabel(app, text="STATUS : IN QUEUE")
                labelQ.place(x=10, y=170)
                old_labels.append(labelQ)
            elif response_ingame.json() == "ReadyCheck":
                response = requests.post(get_queue, auth=('riot', auth), verify=False)
                response.raise_for_status()
                rm()
                labelQ = CTkLabel(app, text="STATUS : IN QUEUE POP")
                labelQ.place(x=10, y=170)
                old_labels.append(labelQ)
            elif response_ingame.json() == "ChampSelect":
                rm()
                labelQ = CTkLabel(app, text="STATUS : IN CHAMPION SELECT")
                labelQ.place(x=10, y=170)
                old_labels.append(labelQ)
            elif response_ingame.json() == "InProgress":
                rm()
                refresh_timer = 15000
                labelQ = CTkLabel(app, text="STATUS : IN GAME")
                labelQ.place(x=10, y=170)
                old_labels.append(labelQ)
                status= False
                label_status.configure(text="status: OFF",text_color="red")

            else:
                rm()
                labelQ = CTkLabel(app, text="STATUS : IN LOBBY")
                labelQ.place(x=10, y=170)
                old_labels.append(labelQ)
        except requests.exceptions.RequestException as e:
            print(e)


    app.after(refresh_timer, autoaccept)


app.mainloop()

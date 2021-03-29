import speech_recognition as sr
import Speak
import requests
from bs4 import BeautifulSoup
import time
import unidecode
import os
from google_trans_new import google_translator
import psutil

class Assistant:
    def __init__(self):
        Speak.ChangeVoice(0)
        self.vocal=None
        self.temperature=None
        self.get_temperature()
        self.reccur=None
        self.battery = psutil.sensors_battery()
    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Say something!")
            audio = r.listen(source)
        try:
            print("T'as dis " + r.recognize_google(audio,language="fr-FR"))
            self.vocal = r.recognize_google(audio,language="fr-FR").lower()
            self.respond()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


    def respond(self):
        b=time.localtime()
        dico={"température":f"Il fait {self.temperature} actuellement à Villeneuve-La-Garenne",
               "heure":f"Il est {b.tm_hour} heure et {b.tm_min} minutes.","alt f4":"Très bien j'éteins l'ordinateur",
               "éteins l'ordinateur":"Très bien je l'éteins",
               "recap":f"il est actuellement {b.tm_hour} heure et {b.tm_min} minutes et Votre ordinateur est à {self.battery.percent}%"}
        if self.vocal != None:
            kl=False
            for ui in dico.keys():
                if ui in self.vocal:
                    a=dico[ui]
                    kl=True
            if kl == False:
                dtf=responding(self.vocal)
                print(dtf.mess)
                a=dtf.dire()
            print(a)
            Speak.speak(a)
            if "Très bien" in a:
                self.cmd()

        else:
            print("Appel la méthode listen d'abord")


    def get_temperature(self):
        html=requests.get("https://www.lachainemeteo.com/meteo-france/ville-12381/previsions-meteo-villeneuve-la-garenne-heure-par-heure")
        soup = BeautifulSoup(html.text)
        tds=soup.findAll("div",{"class":"tempe"})
        self.temperature=tds[15].find("span").text


    def cmd(self):
        dico={"alt f4":"shutdown/s","éteins l'ordinateur":"shutdown/s"}
        os.system(dico[self.vocal])







class responding:
    def __init__(self,voc):
        self.question=False
        self.work=voc
        self.Answer()
        self.mess=""
    def Answer(self):
        L=self.work.split(" ")
        if L[0][:2] =="qu" or L[0] == "ça" or "combien" or "comment":
            self.question = True
        elif "+" or "-" or "/" or "x" in L:
            self.question = True

    def response_quest(self):
        L=self.work.split(" ")
        mot=None
        print(L[:3])
        if self.question == True:
            try:
                if L[:3] == ['que', 'veut', 'dire']:
                    mot=L[3]
                    print("ui")
                elif L[:4] == ['ça', 'veut', 'dire', 'quoi']:
                    mot=L[4]
                elif L[:2] == ["qu'est-ce", "qu'une"] or L[:2] == ["qu'est-ce", "qu'un"] or L[:2] == ["qu'est-ce", "que"]:
                    mot=L[2]
                elif L[:3] == ["comment","on","dit"]:
                    print("okok")
                    mot="lgg"
                elif L[0] =="combien":
                    mot="jjk"
                elif L[1] == "-" or "+" or "x" or "/":
                    mot="jjk"
            except:
                pass
        if mot != None and mot != "jjk" and mot != "lgg":
            mot=unidecode.unidecode(mot)
            if "'" in mot:
                mot=mot.split("'")[1]
            link=f"https://www.linternaute.fr/dictionnaire/fr/definition/{mot}/"
            html=requests.get(link)
            if html.status_code != 400:
                soup=BeautifulSoup(html.text)
                M=soup.find("div",{"class":"grid_last"})

                string_to_read=mot+" veut dire "
                if M != None:
                    P=M.findAll("a")
                    for ui in P:
                        string_to_read=string_to_read+ui.text+" "
                    self.mess = string_to_read
                else:
                    self.mess = f"Je ne sais pas ce que veut dire {mot} ou alors que j'ai mal compris votre demande."

            else:
                self.mess = f"Je ne sais pas ce que veut dire {mot}"
        elif mot == "jjk":
            return self.calcul()
        elif mot == "lgg":
            return self.translate()
        else:
            self.mess = "Je n'ai pas compris votre demande"


    def calcul(self):
        L=self.work.split(" ")
        try:
            if len(L)!=3:
                k=L[1]
                a=int(L[L.index(k)+1])
                b=int(L[L.index(k)+3])
            else:
                a=int(L[0])
                b=int(L[2])
            dico={"-":str(a-b),"+":str(a+b),"x":str(a*b),"/":str(int(a/b))}
            for ui in dico:
                if ui in L:
                    self.mess = "Cela fait "+dico[ui]
        except:
            self.mess = "Je ne comprends pas"

    def translate(self):
        dico={"anglais":"en","allemand":""}
        L=self.work.split(" ")
        language=L[L.index("en")+1]
        translator = google_translator()
        mess=self.work.split("comment on dit")[1].split("en "+language)[0]
        translate_text = translator.translate(mess,lang_tgt=dico[language])
        self.mess =  "On dit "+translate_text

    def dire(self):
        self.response_quest()
        return self.mess




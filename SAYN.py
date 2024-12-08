import tkinter as tk
import os
import time
import winsound
import requests
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import speech_recognition as sr
import threading

recognizer = sr.Recognizer()

# Tkinter GUI Ayarları
window = tk.Tk()
window.title("Sesli ve Yazılı Asistan")
window.geometry("600x500")

durum_label = tk.Label(window, text="Komutlar için 'Dinle' ve ya yazın.", wraplength=500)
durum_label.pack(pady=20)

dinle_button = tk.Button(window, text="Dinle", command=lambda: threading.Thread(target=daima_dinle, daemon=True).start())
dinle_button.pack(pady=10)

komut_giris = tk.Entry(window, width=50)
komut_giris.pack(pady=10)

gonder_button = tk.Button(window, text="Gönder", command=lambda: komut_analiz_et(komut_giris.get()))
gonder_button.pack(pady=10)

# Dosya adı girişi
dosya_adi_giris = tk.Entry(window, width=50)
dosya_adi_giris.pack(pady=10)
dosya_adi_giris.insert(0, "Dosya adı yazın...")  # Başlangıç metni

dosya_ac_button = tk.Button(window, text="Dosya Aç", command=lambda: dosya_ac(dosya_adi_giris.get()))
dosya_ac_button.pack(pady=10)

# Daima Dinleme Modu
def daima_dinle():
    while True:
        ses_dinle()
        time.sleep(2)  # Dinleme arasında kısa bir süre

# Ses Dinleme Fonksiyonu
def ses_dinle():
    with sr.Microphone() as source:
        try:
            durum_label.config(text="Lütfen konuşun...")
            window.update()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            komut = recognizer.recognize_google(audio, language="tr-TR").lower()
            durum_label.config(text=f"Siz: {komut}")
            komut_analiz_et(komut)
        except sr.UnknownValueError:
            durum_label.config(text="Ses anlaşılamadı, tekrar deneyin.")
        except sr.RequestError:
            durum_label.config(text="API hatası.")
        except sr.WaitTimeoutError:
            durum_label.config(text="Dinleme süresi doldu.")
        except Exception as e:
            durum_label.config(text=f"Hata: {str(e)}")

# Komut Analiz ve İşlevler
def komut_analiz_et(komut):
    try:
        if "google'da ara" in komut:
            arama_terimi = komut.replace("google'da ara", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={arama_terimi}")
            durum_label.config(text=f"Google'da arama yapılıyor: {arama_terimi}")

        elif "youtube'da ara" in komut:
            arama_terimi = komut.replace("youtube'da ara", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={arama_terimi}")
            durum_label.config(text=f"YouTube'da arama yapılıyor: {arama_terimi}")

        elif "hava durumu nedir" in komut:
            hava_durumu_goster()

        elif "not al" in komut:
            notepad_ac()

        elif "e-posta gönder" in komut:
            threading.Thread(target=eposta_gonder, daemon=True).start()

        elif "alarm kur" in komut:
            threading.Thread(target=alarm_kur, args=(komut,), daemon=True).start()

        elif "bilgisayarı kapat" in komut:
            os.system("shutdown /s /t 1")

        elif "bilgisayarı yeniden başlat" in komut:
            os.system("shutdown /r /t 1")

        elif "masaüstünü göster" in komut:
            os.system("powershell -command \"(New-Object -ComObject shell.application).minimizeall()\"")
            durum_label.config(text="Masaüstü gösteriliyor.")

        elif "saat kaç" in komut:
            current_time = time.strftime("%H:%M")
            durum_label.config(text=f"Saat şu anda: {current_time}")

        elif "tarih nedir" in komut:
            current_date = time.strftime("%d/%m/%Y")
            durum_label.config(text=f"Bugünün tarihi: {current_date}")

        elif "çöp kutusunu boşalt" in komut:
            cop_kutusunu_bosalt()

        elif "dosya aç" in komut:
            dosya_ac(dosya_adi_giris.get())

        else:
            durum_label.config(text="Komut anlaşılamadı.")
    except Exception as e:
        durum_label.config(text=f"Bir hata oluştu: {str(e)}")

# Hava Durumu Bilgisi
def hava_durumu_goster():
    api_key = "buraya_api_anahtarınızı_yazın"
    city = "Istanbul"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["cod"] == 200:
            description = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            durum_label.config(text=f"{city} için hava durumu: {description}, {temp}°C")
        else:
            durum_label.config(text="Hava durumu alınamadı.")
    except Exception as e:
        durum_label.config(text=f"Hata: {str(e)}")

# Not Almak için Notepad Açma
def notepad_ac():
    try:
        # Notepad uygulamasını açma
        os.system("start notepad")
        durum_label.config(text="Notepad açıldı.")
    except Exception as e:
        durum_label.config(text=f"Notepad açılırken bir hata oluştu: {str(e)}")

# E-Posta Gönderme
def eposta_gonder():
    try:
        sender_email = "gonderici_email@example.com"  # Buraya gönderici e-posta adresinizi yazın
        receiver_email = "alici_email@example.com"    # Buraya alıcı e-posta adresinizi yazın
        password = "sifre"                            # Buraya gönderici e-posta şifrenizi yazın

        subject = "Sesli Asistan Mesajı"
        body = "Bu mesaj, sesli asistan tarafından gönderildi."

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        durum_label.config(text="E-posta başarıyla gönderildi.")
    except Exception as e:
        durum_label.config(text=f"E-posta gönderiminde hata: {str(e)}")

# Çöp Kutusunu Boşaltma
def cop_kutusunu_bosalt():
    try:
        os.system("rd /s /q %systemdrive%\\$Recycle.Bin")
        durum_label.config(text="Çöp kutusu boşaltıldı.")
    except Exception as e:
        durum_label.config(text=f"Hata: {str(e)}")

# Dosya Açma
def dosya_ac(dosya_adi):
    try:
        # Masaüstündeki dosya yolu (kullanıcıdan alınan dosya adı ile)
        dosya_yolu = os.path.expanduser(f"~/Desktop/{dosya_adi}")  # Bu kısmı sisteminize göre uyarlayın.
        if os.path.exists(dosya_yolu):
            os.system(f"start {dosya_yolu}")
            durum_label.config(text=f"{dosya_adi} açılıyor.")
        else:
            durum_label.config(text="Dosya bulunamadı.")
    except Exception as e:
        durum_label.config(text=f"Dosya açılamadı: {str(e)}")

# Alarm Kurma
def alarm_kur(komut):
    try:
        saat = komut.split("alarm kur ")[-1]
        alarm_zamani = datetime.strptime(saat, "%H:%M")
        suan = datetime.now()
        fark = alarm_zamani - suan
        if fark.days < 0:
            fark = alarm_zamani.replace(year=suan.year + 1) - suan
        time.sleep(fark.total_seconds())
        winsound.Beep(1000, 1000)  # Alarm sesi
        durum_label.config(text=f"Alarm! {saat} geldi.")
    except Exception as e:
        durum_label.config(text=f"Alarm kurulamadı: {str(e)}")

# Tkinter uygulaması çalıştırma
window.mainloop()

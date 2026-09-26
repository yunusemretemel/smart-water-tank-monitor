# =============================================================================
# --- 1. BÖLÜM: KÜTÜPHANELER (GEREKLİ ARAÇLAR) ---
# =============================================================================
import serial   # Bilgisayarın USB portuyla (Arduino ile) konuşmak için
import json     # Gelen karmaşık veriyi ({"a":1}) Python'un anlayacağı hale getirmek için
import threading # Arayüz donmasın diye "Çoklu İş Parçacığı" (Arka plan işçisi)
import time     # Zamanla ilgili bekleme işlemleri için
import customtkinter as ctk # Modern ve şık pencereler oluşturmak için (GUI)
from collections import deque # Grafikteki verileri tutan, dolunca eskisini silen akıllı liste
import matplotlib.pyplot as plt # Profesyonel grafik çizimi yapmak için
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Grafiği pencerenin içine gömmek için
from datetime import datetime # O anki tarih ve saati bulmak için
import os       # Bilgisayarın dosya yollarını (C:/Users/...) yönetmek için
from tkinter import filedialog # Açılan "Klasör Seç" penceresi için

# =============================================================================
# --- 2. BÖLÜM: AYARLAR VE BAŞLANGIÇ HAZIRLIĞI ---
# =============================================================================

ARDUINO_PORT = 'COM5'  # <-- ÖNEMLİ: Arduino'nun takılı olduğu portu buraya yaz!
BAUD_RATE = 9600       # Arduino kodundaki "Serial.begin(9600)" ile aynı hızda olmalı.

# --- KLASÖR SEÇME İŞLEMİ ---
print("Lütfen açılan pencereden kayıt klasörünü seçin...")
# Kullanıcıya bir pencere açar ve klasör seçtirir. Seçilen yolu 'secilen_klasor'e atar.
secilen_klasor = filedialog.askdirectory(title="Kayıt Dosyalarının Oluşturulacağı Klasörü Seçin")

# Eğer kullanıcı pencereyi kapatırsa veya seçim yapmazsa hata vermesin,
# programın çalıştığı mevcut klasörü (os.getcwd) kullansın.
if not secilen_klasor:
    secilen_klasor = os.getcwd()

# Dosya yollarını birleştiriyoruz (Örn: C:/Masaüstü/ + anlik_veri.json)
ANLIK_DOSYA = os.path.join(secilen_klasor, "anlik_veri.json")   # Arayüzün okuyacağı dosya
GECMIS_DOSYA = os.path.join(secilen_klasor, "gecmis_veriler.txt") # Rapor tutulacak dosya

print(f"SEÇİLEN YOL: {secilen_klasor}") # Seçilen yeri konsola yaz (Kontrol için)

# --- GRAFİK HAFIZASI ---
max_veri_sayisi = 50 # Grafikte aynı anda en fazla kaç nokta görünsün?
# deque: Listeye benzer ama kapasitesi dolunca en eski veriyi otomatik siler.
su_gecmisi = deque([0]*max_veri_sayisi, maxlen=max_veri_sayisi) 
zaman_ekseni = list(range(max_veri_sayisi)) # X ekseni için 0, 1, 2... 49 sayıları

# Arayüzün temasını ayarla (Karanlık Mod ve Mavi Renk)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =============================================================================
# --- 3. BÖLÜM: ANA PROGRAM SINIFI ---
# =============================================================================
class SuTakipUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__() # Pencere özelliklerini miras al

        # --- PENCERE AYARLARI ---
        self.title("Akıllı Depo - Klasör Seçmeli Sistem") # Pencere başlığı
        self.geometry("950x650") # Pencere boyutu (Genişlik x Yükseklik)
        
        # Ekranı ızgaraya bölüyoruz (Sol taraf sabit, sağ taraf esnek)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (BİLGİLER VE BUTONLAR) ---
        # Sol tarafa gri bir kutu (Frame) çiziyoruz
        self.sol_frame = ctk.CTkFrame(self, width=250, corner_radius=15)
        self.sol_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        
        # Başlık Yazısı
        ctk.CTkLabel(self.sol_frame, text="KAYIT YERİ", font=("Roboto", 20, "bold")).pack(pady=20)
        
        # Seçilen klasör yolunu ekranda göstermek için ayarlamalar
        gosterilecek_yol = GECMIS_DOSYA
        if len(gosterilecek_yol) > 40: # Eğer yol çok uzunsa...
            gosterilecek_yol = "..." + gosterilecek_yol[-35:] # ...sadece son kısmını göster.

        # Yol bilgisini yazan etiket
        self.lbl_bilgi = ctk.CTkLabel(self.sol_frame, text=f"Dosyalar Burada:\n{gosterilecek_yol}", 
                                      font=("Arial", 12), text_color="#ffa200", wraplength=230)
        self.lbl_bilgi.pack(pady=10)

        # Yağmur Bölümü
        ctk.CTkLabel(self.sol_frame, text="HAVA DURUMU", font=("Roboto", 14)).pack(pady=(20, 0))
        # Tıklanmayan buton (Görsel amaçlı kutu)
        self.box_yagmur = ctk.CTkButton(self.sol_frame, text="BEKLENİYOR", fg_color="gray", height=50, width=200, state="disabled", text_color="white", font=("Arial", 16, "bold"))
        self.box_yagmur.pack(pady=5)

        # Su Bölümü
        ctk.CTkLabel(self.sol_frame, text="SU SEVİYESİ", font=("Roboto", 14)).pack(pady=(30, 0))
        # Su değerini sayı olarak gösteren etiket
        self.lbl_su_deger = ctk.CTkLabel(self.sol_frame, text="0", font=("Roboto", 40, "bold"), text_color="#3498db")
        self.lbl_su_deger.pack(pady=5)
        
        # İlerleme Çubuğu (Progress Bar)
        self.su_bar = ctk.CTkProgressBar(self.sol_frame, orientation="horizontal", width=200)
        self.su_bar.set(0) # Başlangıçta 0 olsun
        self.su_bar.pack(pady=10)

        # Saat Göstergesi
        ctk.CTkLabel(self.sol_frame, text="Son Veri Saati:", font=("Arial", 10)).pack(pady=(30, 0))
        self.lbl_zaman = ctk.CTkLabel(self.sol_frame, text="--:--:--", font=("Arial", 14, "bold"), text_color="#f1c40f")
        self.lbl_zaman.pack(pady=0)

        # --- SAĞ PANEL (GRAFİK ALANI) ---
        self.sag_frame = ctk.CTkFrame(self, corner_radius=15)
        self.sag_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Matplotlib kütüphanesi ile grafik oluşturuyoruz
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b') # Grafiğin dış arka planı
        self.ax.set_facecolor('#2b2b2b')        # Çizim alanı arka planı
        
        # Çizgiyi tanımlıyoruz (Rengi turkuaz)
        self.line, = self.ax.plot(zaman_ekseni, su_gecmisi, color='#00ffcc', linewidth=2)
        
        # Grafik ayarları (Başlık, Izgara, Eksenler)
        self.ax.set_title("Canlı Veri Akışı", color='white')
        self.ax.set_ylim(0, 800) # Y ekseni 0-800 arası sabit kalsın
        self.ax.tick_params(colors='white') # Sayılar beyaz olsun
        self.ax.grid(True, color='#444444', linestyle='--') # Izgara çizgileri

        # Grafiği Tkinter penceresine gömüyoruz
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.sag_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # --- İŞLEMLERİ BAŞLAT ---
        # 1. İşlem: Arduino'yu dinleyip dosyaya yazan "Thread"i (arka plan işçisi) başlat.
        threading.Thread(target=self.arduino_dinle_ve_kaydet, daemon=True).start()
        
        # 2. İşlem: Dosyadan okuyup ekranı güncelleyen döngüyü başlat.
        self.dosyadan_oku_ve_guncelle()

    # =========================================================================
    # --- FONKSİYON 1: YAZICI (ARDUINO -> DOSYA) ---
    # =========================================================================
    def arduino_dinle_ve_kaydet(self):
        try:
            # Seri portu açıyoruz
            ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            print(f"Kayıt Başladı! Konum: {secilen_klasor}")
            
            while True: # Sonsuz döngü
                if ser.in_waiting > 0: # Eğer kablodan veri geliyorsa...
                    try:
                        # Gelen satırı oku, temizle ve JSON'a çevir
                        line = ser.readline().decode('utf-8').strip()
                        veri = json.loads(line)
                        
                        # O anki tarih ve saati al
                        simdi = datetime.now()
                        tarih_saat = simdi.strftime("%d.%m.%Y %H:%M:%S")
                        
                        # --- 1. DOSYA: ANLIK VERİ (JSON) ---
                        # Arayüzün okuması için sürekli üzerine yazar ('w' modu)
                        veri["zaman"] = tarih_saat # Saati de veriye ekle
                        with open(ANLIK_DOSYA, "w") as f:
                            json.dump(veri, f)

                        # --- 2. DOSYA: GEÇMİŞ KAYIT (TXT) ---
                        # Rapor için sürekli altına ekler ('a' - append modu)
                        satir = f"{tarih_saat} | Yagmur: {veri['yagmur']} | Su: {veri['su']}\n"
                        with open(GECMIS_DOSYA, "a", encoding="utf-8") as log:
                            log.write(satir)
                            log.flush() # Veriyi bekletmeden hemen diske yaz!
                            
                    except:
                        pass # Hata olursa (bozuk veri vs.) görmezden gel
        except:
            print("Port Hatası! Arduino bağlı mı?") # Bağlantı koparsa uyar

    # =========================================================================
    # --- FONKSİYON 2: OKUYUCU (DOSYA -> EKRAN) ---
    # =========================================================================
    def dosyadan_oku_ve_guncelle(self):
        try:
            # Anlık veri dosyasını okumaya çalış
            with open(ANLIK_DOSYA, "r") as dosya:
                kayitli_veri = json.load(dosya)
                
                # Verileri değişkenlere çek (Bulamazsa 0 varsay)
                yagmur = int(kayitli_veri.get("yagmur", 0))
                su = int(kayitli_veri.get("su", 0))
                zaman = kayitli_veri.get("zaman", "--:--:--")
                
                # Ekrana saati yaz
                self.lbl_zaman.configure(text=zaman)
                
                # Yağmur Mantığı
                if yagmur < 800:
                    self.box_yagmur.configure(text="YAĞMUR YAĞIYOR", fg_color="#e74c3c") # Kırmızı
                else:
                    self.box_yagmur.configure(text="HAVA AÇIK", fg_color="#2ecc71") # Yeşil
                
                # Su Seviyesi ve Çubuk Güncelleme
                self.lbl_su_deger.configure(text=str(su))
                oran = su / 700 # Bar 0-1 arası çalıştığı için oranlıyoruz
                if oran > 1: oran = 1 # Taşmayı engelle
                self.su_bar.set(oran)
                
                # Grafiği Güncelle
                su_gecmisi.append(su) # Yeni veriyi listeye ekle
                self.line.set_ydata(su_gecmisi) # Çizgiyi yenile
                self.canvas.draw_idle() # Grafiği tekrar çiz
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass # Dosya henüz oluşmadıysa sorun etme, bekle.

        # Bu fonksiyonu 100 milisaniye sonra tekrar çalıştır (Sürekli Döngü)
        self.after(100, self.dosyadan_oku_ve_guncelle)

# =============================================================================
# --- 4. BÖLÜM: PROGRAMI BAŞLATMA ---
# =============================================================================
if __name__ == "__main__":
    app = SuTakipUygulamasi() # Uygulama sınıfından bir örnek yarat
    app.mainloop() # Pencereyi kapatılana kadar açık tut
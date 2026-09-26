#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- PİNLER ---
const int yagmurSensorPin = A0;
const int suSensorPin = A1;

const int yagmurLed = 2;
const int suLed1 = 3; // Az
const int suLed2 = 4; // Orta
const int suLed3 = 5; // Yüksek

// --- EŞİK DEĞERLERİ ---
int yagmurEsik = 800; // 800 altı yağmur var demektir

// Su Seviyeleri
int sinirAz = 200;    // 200'ü geçerse "Az"
int sinirOrta = 450;  // 450'yi geçerse "Orta"
int sinirYuksek = 600;// 600'ü geçerse "Yüksek"

// Zamanlayıcı
unsigned long oncekiZaman = 0;
bool ledDurumu = LOW;

void setup() {
  Serial.begin(9600); 
  lcd.init();
  lcd.backlight();
  
  pinMode(yagmurLed, OUTPUT);
  pinMode(suLed1, OUTPUT);
  pinMode(suLed2, OUTPUT);
  pinMode(suLed3, OUTPUT);
  
  // Açılış Testi
  lcd.setCursor(0, 0);
  lcd.print("Akilli Depo");
  lcd.setCursor(0, 1);
  lcd.print("Sistemi v3.0");
  delay(1500);
  lcd.clear();
}

void loop() {
  unsigned long simdikiZaman = millis();

  // 1. Sensörleri Oku (Hatasız okuma tekniği ile)
  int yagmurDegeri = analogRead(yagmurSensorPin);
  delay(20); 
  analogRead(suSensorPin); 
  delay(10);
  int suDegeri = analogRead(suSensorPin); 

  // 2. Python'a Veri Gönder (JSON)
  Serial.print("{\"yagmur\":");
  Serial.print(yagmurDegeri);
  Serial.print(", \"su\":");
  Serial.print(suDegeri);
  Serial.println("}");

  // --- MANTIK KONTROLÜ ---
  
  // Yağmur Var mı? (Boolean değişken)
  bool yagmurYagiyor = (yagmurDegeri < yagmurEsik);
  
  // Yağmur LED Kontrolü
  if (yagmurYagiyor) digitalWrite(yagmurLed, HIGH);
  else digitalWrite(yagmurLed, LOW);

  // LCD Üst Satır
  lcd.setCursor(0, 0);
  if (yagmurYagiyor) lcd.print("Yagmur: YAGIYOR ");
  else lcd.print("Yagmur: YOK     ");

  // --- SU SEVİYESİ VE ALARM MANTIĞI ---
  lcd.setCursor(0, 1);

  // DURUM 1: SU YÜKSEK (Kritik Bölge)
  if (suDegeri >= sinirYuksek) {
    
    // Eğer SU YÜKSEK **VE** YAĞMUR YAĞIYORSA -> FLAŞÖR (ALARM)
    if (yagmurYagiyor) {
       lcd.print("RISK: TASMA!    ");
       
       if (simdikiZaman - oncekiZaman >= 200) { // Hızlı yanıp sönme
          oncekiZaman = simdikiZaman;
          ledDurumu = !ledDurumu;
          digitalWrite(suLed1, ledDurumu);
          digitalWrite(suLed2, ledDurumu);
          digitalWrite(suLed3, ledDurumu);
       }
    } 
    // Eğer SADECE SU YÜKSEKSE (Yağmur Yoksa) -> SABİT YAN
    else {
       lcd.print("Su: YUKSEK/DOLU ");
       digitalWrite(suLed1, HIGH);
       digitalWrite(suLed2, HIGH);
       digitalWrite(suLed3, HIGH);
    }
  }
  
  // DURUM 2: SU ORTA
  else if (suDegeri >= sinirOrta) {
    lcd.print("Su: ORTA        ");
    digitalWrite(suLed1, HIGH);
    digitalWrite(suLed2, HIGH);
    digitalWrite(suLed3, LOW);
  }
  
  // DURUM 3: SU AZ (veya Boş'un biraz üstü)
  else if (suDegeri >= sinirAz) {
    lcd.print("Su: AZ          ");
    digitalWrite(suLed1, HIGH);
    digitalWrite(suLed2, LOW);
    digitalWrite(suLed3, LOW);
  }
  
  // DURUM 4: SU BOŞ
  else {
    lcd.print("Su: BOS         ");
    // Boşken hepsi sönük olsun (veya sadece 1. loş yanabilir, şimdilik söndürdük)
    digitalWrite(suLed1, LOW); 
    digitalWrite(suLed2, LOW); 
    digitalWrite(suLed3, LOW);
  }

  delay(50); // Sistem hızı
}
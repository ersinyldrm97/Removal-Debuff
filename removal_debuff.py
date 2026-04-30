import cv2
import numpy as np
import pyautogui
import keyboard
import time
import threading
import tkinter as tk
from tkinter import scrolledtext

# --- AYARLAR (DEĞİŞTİRİLMEDİ) ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

BERSERKER_ICON = 'images/berserker_70.png'
DEBUFF_ICON = 'images/torment.png'
PARAZIT_ICON = 'images/parazit.png'
SUPER_PARAZIT_ICON = 'images/super_parazit.png'
MALICE_ICON = 'images/malice.png'

THRESHOLD_BERSERKER = 0.85
THRESHOLD_DEBUFF = 0.80
THRESHOLD_PARAZIT = 0.80
THRESHOLD_SUPER_PARAZIT = 0.80
THRESHOLD_MALICE = 0.80

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCAN_REGION = (
    int(SCREEN_WIDTH * 0.2),
    int(SCREEN_HEIGHT * 0.05),
    int(SCREEN_WIDTH * 0.6),
    int(SCREEN_HEIGHT * 0.4)
)

class WarriorBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Warrior Debuff Bot")
        self.root.geometry("400x600")
        self.root.attributes("-topmost", True)  # Pencereyi hep üstte tutar

        self.is_running = False
        self.bot_thread = None
        self.shield_coords = None
        self.shield_equipped = False
        self.tracking_mouse = False

        # --- Arayüz Tasarımı ---
        # --- Koordinat Takip Bölümü ---
        coord_frame = tk.LabelFrame(root, text="Kalkan Koordinatı", padx=10, pady=5)
        coord_frame.pack(pady=5, fill="x", padx=10)
        self.bot_start = tk.Label(coord_frame, text="BOTUN BAŞLATILMASI İÇİN  SHIFT TUŞUNA BASINIZ", font=("Consolas", 10), fg="blue")
        self.bot_start.pack(pady=2)

        self.bot_stop = tk.Label(coord_frame, text="BOTU DURDURMAK İÇİN  SHIFT TUŞUNA BASINIZ", font=("Consolas", 10), fg="blue")
        self.bot_stop.pack(pady=2)

        self.mouse_label = tk.Label(coord_frame, text="Fare: X=0, Y=0", font=("Consolas", 10), fg="blue")
        self.mouse_label.pack(pady=2)

        self.track_button = tk.Button(coord_frame, text="Koordinat Takibi BAŞLAT", command=self.toggle_tracking, bg="#4a90d9", fg="white", width=25)
        self.track_button.pack(pady=2)

        self.save_coord_button = tk.Button(coord_frame, text="Mevcut Koordinatı KAYDET (Kalkan)", command=self.save_shield_coords, bg="#e67e22", fg="white", width=25)
        self.save_coord_button.pack(pady=2)

        self.shield_label = tk.Label(coord_frame, text="Kalkan: X=1570, Y=490", font=("Consolas", 10), fg="green")
        self.shield_label.pack(pady=2)

        self.status_label = tk.Label(root, text="BOT DURDURULDU", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(root, text="BAŞLAT", command=self.start_bot, bg="green", fg="white", width=15, height=2)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="DURDUR", command=self.stop_bot, bg="red", fg="white", width=15, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=45, height=15)
        self.log_area.pack(pady=10)

        self.log("Bot Hazır. Başlat butonuna basın.")
        self.log("Kalkan koordinatı için: Koordinat Takibi başlatın,")
        self.log("fareyi kalkan üzerine getirin ve KAYDET'e basın.")
        self.log("Başlatmak/Durdurmak için 'Shift' tuşunu kullanabilirsiniz.")

        keyboard.add_hotkey('shift', self.on_shift_pressed)

    def on_shift_pressed(self):
        self.root.after(0, self.toggle_bot)

    def toggle_bot(self):
        if self.is_running:
            self.stop_bot()
        else:
            self.start_bot()

    def log(self, message):
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)

    def toggle_tracking(self):
        self.tracking_mouse = not self.tracking_mouse
        if self.tracking_mouse:
            self.track_button.config(text="Koordinat Takibi DURDUR", bg="#c0392b")
            self.update_mouse_position()
        else:
            self.track_button.config(text="Koordinat Takibi BAŞLAT", bg="#4a90d9")

    def update_mouse_position(self):
        if self.tracking_mouse:
            x, y = pyautogui.position()
            self.mouse_label.config(text=f"Fare: X={x}, Y={y}")
            self.root.after(50, self.update_mouse_position)

    def save_shield_coords(self):
        x, y = pyautogui.position()
        self.shield_coords = (x, y)
        self.shield_label.config(text=f"Kalkan: X={x}, Y={y}", fg="green")
        self.log(f"Kalkan koordinatı kaydedildi: ({x}, {y})")

    def load_images(self):
        ber_img = cv2.imread(BERSERKER_ICON, 0)
        deb_img = cv2.imread(DEBUFF_ICON, 0)
        par_img = cv2.imread(PARAZIT_ICON, 0)
        super_par_img = cv2.imread(SUPER_PARAZIT_ICON, 0)
        malice_img = cv2.imread(MALICE_ICON, 0)
        
        if ber_img is None or deb_img is None or par_img is None or super_par_img is None or malice_img is None:
            self.log("Hata: Resim dosyaları bulunamadı!")
            return None
        return ber_img, deb_img, par_img, super_par_img, malice_img

    def find_icon(self, haystack_gray, needle_gray, threshold, offset=(0, 0)):
        result = cv2.matchTemplate(haystack_gray, needle_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = needle_gray.shape
            actual_x = offset[0] + max_loc[0] + w // 2
            actual_y = offset[1] + max_loc[1] + h // 2
            return (actual_x, actual_y), max_val
        return None, max_val

    def left_double_click(self, x, y, duration=0, delay=0.03):
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.mouseDown(button='left')
        time.sleep(delay)
        pyautogui.mouseUp(button='left')
        time.sleep(delay)
        pyautogui.mouseDown(button='left')
        time.sleep(delay)
        pyautogui.mouseUp(button='left')
        time.sleep(delay)

    def right_click(self, x, y, duration=0, delay=0.25):
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(delay)
        pyautogui.mouseDown(button='right')
        time.sleep(delay)
        pyautogui.mouseUp(button='right')
        time.sleep(delay)
        pyautogui.moveTo(963, 392, duration=duration)

    def run_bot_logic(self):
        templates = self.load_images()
        if not templates:
            self.is_running = False
            return
            
        berserker_template, debuff_template, parazit_template, super_parazit_template, malice_template = templates
        self.log("Tarama başlatıldı...")

        while self.is_running:
            img = pyautogui.screenshot(region=SCAN_REGION)
            img_np = np.array(img)
            gray_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            # --- DEBUFF KONTROLÜ (Torment, Parazit, Süper Parazit, Malice) ---
            debuff_found = False
            debuff_name = ""

            # Sırayla tüm debuff'ları kontrol et
            deb_coords, _ = self.find_icon(gray_img, debuff_template, THRESHOLD_DEBUFF, offset=SCAN_REGION[:2])
            if deb_coords:
                debuff_found = True
                debuff_name = "Torment"

            if not debuff_found:
                deb_coords, _ = self.find_icon(gray_img, parazit_template, THRESHOLD_PARAZIT, offset=SCAN_REGION[:2])
                if deb_coords:
                    debuff_found = True
                    debuff_name = "Parazit"

            if not debuff_found:
                deb_coords, _ = self.find_icon(gray_img, super_parazit_template, THRESHOLD_SUPER_PARAZIT, offset=SCAN_REGION[:2])
                if deb_coords:
                    debuff_found = True
                    debuff_name = "Süper Parazit"

            if not debuff_found:
                deb_coords, _ = self.find_icon(gray_img, malice_template, THRESHOLD_MALICE, offset=SCAN_REGION[:2])
                if deb_coords:
                    debuff_found = True
                    debuff_name = "Malice"

            if debuff_found:
                # Debuff ekranda → Berserker varsa iptal et
                ber_coords, _ = self.find_icon(gray_img, berserker_template, THRESHOLD_BERSERKER, offset=SCAN_REGION[:2])
                if ber_coords:
                    self.log(f"{debuff_name} bulundu! Berserker iptal ediliyor...")
                    self.left_double_click(ber_coords[0], ber_coords[1])
                    time.sleep(0.05)

                # Kalkan takılı değilse → tak
                if self.shield_coords and not self.shield_equipped:
                    self.log(f"{debuff_name} tespit edildi! Kalkan takılıyor: ({self.shield_coords[0]}, {self.shield_coords[1]})")
                    self.right_click(self.shield_coords[0], self.shield_coords[1])
                    self.shield_equipped = True
                    time.sleep(0.05)
            else:
                # Hiçbir debuff yok → kalkan takılıysa silaha geri geç
                if self.shield_equipped and self.shield_coords:
                    self.log(f"Debuff kalktı! Silaha geçiliyor: ({self.shield_coords[0]}, {self.shield_coords[1]})")
                    self.right_click(self.shield_coords[0], self.shield_coords[1])
                    self.shield_equipped = False
                    time.sleep(0.05)

            time.sleep(0.03)

    def start_bot(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="BOT ÇALIŞIYOR", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.bot_thread = threading.Thread(target=self.run_bot_logic, daemon=True)
            self.bot_thread.start()
            self.log("Bot başlatıldı.")

    def stop_bot(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="BOT DURDURULDU", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("Bot durduruldu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarriorBotGUI(root)
    root.mainloop()
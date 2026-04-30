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
DEBUFF_ICON = 'images/priest_debuff.png'
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
        self.root.geometry("400x500")
        self.root.attributes("-topmost", True)  # Pencereyi hep üstte tutar

        self.is_running = False
        self.bot_thread = None

        # --- Arayüz Tasarımı ---
        self.status_label = tk.Label(root, text="BOT DURDURULDU", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(root, text="BAŞLAT", command=self.start_bot, bg="green", fg="white", width=15, height=2)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="DURDUR", command=self.stop_bot, bg="red", fg="white", width=15, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=45, height=15)
        self.log_area.pack(pady=10)

        self.log("Bot Hazır. Başlat butonuna basın.")

    def log(self, message):
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)

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

    def run_bot_logic(self):
        templates = self.load_images()
        if not templates:
            self.is_running = False
            return
            
        berserker_template, debuff_template, parazit_template, super_parazit_template, malice_template = templates
        self.log("Tarama başlatıldı...")

        while self.is_running:
            if keyboard.is_pressed('q'):
                self.log("Klavye ile kapatıldı.")
                self.root.after(0, self.stop_bot)
                break

            img = pyautogui.screenshot(region=SCAN_REGION)
            img_np = np.array(img)
            gray_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            deb_coords, d_val = self.find_icon(gray_img, debuff_template, THRESHOLD_DEBUFF, offset=SCAN_REGION[:2])
            if not deb_coords:
                deb_coords, d_val = self.find_icon(gray_img, parazit_template, THRESHOLD_PARAZIT, offset=SCAN_REGION[:2])
            if not deb_coords:
                deb_coords, d_val = self.find_icon(gray_img, super_parazit_template, THRESHOLD_SUPER_PARAZIT, offset=SCAN_REGION[:2])
            if not deb_coords:
                deb_coords, d_val = self.find_icon(gray_img, malice_template, THRESHOLD_MALICE, offset=SCAN_REGION[:2])
            
            if deb_coords:
                ber_coords, b_val = self.find_icon(gray_img, berserker_template, THRESHOLD_BERSERKER, offset=SCAN_REGION[:2])
                if ber_coords:
                    self.log(f"KRİTİK: Debuff/Parazit bulundu! Çift tıklanıyor...")
                    self.left_double_click(ber_coords[0], ber_coords[1])
                    time.sleep(0.05)
                else:
                    self.log("Berserker ikonu ekranda bulunamadı!")

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
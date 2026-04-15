import requests
import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import os
import sys
import ctypes

class SettingsManager:
    FILE_PATH = "settings.json"
    DEFAULT = {"theme": "System", "accent": "Blue"}

    @classmethod
    def load(cls):
        if os.path.exists(cls.FILE_PATH):
            try:
                with open(cls.FILE_PATH, "r") as f:
                    return json.load(f)
            except: pass
        return cls.DEFAULT

    @classmethod
    def save(cls, theme, accent):
        with open(cls.FILE_PATH, "w") as f:
            json.dump({"theme": theme, "accent": accent}, f)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GoogleIconFont:
    FILE_NAME = "MaterialIcons-Regular.ttf"
    URL = "https://github.com/google/material-design-icons/raw/master/font/MaterialIcons-Regular.ttf"
    FAMILY = "Material Icons"
    SETTINGS = "\ue8b8"
    CLOSE = "\ue5cd"

    @classmethod
    def load(cls):
        path = resource_path(cls.FILE_NAME)
        if not os.path.exists(path):
            try:
                r = requests.get(cls.URL, allow_redirects=True, timeout=5)
                with open(path, 'wb') as f:
                    f.write(r.content)
            except: pass
        
        if os.path.exists(path):
            ctk.FontManager.load_font(path)
            return True
        return False

PALETTES = {
    "Blue":   {"main": "#1a73e8", "bg": ("#f0f4f8", "#111418"), "card": ("#d3e3fd", "#1e242c"), "entry": ("#ffffff", "#15191e"), "text": ("#041e49", "#d3e3fd")},
    "Green":  {"main": "#34a853", "bg": ("#f0f7f1", "#101612"), "card": ("#c4eed0", "#1a231d"), "entry": ("#ffffff", "#141b16"), "text": ("#072711", "#c4eed0")},
    "Purple": {"main": "#a142f4", "bg": ("#f8f4fb", "#161219"), "card": ("#eaddff", "#2b2131"), "entry": ("#ffffff", "#1d1721"), "text": ("#21005d", "#eaddff")},
    "Orange": {"main": "#fbbc04", "bg": ("#fff8f4", "#1a1612"), "card": ("#ffdf99", "#2e2418"), "entry": ("#ffffff", "#211a14"), "text": ("#291a00", "#ffdf99")},
    "Black":  {"main": "#404040", "bg": ("#f4f4f4", "#121212"), "card": ("#e3e3e3", "#1e1e1e"), "entry": ("#ffffff", "#171717"), "text": ("#000000", "#e3e3e3")}
}

FONT_MAIN = "Segoe UI" if sys.platform == "win32" else "Roboto"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        if sys.platform == "win32":
            myappid = 'mycompany.kegeansw.1.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        try: self.iconbitmap(resource_path("icon.ico"))
        except: pass 

        self.has_icons = GoogleIconFont.load()
        self.icon_font = (GoogleIconFont.FAMILY, 26) if self.has_icons else (FONT_MAIN, 20)
        self.icon_settings = GoogleIconFont.SETTINGS if self.has_icons else "⚙"
        self.icon_close = GoogleIconFont.CLOSE if self.has_icons else "✕"

        self.settings = SettingsManager.load()
        self.current_accent = self.settings.get("accent", "Blue")
        if self.current_accent not in PALETTES:
            self.current_accent = "Blue"
        
        self.title("KegeAnsw")
        self.geometry("460x700")
        
        ctk.set_appearance_mode(self.settings["theme"])
        self.configure(fg_color=PALETTES[self.current_accent]["bg"])

        self.build_main_screen()
        self.build_settings_popup()
        
        self.settings_frame.place(relx=0.5, rely=1.5, anchor="center")
        self.popup_is_open = False

    def animate_popup(self, target_rely, current_rely=None):
        if current_rely is None:
            current_rely = float(self.settings_frame.place_info().get('rely', 1.5))
        diff = target_rely - current_rely
        step = diff * 0.2
        if abs(diff) < 0.005:
            self.settings_frame.place(relx=0.5, rely=target_rely, anchor="center")
            return
        new_rely = current_rely + step
        self.settings_frame.place(relx=0.5, rely=new_rely, anchor="center")
        self.after(16, self.animate_popup, target_rely, new_rely)

    def toggle_settings(self):
        self.settings_frame.lift()
        if self.popup_is_open:
            self.animate_popup(target_rely=1.5)
            self.popup_is_open = False
        else:
            self.animate_popup(target_rely=0.5)
            self.popup_is_open = True

    def build_main_screen(self):
        colors = PALETTES[self.current_accent]
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        self.settings_btn = ctk.CTkButton(
            self.main_frame, text=self.icon_settings, width=40, height=40, corner_radius=20,
            fg_color="transparent", text_color=colors["text"], font=self.icon_font,
            hover_color=colors["card"], command=self.toggle_settings
        )
        self.settings_btn.place(relx=0.95, rely=0.03, anchor="ne")

        self.title_label = ctk.CTkLabel(self.main_frame, text="KegeAnsw", font=(FONT_MAIN, 28, "bold"), text_color=colors["text"])
        self.title_label.pack(pady=(50, 20), padx=25, anchor="w")

        self.input_card = ctk.CTkFrame(self.main_frame, corner_radius=25, fg_color=colors["card"])
        self.input_card.pack(fill=ctk.X, padx=20, pady=(0, 20))

        self.entry = ctk.CTkEntry(
            self.input_card, placeholder_text="ID варианта", height=50, corner_radius=15,
            border_width=0, fg_color=colors["entry"], text_color=colors["text"], font=(FONT_MAIN, 15)
        )
        self.entry.pack(side=ctk.LEFT, padx=(20, 10), pady=15, expand=True, fill=ctk.X)
        self.entry.bind('<Return>', self.fetch_answers)

        self.btn = ctk.CTkButton(
            self.input_card, text="Найти", command=self.fetch_answers, height=50, width=90, 
            corner_radius=15, font=(FONT_MAIN, 15, "bold"), fg_color=colors["main"], hover_color=colors["text"]
        )
        self.btn.pack(side=ctk.RIGHT, padx=(0, 20), pady=15)

        self.output_card = ctk.CTkFrame(self.main_frame, corner_radius=25, fg_color=colors["card"])
        self.output_card.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(0, 30))

        self.output_area = ctk.CTkTextbox(self.output_card, font=("Courier New", 15), fg_color="transparent", text_color=colors["text"])
        self.output_area.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        self.output_area.configure(state='disabled')

    def build_settings_popup(self):
        colors = PALETTES[self.current_accent]
        self.settings_frame = ctk.CTkFrame(self, width=320, height=360, corner_radius=0, fg_color=colors["card"])
        self.settings_frame.pack_propagate(False)

        self.close_btn = ctk.CTkButton(
            self.settings_frame, text=self.icon_close, width=40, height=40, corner_radius=20,
            fg_color="transparent", text_color=colors["text"], font=self.icon_font,
            hover_color=colors["bg"], command=self.toggle_settings
        )
        self.close_btn.place(relx=0.92, rely=0.05, anchor="ne")

        self.settings_title = ctk.CTkLabel(self.settings_frame, text="Настройки", font=(FONT_MAIN, 22, "bold"), text_color=colors["text"])
        self.settings_title.pack(pady=(40, 30))

        self.theme_label = ctk.CTkLabel(self.settings_frame, text="Режим оформления:", font=(FONT_MAIN, 14), text_color=colors["text"])
        self.theme_label.pack()
        self.theme_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=["System", "Light", "Dark"], command=self.change_theme, font=(FONT_MAIN, 14),
            fg_color=colors["main"], button_color=colors["main"], text_color="#ffffff", corner_radius=12, height=38
        )
        self.theme_menu.set(self.settings["theme"])
        self.theme_menu.pack(pady=(5, 20))

        self.accent_label = ctk.CTkLabel(self.settings_frame, text="Акцентный цвет:", font=(FONT_MAIN, 14), text_color=colors["text"])
        self.accent_label.pack()
        self.accent_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=list(PALETTES.keys()), command=self.change_accent, font=(FONT_MAIN, 14),
            fg_color=colors["main"], button_color=colors["main"], text_color="#ffffff", corner_radius=12, height=38
        )
        self.accent_menu.set(self.current_accent)
        self.accent_menu.pack(pady=5)

    def update_ui_colors(self):
        colors = PALETTES[self.current_accent]
        self.configure(fg_color=colors["bg"])
        self.title_label.configure(text_color=colors["text"])
        self.settings_btn.configure(text_color=colors["text"], hover_color=colors["card"])
        self.input_card.configure(fg_color=colors["card"])
        self.entry.configure(fg_color=colors["entry"], text_color=colors["text"])
        self.btn.configure(fg_color=colors["main"], hover_color=colors["text"])
        self.output_card.configure(fg_color=colors["card"])
        self.output_area.configure(text_color=colors["text"])

        self.settings_frame.configure(fg_color=colors["card"])
        self.close_btn.configure(text_color=colors["text"], hover_color=colors["bg"])
        self.settings_title.configure(text_color=colors["text"])
        self.theme_label.configure(text_color=colors["text"])
        self.accent_label.configure(text_color=colors["text"])
        self.theme_menu.configure(fg_color=colors["main"], button_color=colors["main"])
        self.accent_menu.configure(fg_color=colors["main"], button_color=colors["main"])
        self.update_idletasks()

    def change_theme(self, new_theme):
        self.settings["theme"] = new_theme
        ctk.set_appearance_mode(new_theme)
        SettingsManager.save(new_theme, self.current_accent)
        self.update_ui_colors()

    def change_accent(self, new_accent):
        self.current_accent = new_accent
        SettingsManager.save(self.settings["theme"], new_accent)
        self.update_ui_colors()

    def fetch_answers(self, event=None):
        variant_id = self.entry.get().strip()
        if not variant_id: return

        self.output_area.configure(state='normal')
        self.output_area.delete("1.0", ctk.END)
        self.output_area.insert(ctk.END, "⏳ Поиск...")
        self.update()

        try:
            r = requests.get(f"https://kompege.ru/api/variant/get/{variant_id}", timeout=10)
            data = r.json()
            tasks = sorted(data.get('tasks', []), key=lambda x: x.get('number', 0))
            
            res = f"{'№':<5} | {'Ответ'}\n{'═'*35}\n"
            for t in tasks:
                num, key = t.get('number'), str(t.get('key', ''))
                lines = key.split('\n')
                res += f"{num:<5} | {lines[0]}\n"
                for ex in lines[1:]: res += f"{'':<5} | {ex}\n"
                res += "─" * 35 + "\n"
            
            self.output_area.delete("1.0", ctk.END)
            self.output_area.insert(ctk.END, res)
        except Exception as e:
            self.output_area.insert(ctk.END, f"\n❌ Ошибка: {e}")
        finally:
            self.output_area.configure(state='disabled')

if __name__ == "__main__":
    app = App()
    app.mainloop()

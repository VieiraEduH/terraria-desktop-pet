import tkinter as tk
import win32gui
import win32con
import win32api
import win32event
import winerror
import random
import threading
import pystray
import sys
import os
import math
from PIL import Image, ImageTk, ImageOps

# --- 1. PROCESSO ÚNICO (MUTEX) ---
mutex_name = "Global\\TerrariaDesktopPet_SingleInstance_Mutex"
mutex = win32event.CreateMutex(None, False, mutex_name)
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    sys.exit(0)

def resource_path(relative_path):
    """Obtém o caminho absoluto para recursos, funcionando em dev e no PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SkinSelectorWindow:
    """Janela de Galeria Compacta"""
    def __init__(self, parent_pet):
        self.pet = parent_pet
        self.win = tk.Toplevel(self.pet.root)
        self.win.title("Seleção de Mascotes")
        self.win.geometry("640x380")
        self.win.resizable(True, True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#1A1A1A")
        
        # Centraliza a janela na tela
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = (sw - 640) // 2
        y = (sh - 380) // 2
        self.win.geometry(f"640x380+{x}+{y}")
        
        lbl_title = tk.Label(
            self.win, 
            text="Escolha o seu Mascote", 
            font=("Segoe UI", 11, "bold"), 
            bg="#1A1A1A", 
            fg="#FFFFFF",
            pady=8
        )
        lbl_title.pack()

        # Frame principal com Scrollbar ajustada
        container = tk.Frame(self.win, bg="#1A1A1A")
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        canvas = tk.Canvas(container, bg="#1A1A1A", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#1A1A1A")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.preview_images = []
        self.populate_skins()

    def populate_skins(self):
        columns = 9
        row = 0
        col = 0
        
        for skin_name, skin_info in self.pet.skins.items():
            card = tk.Frame(
                self.scrollable_frame, 
                bg="#242424", 
                bd=0, 
                relief="flat", 
                width=105, 
                height=105
            )
            card.grid(row=row, column=col, padx=4, pady=4)
            card.grid_propagate(False)

            raw_frames, _, _, _ = self.pet.process_image_frames(skin_info["file"], skin_info.get("default_facing", "left"))
            
            if raw_frames:
                img_f = raw_frames[0].resize((32, 32), Image.NEAREST)
                bg = Image.new("RGBA", img_f.size, (36, 36, 36, 255))
                comp = Image.alpha_composite(bg, img_f)
                tk_img = ImageTk.PhotoImage(comp.convert("RGB"))
                self.preview_images.append(tk_img)
                
                lbl_img = tk.Label(card, image=tk_img, bg="#242424", bd=0)
                lbl_img.pack(pady=(6, 2))

            lbl_name = tk.Label(
                card, 
                text=skin_name, 
                font=("Segoe UI", 7, "bold"), 
                bg="#242424", 
                fg="#F0F0F0",
                wraplength=95,
                justify="center"
            )
            lbl_name.pack(pady=1, fill="x")

            btn_select = tk.Button(
                card,
                text="Selecionar",
                font=("Segoe UI", 7),
                bg="#0078D4",
                fg="#FFFFFF",
                activebackground="#005A9E",
                activeforeground="#FFFFFF",
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda name=skin_name: self.select_skin(name)
            )
            btn_select.pack(side="bottom", pady=(0, 6), ipadx=6, ipady=1)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def select_skin(self, skin_name):
        self.pet.load_skin(skin_name)
        self.win.destroy()


class TerrariaDesktopPet:
    def __init__(self, target_width=40):
        # Alterado de target_height para target_width
        self.target_width = target_width
        self.transparent_color = "#000001"
        
        self.skins = {
            "Slime": {"file": "Slime_Yellow.gif", "type": "jump", "default_facing": "left"},
            "Slime Rei": {"file": "Slime_Prince.gif", "type": "jump", "default_facing": "left"},
            "Slime Princesa": {"file": "Slime_Princess.gif", "type": "jump", "default_facing": "left"},
            "Coelhinho 1": {"file": "Bunny.gif", "type": "walk", "default_facing": "left"},
            "Coelhinho 2": {"file": "Volt_Bunny.gif", "type": "walk", "default_facing": "left"},
            "Patinho 1": {"file": "Duck.gif", "type": "walk", "default_facing": "left"},
            "Patinho 2": {"file": "Duck_Walk.gif", "type": "walk", "default_facing": "left"},
            "Peixinho 1": {"file": "Goldfish_Walker.gif", "type": "walk", "default_facing": "left"},
            "Peixinho 2": {"file": "Goldfish.gif", "type": "jump", "default_facing": "left"},
            "Abelhinha": {"file": "Honey_Bee.gif", "type": "walk", "default_facing": "left"},
            "Esquilo": {"file": "Spiffo.gif", "type": "walk", "default_facing": "left"},
            "Galinha Azul": {"file": "Blue_Chicken.gif", "type": "walk", "default_facing": "left"},
            "Gatinho": {"file": "Dynamite_Kitten.gif", "type": "walk", "default_facing": "left"},
            "Psicopatinha": {"file": "Psycho.gif", "type": "walk", "default_facing": "left"},
            "Possuído": {"file": "The_Possessed.gif", "type": "walk", "default_facing": "left"},
            "Zumbi 1": {"file": "Zombie.gif", "type": "walk", "default_facing": "left"},
            "Zumbi 2": {"file": "Maggot_Zombie.gif", "type": "walk", "default_facing": "left"},
            "Junino": {"file": "Junimo.gif", "type": "walk", "default_facing": "left"},
        }
        self.current_skin_name = "Slime Rei"
        
        self.root = tk.Tk()
        self.root.title("Terraria Desktop Pet")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=self.transparent_color)
        self.root.attributes("-transparentcolor", self.transparent_color)
        
        self.is_visible = True
        self.pet_mode = 0 
        self.tray_icon = None
        self.selector_window = None
        self.setup_positions()
        
        self.label = tk.Label(self.root, bg=self.transparent_color, bd=0)
        self.label.pack(fill="both", expand=True)
        
        self.hwnd = None
        self.root.after(100, self.make_click_through)
        
        self.vx = 0.0
        self.vy = 0.0
        self.gravity = 1.2
        self.is_jumping = False
        self.direction = 1
        self.squish_timer = 0
        self.walk_step = 0
        self.celebrate_timer = 0
        
        self.frame_index = 0
        self.anim_counter = 0
        self.anim_delay = 3
        
        self.load_skin(self.current_skin_name)
        self.animate()

    def setup_positions(self):
        self.vx_start = win32api.GetSystemMetrics(76)
        self.vy_start = win32api.GetSystemMetrics(77)
        self.vscreen_w = win32api.GetSystemMetrics(78)
        self.vscreen_h = win32api.GetSystemMetrics(79)
        self.vx_end = self.vx_start + self.vscreen_w
        
        try:
            work_area = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))['Work']
            self.work_bottom = work_area[3]
            work_right = work_area[2]
        except Exception:
            self.work_bottom = win32api.GetSystemMetrics(1) - 48
            work_right = win32api.GetSystemMetrics(0)

        self.clock_x = float(work_right - self.target_width - 20)
        self.x = float(random.randint(100, 500))
        self.y_ground = float(self.work_bottom - getattr(self, 'base_height', 40))
        self.y = float(self.y_ground)

    def process_image_frames(self, filename, default_facing="left"):
        img_path = resource_path(filename)
        
        if not os.path.exists(img_path):
            base_name = os.path.splitext(filename)[0]
            for ext in [".gif", ".webp", ".png"]:
                alt_path = resource_path(base_name + ext)
                if os.path.exists(alt_path):
                    img_path = alt_path
                    break

        if not os.path.exists(img_path):
            return None, 40, 40, default_facing

        try:
            img = Image.open(img_path)
            orig_w, orig_h = img.size
            
            # Ajuste baseado na largura máxima fixa:
            new_w = self.target_width
            new_h = int(orig_h * (new_w / orig_w))
            
            raw_frames = []
            if getattr(img, "is_animated", False):
                for i in range(img.n_frames):
                    img.seek(i)
                    frame = img.convert("RGBA")
                    r, g, b, alpha = frame.split()
                    alpha = alpha.point(lambda p: 255 if p > 128 else 0)
                    frame.putalpha(alpha)
                    raw_frames.append(frame)
            else:
                frame = img.convert("RGBA")
                r, g, b, alpha = frame.split()
                alpha = alpha.point(lambda p: 255 if p > 128 else 0)
                frame.putalpha(alpha)
                raw_frames.append(frame)

            return raw_frames, new_w, new_h, default_facing
        except Exception as e:
            print(f"Erro ao carregar '{filename}': {e}")
            return None, 40, 40, default_facing

    def load_skin(self, skin_name):
        skin_info = self.skins.get(skin_name, self.skins["Slime Rei"])
        filename = skin_info["file"]
        self.movement_type = skin_info["type"]
        default_facing = skin_info.get("default_facing", "left")
        
        self.frame_index = 0
        self.anim_counter = 0
        self.is_jumping = False
        self.celebrate_timer = 0
        self.squish_timer = 0
        self.vy = 0
        self.vx = 0
        
        raw_frames, new_w, new_h, facing = self.process_image_frames(filename, default_facing)
        self.base_width = new_w
        self.base_height = new_h
        self.y_ground = float(self.work_bottom - self.base_height)

        self.idle_sprites = None

        if self.movement_type == "walk" and "idle_file" in skin_info:
            idle_frames, idle_w, idle_h, _ = self.process_image_frames(skin_info["idle_file"], default_facing)
            if idle_frames:
                self.idle_sprites = {1: [], -1: []}
                for f in idle_frames:
                    base_resized = f.resize((idle_w, idle_h), Image.NEAREST)
                    if facing == "left":
                        left_img = base_resized
                        right_img = ImageOps.mirror(base_resized)
                    else:
                        right_img = base_resized
                        left_img = ImageOps.mirror(base_resized)
                    
                    self.idle_sprites[-1].append(self.pil_to_tk(left_img))
                    self.idle_sprites[1].append(self.pil_to_tk(right_img))

        self.sprites = {
            ("normal", 1): [], ("normal", -1): [],
            ("stretch", 1): [], ("stretch", -1): [],
            ("squash", 1): [], ("squash", -1): []
        }

        if raw_frames:
            for f in raw_frames:
                base_norm = f.resize((self.base_width, self.base_height), Image.NEAREST)
                
                if facing == "left":
                    left_norm = base_norm
                    right_norm = ImageOps.mirror(base_norm)
                else:
                    right_norm = base_norm
                    left_norm = ImageOps.mirror(base_norm)
                
                left_stretch = left_norm.resize((int(self.base_width * 0.85), int(self.base_height * 1.2)), Image.NEAREST)
                right_stretch = right_norm.resize((int(self.base_width * 0.85), int(self.base_height * 1.2)), Image.NEAREST)
                
                left_squash = left_norm.resize((int(self.base_width * 1.2), int(self.base_height * 0.8)), Image.NEAREST)
                right_squash = right_norm.resize((int(self.base_width * 1.2), int(self.base_height * 0.8)), Image.NEAREST)
                
                self.sprites[("normal", 1)].append(self.pil_to_tk(right_norm))
                self.sprites[("normal", -1)].append(self.pil_to_tk(left_norm))
                self.sprites[("stretch", 1)].append(self.pil_to_tk(right_stretch))
                self.sprites[("stretch", -1)].append(self.pil_to_tk(left_stretch))
                self.sprites[("squash", 1)].append(self.pil_to_tk(right_squash))
                self.sprites[("squash", -1)].append(self.pil_to_tk(left_squash))

        self.win_w = int(self.base_width * 1.6)
        self.win_h = int(self.base_height * 1.6)
        self.root.geometry(f"{self.win_w}x{self.win_h}+{int(self.x)}+{int(self.y)}")
        self.current_skin_name = skin_name
        return True

    def switch_random_skin(self):
        """Sorteia um novo modelo diferente do atual"""
        available_skins = [name for name in self.skins.keys() if name != self.current_skin_name]
        if available_skins:
            next_skin = random.choice(available_skins)
            self.load_skin(next_skin)

    def pil_to_tk(self, img):
        bg = Image.new("RGBA", img.size, self.transparent_color)
        composite = Image.alpha_composite(bg, img)
        return ImageTk.PhotoImage(composite.convert("RGB"))

    def make_click_through(self):
        try:
            hwnd = win32gui.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()
            self.hwnd = hwnd
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_styles = styles | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_styles)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        except Exception:
            pass

    def toggle_visibility(self):
        if self.is_visible:
            self.root.withdraw()
            self.is_visible = False
        else:
            self.root.deiconify()
            self.make_click_through()
            self.is_visible = True
        
        if self.tray_icon:
            self.tray_icon.update_menu()

    def set_mode(self, mode_index):
        """Define o modo: 0=Seguir, 1=Parado, 2=Andar, 3=Randômico"""
        self.pet_mode = mode_index
        self.is_jumping = False
        self.vy = 0
        self.vx = 0
        if self.pet_mode == 1:
            self.x = self.clock_x
            self.y = self.y_ground

    def open_skin_selector(self):
        if self.selector_window is not None and self.selector_window.win.winfo_exists():
            self.selector_window.win.lift()
            self.selector_window.win.focus_force()
        else:
            self.selector_window = SkinSelectorWindow(self)

    def reload_pet(self):
        try:
            self.setup_positions()
            self.make_click_through()
            self.is_jumping = False
            self.celebrate_timer = 0
            self.vy = 0
            self.vx = 0
            if self.pet_mode == 1:
                self.x = self.clock_x
                self.y = self.y_ground
        except Exception:
            pass

    def animate(self):
        if hasattr(self, 'sprites') and self.is_visible:
            try:
                state = "normal"
                active_frame_list = None

                # MODO 1: PARADO (NO RELÓGIO)
                if self.pet_mode == 1:
                    self.x = self.clock_x
                    self.y = self.y_ground
                    self.direction = -1
                    active_frame_list = self.sprites.get(("normal", self.direction))

                # MODOS DE MOVIMENTO: 0 (SEGUIR), 2 (ANDAR) E 3 (RANDÔMICO)
                else:
                    reached_target = False

                    if self.pet_mode == 0:  # Seguir Mouse
                        mouse_x, _ = win32api.GetCursorPos()
                        pet_center_x = self.x + self.base_width / 2
                        dx = mouse_x - pet_center_x
                        reached_target = abs(dx) <= 20
                    else:  # Modos Andar (2) e Randômico (3)
                        dx = self.direction
                        reached_target = False

                    # Comemoração ao alcançar o mouse (no modo Seguir)
                    if self.pet_mode == 0 and reached_target and not self.is_jumping and self.squish_timer == 0:
                        if random.random() < 0.08:
                            self.celebrate_timer = 3

                    if self.celebrate_timer > 0 and not self.is_jumping:
                        self.is_jumping = True
                        self.vy = random.uniform(-9, -6)
                        self.vx = random.uniform(-1.5, 1.5)
                        self.celebrate_timer -= 1

                    # FISICA: TIPO PULO
                    if self.movement_type == "jump":
                        if not self.is_jumping and self.squish_timer == 0:
                            chance = 0.035 if self.pet_mode == 0 else 0.025
                            if random.random() < chance:
                                self.is_jumping = True
                                self.vy = random.uniform(-14, -10)
                                
                                if self.pet_mode == 0:
                                    if abs(dx) > 15:
                                        speed = random.uniform(3.5, 6.0)
                                        self.vx = speed if dx > 0 else -speed
                                        self.direction = 1 if dx > 0 else -1
                                    else:
                                        self.vx = 0.0
                                else:
                                    speed = random.uniform(3.5, 5.5)
                                    self.vx = speed * self.direction

                        if self.is_jumping:
                            self.y += self.vy
                            self.vy += self.gravity
                            self.x += self.vx
                            state = "stretch"
                            
                            if self.x <= self.vx_start:
                                self.x = float(self.vx_start)
                                self.vx *= -1
                                self.direction = 1
                                if self.pet_mode == 3:
                                    self.switch_random_skin()
                            elif self.x >= self.vx_end - self.base_width:
                                self.x = float(self.vx_end - self.base_width)
                                self.vx *= -1
                                self.direction = -1
                                if self.pet_mode == 3:
                                    self.switch_random_skin()
                            
                            if self.y >= self.y_ground:
                                self.y = self.y_ground
                                self.is_jumping = False
                                self.vy = 0
                                self.vx = 0
                                self.squish_timer = 2

                        elif self.squish_timer > 0:
                            state = "squash"
                            self.squish_timer -= 1

                        active_frame_list = self.sprites.get((state, self.direction), self.sprites[("normal", self.direction)])

                    # FISICA: TIPO CAMINHADA
                    elif self.movement_type == "walk":
                        if self.is_jumping:
                            self.y += self.vy
                            self.vy += self.gravity
                            self.x += self.vx
                            state = "stretch"

                            if self.y >= self.y_ground:
                                self.y = self.y_ground
                                self.is_jumping = False
                                self.vy = 0
                                self.vx = 0
                                self.squish_timer = 2

                            active_frame_list = self.sprites.get((state, self.direction), self.sprites[("normal", self.direction)])

                        elif self.squish_timer > 0:
                            state = "squash"
                            self.squish_timer -= 1
                            active_frame_list = self.sprites.get((state, self.direction), self.sprites[("normal", self.direction)])

                        elif not reached_target:
                            speed = 2.5
                            if self.pet_mode == 0:
                                self.direction = 1 if dx > 0 else -1
                            
                            self.x += speed * self.direction
                            self.walk_step += 0.3
                            bounce = math.sin(self.walk_step) * 2
                            self.y = self.y_ground + bounce
                            active_frame_list = self.sprites.get(("normal", self.direction))
                        else:
                            self.y = self.y_ground
                            self.walk_step = 0
                            if self.idle_sprites:
                                active_frame_list = self.idle_sprites[self.direction]
                            else:
                                active_frame_list = self.sprites.get(("normal", self.direction))

                    # INVERSÃO AUTOMÁTICA E TROCA DE MODELO NAS BORDAS DA TELA
                    if self.x <= self.vx_start:
                        self.x = float(self.vx_start)
                        self.direction = 1
                        if self.pet_mode == 3:
                            self.switch_random_skin()
                    elif self.x >= self.vx_end - self.base_width:
                        self.x = float(self.vx_end - self.base_width)
                        self.direction = -1
                        if self.pet_mode == 3:
                            self.switch_random_skin()

                if active_frame_list:
                    self.anim_counter += 1
                    if self.anim_counter >= self.anim_delay:
                        self.frame_index = (self.frame_index + 1) % len(active_frame_list)
                        self.anim_counter = 0
                    
                    render_img = active_frame_list[self.frame_index % len(active_frame_list)]
                    self.label.config(image=render_img)

                self.root.geometry(f"{self.win_w}x{self.win_h}+{int(self.x)}+{int(self.y)}")
                
                if self.hwnd:
                    win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

            except Exception:
                pass

        self.root.after(40, self.animate)

# --- MENU DA BANDEJA ---
def create_tray_icon(pet):
    icon_image = Image.new('RGB', (64, 64), color=(0, 162, 232))
    
    def get_toggle_label(item):
        return "Ocultar" if pet.is_visible else "Mostrar"

    def on_toggle_visible(icon, item):
        pet.root.after(0, pet.toggle_visibility)

    def set_mode(mode_index):
        return lambda icon, item: pet.root.after(0, lambda: pet.set_mode(mode_index))

    def on_open_gallery(icon, item):
        pet.root.after(0, pet.open_skin_selector)

    def on_reload(icon, item):
        pet.root.after(0, pet.reload_pet)

    def on_quit(icon, item):
        icon.stop()
        if hasattr(pet, 'root') and pet.root:
            pet.root.quit()

    mode_menu = pystray.Menu(
        pystray.MenuItem("Andar", set_mode(2)),
        pystray.MenuItem("Seguir", set_mode(0)),
        pystray.MenuItem("Parado", set_mode(1)),
        pystray.MenuItem("Randômico", set_mode(3))
    )

    menu = pystray.Menu(
        pystray.MenuItem(get_toggle_label, on_toggle_visible),
        pystray.MenuItem("Modo", mode_menu),
        pystray.MenuItem("Trocar Modelo...", on_open_gallery),
        pystray.MenuItem("Recarregar Pet", on_reload),
        pystray.MenuItem("Fechar Pet", on_quit)
    )
    
    icon = pystray.Icon("TerrariaPet", icon_image, "Terraria Desktop Pet", menu)
    pet.tray_icon = icon
    icon.run()

if __name__ == "__main__":
    app = TerrariaDesktopPet(target_width=40)
    if hasattr(app, 'root') and app.root.winfo_exists():
        tray_thread = threading.Thread(target=create_tray_icon, args=(app,), daemon=True)
        tray_thread.start()
        app.root.mainloop()
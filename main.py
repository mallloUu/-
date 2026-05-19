"""
main.py — Кулинарная книга
Python + CustomTkinter + SQLite
Дизайн: тёплая кухонная палитра (терракота, оливковый, сливочный)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk, Menu
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
import database as db

# ─── Тема ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BG        = "#FAF6F0"
SIDEBAR   = "#2D3B2D"
CARD      = "#FFFFFF"
ACCENT    = "#C0392B"
ACCENT2   = "#E8845A"
OLIVE     = "#4A5E3A"
OLIVE_LT  = "#7A9960"
CREAM     = "#FFF8EE"
GOLD      = "#F5A623"
TEXT      = "#1A1A1A"
TEXT_SEC  = "#6B6B6B"
BORDER    = "#E2D9CE"

CATEGORIES = ["Супы", "Выпечка", "Десерты", "Основные блюда", "Салаты"]


# ════════════════════════════════════════════════════════════════════════════
# Экран входа / регистрации
# ════════════════════════════════════════════════════════════════════════════

class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Кулинарная книга — Вход")
        self.geometry("420x560")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self._user = None
        self._mode = "login"
        self._build()

    def _build(self):
        # Шапка
        top = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=0, height=140)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="🍳", font=("Segoe UI Emoji", 46)).pack(pady=(22, 4))
        ctk.CTkLabel(top, text="Кулинарная книга",
                     font=("Georgia", 18, "bold"), text_color="#F5ECD7").pack()

        # Карточка
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(padx=36, pady=28, fill="x")

        self.lbl_header = ctk.CTkLabel(
            card, text="Вход в систему",
            font=("Georgia", 16, "bold"), text_color=OLIVE)
        self.lbl_header.pack(pady=(22, 16))

        def field(ph, show=None):
            e = ctk.CTkEntry(card, placeholder_text=ph,
                             font=("Segoe UI", 13), height=42,
                             fg_color=CREAM, border_color=BORDER,
                             border_width=1, text_color=TEXT,
                             corner_radius=8, show=show or "")
            e.pack(padx=22, pady=(0, 10), fill="x")
            return e

        self.e_login = field("Логин")
        self.e_pass  = field("Пароль", show="●")

        self.btn_main = ctk.CTkButton(
            card, text="Войти",
            font=("Segoe UI", 14, "bold"), height=44, corner_radius=10,
            fg_color=ACCENT, hover_color="#A93226",
            command=self._on_main
        )
        self.btn_main.pack(padx=22, pady=(4, 8), fill="x")

        self.btn_switch = ctk.CTkButton(
            card, text="Нет аккаунта? Зарегистрироваться",
            font=("Segoe UI", 12), height=36, corner_radius=8,
            fg_color="transparent", border_width=1,
            border_color=BORDER, hover_color=CREAM,
            text_color=OLIVE_LT,
            command=self._switch
        )
        self.btn_switch.pack(padx=22, pady=(0, 22), fill="x")

        self.e_login.bind("<Return>", lambda e: self.e_pass.focus())
        self.e_pass.bind("<Return>",  lambda e: self._on_main())

    def _switch(self):
        if self._mode == "login":
            self._mode = "register"
            self.lbl_header.configure(text="Регистрация")
            self.btn_main.configure(text="Создать аккаунт")
            self.btn_switch.configure(text="Уже есть аккаунт? Войти")
        else:
            self._mode = "login"
            self.lbl_header.configure(text="Вход в систему")
            self.btn_main.configure(text="Войти")
            self.btn_switch.configure(text="Нет аккаунта? Зарегистрироваться")

    def _on_main(self):
        login = self.e_login.get().strip()
        pwd   = self.e_pass.get().strip()
        if not login or not pwd:
            messagebox.showwarning("Ошибка", "Заполните логин и пароль.")
            return
        if self._mode == "login":
            user = db.authenticate(login, pwd)
            if user:
                self._user = user
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль.")
        else:
            if db.register_user(login, pwd):
                messagebox.showinfo("Готово", "Аккаунт создан! Теперь войдите.")
                self._switch()
                self.e_login.delete(0, "end")
                self.e_pass.delete(0, "end")
            else:
                messagebox.showerror("Ошибка", "Логин уже занят.")

    def get_user(self):
        return self._user


# ════════════════════════════════════════════════════════════════════════════
# Главное окно
# ════════════════════════════════════════════════════════════════════════════

class CookbookApp(ctk.CTk):
    def __init__(self, user: dict):
        super().__init__()
        self.user     = user
        self._edit_id = None
        self._active_tab = "add"

        self.title("Кулинарная книга")
        self.geometry("1180x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        self._style_tree()
        self._build_menu()
        self._build_ui()
        self._switch_tab("all")

        self.bind("<Control-n>", lambda e: self._switch_tab("add"))
        self.bind("<Control-f>", lambda e: self._toggle_fav_shortcut())

    # ── Treeview style ───────────────────────────────────────────────────────
    def _style_tree(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Cook.Treeview",
            background=CARD, fieldbackground=CARD,
            foreground=TEXT, rowheight=36,
            font=("Segoe UI", 12), borderwidth=0)
        s.configure("Cook.Treeview.Heading",
            background=CREAM, foreground=OLIVE,
            font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0)
        s.map("Cook.Treeview",
              background=[("selected", ACCENT2)],
              foreground=[("selected", "#fff")])
        s.layout("Cook.Treeview",
                 [("Cook.Treeview.treearea", {"sticky": "nswe"})])

        # Для таблицы пользователей (админ)
        s.configure("Admin.Treeview",
            background=CARD, fieldbackground=CARD,
            foreground=TEXT, rowheight=32,
            font=("Segoe UI", 12), borderwidth=0)
        s.configure("Admin.Treeview.Heading",
            background=CREAM, foreground=OLIVE,
            font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0)
        s.map("Admin.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#fff")])

    # ── Меню ────────────────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = Menu(self, bg=SIDEBAR, fg="#FFFFFF",
                       activebackground=ACCENT2, activeforeground="#fff",
                       relief="flat", bd=0, font=("Segoe UI", 11))

        mf = Menu(menubar, tearoff=0, bg=CARD, fg=TEXT,
                  activebackground=ACCENT2, activeforeground="#fff",
                  font=("Segoe UI", 11))
        mf.add_command(label="Новый рецепт  Ctrl+N", command=lambda: self._switch_tab("add"))
        mf.add_command(label="Удалить выбранный",    command=self._delete_recipe)
        mf.add_command(label="Экспорт в TXT",         command=self._export_txt)
        mf.add_separator()
        mf.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="  Файл  ", menu=mf)

        ms = Menu(menubar, tearoff=0, bg=CARD, fg=TEXT,
                  activebackground=ACCENT2, activeforeground="#fff",
                  font=("Segoe UI", 11))
        ms.add_command(label="По ингредиенту…", command=self._search_ingredient_dialog)
        ms.add_command(label="По категории…",   command=self._search_category_dialog)
        menubar.add_cascade(label="  Поиск  ", menu=ms)

        mfav = Menu(menubar, tearoff=0, bg=CARD, fg=TEXT,
                    activebackground=GOLD, activeforeground="#fff",
                    font=("Segoe UI", 11))
        mfav.add_command(label="Показать только избранные", command=lambda: self._switch_tab("fav"))
        menubar.add_cascade(label="  Избранное  ", menu=mfav)

        if self.user["is_admin"]:
            ma = Menu(menubar, tearoff=0, bg=CARD, fg=TEXT,
                      activebackground=ACCENT, activeforeground="#fff",
                      font=("Segoe UI", 11))
            ma.add_command(label="Управление пользователями", command=self._open_admin)
            menubar.add_cascade(label="  Администратор  ", menu=ma)

        mh = Menu(menubar, tearoff=0, bg=CARD, fg=TEXT,
                  activebackground=ACCENT2, activeforeground="#fff",
                  font=("Segoe UI", 11))
        mh.add_command(label="О программе", command=self._about)
        menubar.add_cascade(label="  Справка  ", menu=mh)

        self.configure(menu=menubar)

    # ── Основной UI ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # Сайдбар
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(padx=20, pady=(30, 10))
        ctk.CTkLabel(logo, text="🍳", font=("Segoe UI Emoji", 44)).pack()
        ctk.CTkLabel(logo, text="Кулинарная\nкнига",
                     font=("Georgia", 17, "bold"), text_color="#F5ECD7",
                     justify="center").pack(pady=(4, 0))

        # Пользователь
        role_text = "👑 Администратор" if self.user["is_admin"] else f"👤 {self.user['login']}"
        ctk.CTkLabel(self.sidebar, text=role_text,
                     font=("Segoe UI", 11), text_color=OLIVE_LT).pack(pady=(6, 0))

        ctk.CTkFrame(self.sidebar, fg_color="#3D5C3D", height=1).pack(
            fill="x", padx=20, pady=20)

        # Навигация
        self._nav_btns = {}
        nav_items = [
            ("add", "✏️   Добавить рецепт"),
            ("all", "📖   Все рецепты"),
            ("fav", "⭐   Избранное"),
        ]
        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                font=("Segoe UI", 13), height=44, corner_radius=10,
                fg_color="transparent", hover_color="#3D5C3D",
                text_color="#D4C9B8",
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(padx=12, pady=3, fill="x")
            self._nav_btns[key] = btn

        self.lbl_count = ctk.CTkLabel(
            self.sidebar, text="", font=("Segoe UI", 11), text_color="#8A9E8A")
        self.lbl_count.pack(padx=20, pady=(20, 0), anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="Ctrl+N  новый рецепт\nCtrl+F  избранное",
            font=("Segoe UI", 10), text_color="#4D6B4D", justify="left"
        ).pack(padx=20, pady=(8, 0), anchor="w")

        # Правая область
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self.frames = {}
        self.frames["add"] = self._build_add_tab()
        self.frames["all"] = self._build_list_tab("all")
        self.frames["fav"] = self._build_list_tab("fav")

    def _nav_activate(self, key):
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color=OLIVE if k == key else "transparent",
                text_color="#FFFFFF" if k == key else "#D4C9B8"
            )

    def _switch_tab(self, key):
        for f in self.frames.values():
            f.pack_forget()
        self._active_tab = key
        self.frames[key].pack(fill="both", expand=True)
        self._nav_activate(key)
        if key in ("all", "fav"):
            self._refresh_list(key)
        if key == "add" and self._edit_id is None:
            self._clear_form()

    # ════════════════════════════════════════════════════════════════════════
    # Вкладка «Добавить рецепт»
    # ════════════════════════════════════════════════════════════════════════
    def _build_add_tab(self):
        outer = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)

        hdr = ctk.CTkFrame(outer, fg_color=CREAM, corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        self.lbl_form_title = ctk.CTkLabel(
            hdr, text="✏️  Новый рецепт",
            font=("Georgia", 18, "bold"), text_color=OLIVE)
        self.lbl_form_title.pack(side="left", padx=28, pady=14)

        scroll = ctk.CTkScrollableFrame(outer, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(padx=32, pady=24, fill="x")

        def lbl(text):
            ctk.CTkLabel(card, text=text, font=("Segoe UI", 12, "bold"),
                         text_color=OLIVE, anchor="w").pack(
                padx=20, pady=(14, 4), anchor="w")

        # Строка: название + категория + время
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(padx=20, pady=(14, 0), fill="x")
        row1.columnconfigure(0, weight=3)
        row1.columnconfigure(1, weight=2)
        row1.columnconfigure(2, weight=1)

        for col_i, text in enumerate(["Название рецепта *", "Категория", "Время (мин)"]):
            ctk.CTkLabel(row1, text=text, font=("Segoe UI", 12, "bold"),
                         text_color=OLIVE, anchor="w").grid(
                row=0, column=col_i, sticky="w", padx=(0, 10) if col_i < 2 else (0, 0))

        self.e_title = ctk.CTkEntry(row1, placeholder_text="Борщ украинский",
                                    font=("Segoe UI", 13), height=40,
                                    fg_color=CREAM, border_color=BORDER,
                                    border_width=1, text_color=TEXT, corner_radius=8)
        self.e_title.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))

        self.cb_cat = ctk.CTkComboBox(row1, values=CATEGORIES,
                                      font=("Segoe UI", 13), height=40,
                                      fg_color=CREAM, border_color=BORDER,
                                      border_width=1, text_color=TEXT,
                                      button_color=OLIVE_LT, button_hover_color=OLIVE,
                                      dropdown_fg_color=CARD, dropdown_text_color=TEXT,
                                      corner_radius=8)
        self.cb_cat.set(CATEGORIES[0])
        self.cb_cat.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(4, 0))

        self.sp_time = ctk.CTkEntry(row1, placeholder_text="30",
                                    font=("Segoe UI", 13), height=40,
                                    fg_color=CREAM, border_color=BORDER,
                                    border_width=1, text_color=TEXT,
                                    corner_radius=8, width=90)
        self.sp_time.grid(row=1, column=2, sticky="ew", pady=(4, 0))

        lbl("Ингредиенты (каждый с новой строки)")
        self.t_ingr = ctk.CTkTextbox(card, height=110, font=("Segoe UI", 12),
                                     fg_color=CREAM, border_color=BORDER,
                                     border_width=1, text_color=TEXT,
                                     corner_radius=8)
        self.t_ingr.pack(padx=20, fill="x")

        lbl("Инструкции (пошагово)")
        self.t_inst = ctk.CTkTextbox(card, height=140, font=("Segoe UI", 12),
                                     fg_color=CREAM, border_color=BORDER,
                                     border_width=1, text_color=TEXT,
                                     corner_radius=8)
        self.t_inst.pack(padx=20, fill="x")

        fav_row = ctk.CTkFrame(card, fg_color="transparent")
        fav_row.pack(padx=20, pady=(12, 0), anchor="w")
        self.var_fav = ctk.IntVar(value=0)
        ctk.CTkCheckBox(fav_row, text="⭐  Добавить в избранное",
                        variable=self.var_fav,
                        font=("Segoe UI", 13), text_color=TEXT,
                        fg_color=GOLD, hover_color="#D4911D",
                        border_color=BORDER, checkmark_color="white",
                        corner_radius=6).pack()

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(padx=20, pady=(16, 20), fill="x")

        self.btn_save = ctk.CTkButton(
            btn_row, text="💾  Сохранить рецепт",
            font=("Segoe UI", 14, "bold"), height=46, corner_radius=12,
            fg_color=ACCENT, hover_color="#A93226",
            command=self._save_recipe)
        self.btn_save.pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="✕  Очистить",
            font=("Segoe UI", 13), height=46, corner_radius=12,
            fg_color="transparent", border_width=1,
            border_color=BORDER, hover_color=CREAM,
            text_color=TEXT_SEC, command=self._clear_form
        ).pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(card, text="* обязательное поле",
                     font=("Segoe UI", 10), text_color="#B0A090").pack(
            padx=20, pady=(0, 16), anchor="w")

        return outer

    # ════════════════════════════════════════════════════════════════════════
    # Вкладки списков
    # ════════════════════════════════════════════════════════════════════════
    def _build_list_tab(self, key):
        outer = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)

        title_text = "📖  Все рецепты" if key == "all" else "⭐  Избранное"
        hdr = ctk.CTkFrame(outer, fg_color=CREAM, corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=title_text,
                     font=("Georgia", 18, "bold"), text_color=OLIVE).pack(
            side="left", padx=28, pady=14)

        btn_bar = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_bar.pack(side="right", padx=16)
        ctk.CTkButton(btn_bar, text="🗑  Удалить", width=110, height=34,
                      corner_radius=8, font=("Segoe UI", 12),
                      fg_color=ACCENT, hover_color="#A93226",
                      command=self._delete_recipe).pack(side="left", padx=4)
        ctk.CTkButton(btn_bar, text="✏️  Изменить", width=110, height=34,
                      corner_radius=8, font=("Segoe UI", 12),
                      fg_color=OLIVE, hover_color="#3A4D2A",
                      command=lambda: self._edit_selected(key)).pack(side="left", padx=4)

        tree_wrap = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=14,
                                  border_width=1, border_color=BORDER)
        tree_wrap.pack(padx=24, pady=20, fill="both", expand=True)

        cols = ("id", "title", "category", "cook_time", "fav")
        tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                             style="Cook.Treeview", selectmode="browse")
        for col, hd, w, stretch in [
            ("id",        "ID",          50,  False),
            ("title",     "Название",    300, True),
            ("category",  "Категория",   140, False),
            ("cook_time", "Время (мин)", 100, False),
            ("fav",       "Избранное",    90, False),
        ]:
            tree.heading(col, text=hd, command=lambda c=col, t=tree: self._sort_tree(t, c))
            tree.column(col, width=w, stretch=stretch, anchor="w")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        tree.bind("<Double-1>", lambda e, t=tree: self._view_recipe(t))

        if key == "all":
            self.tree_all = tree
        else:
            self.tree_fav = tree

        return outer

    # ════════════════════════════════════════════════════════════════════════
    # Логика
    # ════════════════════════════════════════════════════════════════════════
    def _uid(self):
        # Админ видит все рецепты; обычный — только свои
        return None if self.user["is_admin"] else self.user["id"]

    def _clear_form(self):
        self._edit_id = None
        self.lbl_form_title.configure(text="✏️  Новый рецепт")
        self.btn_save.configure(text="💾  Сохранить рецепт")
        self.e_title.delete(0, "end")
        self.sp_time.delete(0, "end")
        self.t_ingr.delete("1.0", "end")
        self.t_inst.delete("1.0", "end")
        self.cb_cat.set(CATEGORIES[0])
        self.var_fav.set(0)

    def _save_recipe(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Название рецепта обязательно.")
            return
        try:
            cook_time = int(self.sp_time.get().strip() or 0)
            if not (5 <= cook_time <= 600):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Время приготовления: от 5 до 600 минут.")
            return

        cat    = self.cb_cat.get()
        ingr   = self.t_ingr.get("1.0", "end").strip()
        inst   = self.t_inst.get("1.0", "end").strip()
        is_fav = self.var_fav.get()

        if self._edit_id:
            db.update_recipe(self._edit_id, title, cat, cook_time, ingr, inst, is_fav)
            messagebox.showinfo("Готово", "Рецепт обновлён!")
        else:
            db.add_recipe(self.user["id"], title, cat, cook_time, ingr, inst, is_fav)
            messagebox.showinfo("Готово", "Рецепт сохранён!")

        self._clear_form()
        self._refresh_counts()

    def _refresh_list(self, key, recipes=None):
        tree = self.tree_all if key == "all" else self.tree_fav
        tree.delete(*tree.get_children())
        if recipes is None:
            recipes = db.get_all_recipes(self._uid()) if key == "all" \
                      else db.get_favorites(self._uid())
        for r in recipes:
            fav = "⭐" if r["is_favorite"] else ""
            tree.insert("", "end", iid=str(r["id"]),
                        values=(r["id"], r["title"], r["category"], r["cook_time"], fav))
        self._refresh_counts()

    def _refresh_counts(self):
        uid = self._uid()
        self.lbl_count.configure(
            text=f"Рецептов: {len(db.get_all_recipes(uid))}\n"
                 f"Избранных: {len(db.get_favorites(uid))}"
        )

    def _get_selected_id(self):
        tree = self.tree_all if self._active_tab == "all" else self.tree_fav
        sel = tree.selection()
        return int(sel[0]) if sel else None

    def _delete_recipe(self):
        rid = self._get_selected_id()
        if not rid:
            messagebox.showwarning("Ошибка", "Выберите рецепт.")
            return
        if not messagebox.askyesno("Удаление", "Удалить рецепт?"):
            return
        db.delete_recipe(rid)
        self._refresh_list(self._active_tab)

    def _edit_selected(self, key):
        tree = self.tree_all if key == "all" else self.tree_fav
        sel = tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        r = next((x for x in db.get_all_recipes() if x["id"] == rid), None)
        if not r:
            return
        self._switch_tab("add")
        self._edit_id = rid
        self.lbl_form_title.configure(text=f"✏️  Редактировать: {r['title']}")
        self.btn_save.configure(text="💾  Обновить рецепт")
        self.e_title.delete(0, "end");  self.e_title.insert(0, r["title"])
        self.cb_cat.set(r["category"])
        self.sp_time.delete(0, "end"); self.sp_time.insert(0, str(r["cook_time"]))
        self.t_ingr.delete("1.0", "end"); self.t_ingr.insert("1.0", r["ingredients"])
        self.t_inst.delete("1.0", "end"); self.t_inst.insert("1.0", r["instructions"])
        self.var_fav.set(r["is_favorite"])

    def _sort_tree(self, tree, col):
        items = [(tree.set(k, col), k) for k in tree.get_children("")]
        items.sort(key=lambda x: str(x[0]).lower())
        for i, (_, k) in enumerate(items):
            tree.move(k, "", i)

    def _view_recipe(self, tree):
        sel = tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        r = next((x for x in db.get_all_recipes() if x["id"] == rid), None)
        if r:
            RecipeViewer(self, r)

    def _search_ingredient_dialog(self):
        dlg = ctk.CTkInputDialog(text="Введите ингредиент для поиска:", title="Поиск по ингредиенту")
        q = dlg.get_input()
        if q and q.strip():
            results = db.search_by_ingredient(q.strip(), self._uid())
            self._switch_tab("all")
            self._refresh_list("all", results)

    def _search_category_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Поиск по категории")
        win.geometry("300x220")
        win.configure(fg_color=BG)
        win.grab_set()
        ctk.CTkLabel(win, text="Выберите категорию:",
                     font=("Segoe UI", 13, "bold"), text_color=OLIVE).pack(pady=(20, 10))
        cb = ctk.CTkComboBox(win, values=CATEGORIES, font=("Segoe UI", 13),
                             fg_color=CREAM, border_color=BORDER,
                             button_color=OLIVE_LT, button_hover_color=OLIVE,
                             dropdown_fg_color=CARD, dropdown_text_color=TEXT,
                             height=40, corner_radius=8)
        cb.set(CATEGORIES[0])
        cb.pack(padx=30, fill="x")

        def do_search():
            results = db.search_by_category(cb.get(), self._uid())
            win.destroy()
            self._switch_tab("all")
            self._refresh_list("all", results)

        ctk.CTkButton(win, text="Найти", font=("Segoe UI", 13, "bold"),
                      height=40, corner_radius=10,
                      fg_color=ACCENT, hover_color="#A93226",
                      command=do_search).pack(padx=30, pady=20, fill="x")

    def _export_txt(self):
        tree = self.tree_all if self._active_tab == "all" else self.tree_fav
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Ошибка", "Выберите рецепт для экспорта.")
            return
        rid = int(sel[0])
        r = next((x for x in db.get_all_recipes() if x["id"] == rid), None)
        if not r:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")],
            title="Экспорт рецепта", initialfile=r["title"])
        if not path:
            return
        sep = "═" * 50
        content = (
            f"{sep}\n  {r['title'].upper()}\n{sep}\n\n"
            f"Категория : {r['category']}\n"
            f"Время     : {r['cook_time']} мин\n"
            f"Избранное : {'Да ⭐' if r['is_favorite'] else 'Нет'}\n\n"
            f"{'─'*50}\nИНГРЕДИЕНТЫ:\n{'─'*50}\n{r['ingredients']}\n\n"
            f"{'─'*50}\nИНСТРУКЦИИ:\n{'─'*50}\n{r['instructions']}\n\n{sep}\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Экспорт", "Рецепт экспортирован!")

    def _toggle_fav_shortcut(self):
        rid = self._get_selected_id()
        if rid:
            db.toggle_favorite(rid)
            self._refresh_list(self._active_tab)

    def _open_admin(self):
        AdminWindow(self, self.user)

    def _about(self):
        messagebox.showinfo(
            "О программе",
            "🍳 Кулинарная книга v1.0\n\n"
            "Стек: Python, CustomTkinter, SQLite\n\n"
            "Горячие клавиши:\n"
            "  Ctrl+N — новый рецепт\n"
            "  Ctrl+F — переключить избранное\n"
            "  Двойной клик — просмотр рецепта"
        )


# ════════════════════════════════════════════════════════════════════════════
# Окно просмотра рецепта
# ════════════════════════════════════════════════════════════════════════════

class RecipeViewer(ctk.CTkToplevel):
    def __init__(self, parent, recipe: dict):
        super().__init__(parent)
        self.recipe = recipe
        self.title(recipe["title"])
        self.geometry("620x640")
        self.configure(fg_color=CREAM)
        self.grab_set()
        self._build(recipe)

    def _build(self, r):
        cat_colors = {
            "Супы": "#3B7BBF", "Выпечка": "#C0392B",
            "Десерты": "#8E44AD", "Основные блюда": "#27AE60",
            "Салаты": "#16A085"
        }
        hdr_color = cat_colors.get(r["category"], OLIVE)

        hdr = ctk.CTkFrame(self, fg_color=hdr_color, corner_radius=0, height=90)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=r["title"],
                     font=("Georgia", 20, "bold"), text_color="#FFFFFF",
                     wraplength=500).pack(padx=24, pady=(14, 0), anchor="w")
        meta = f"{r['category']}   ·   ⏱ {r['cook_time']} мин"
        if r["is_favorite"]:
            meta += "   ·   ⭐ Избранное"
        ctk.CTkLabel(hdr, text=meta, font=("Segoe UI", 12),
                     text_color="#DDDDDD").pack(padx=24, anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=CREAM, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        def section(title, content):
            f = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12,
                             border_width=1, border_color=BORDER)
            f.pack(padx=20, pady=(12, 0), fill="x")
            ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"),
                         text_color=OLIVE, anchor="w").pack(padx=16, pady=(12, 6), anchor="w")
            tb = ctk.CTkTextbox(f, height=120, font=("Segoe UI", 12),
                                fg_color=CREAM, border_width=0,
                                text_color=TEXT, corner_radius=8, wrap="word")
            tb.pack(padx=16, pady=(0, 12), fill="x")
            tb.insert("1.0", content)
            tb.configure(state="disabled")

        section("🧅  Ингредиенты", r["ingredients"])
        section("📝  Инструкции",  r["instructions"])

        btn_row = ctk.CTkFrame(self, fg_color=CREAM, corner_radius=0)
        btn_row.pack(padx=20, pady=16, fill="x")

        def toggle_fav():
            db.toggle_favorite(r["id"])
            new_r = next((x for x in db.get_all_recipes() if x["id"] == r["id"]), None)
            if new_r:
                lbl = "💛  Убрать из избранного" if new_r["is_favorite"] else "⭐  В избранное"
                fc  = GOLD if new_r["is_favorite"] else OLIVE_LT
                btn_fav.configure(text=lbl, fg_color=fc)

        btn_fav = ctk.CTkButton(
            btn_row,
            text="💛  Убрать из избранного" if r["is_favorite"] else "⭐  В избранное",
            font=("Segoe UI", 13), height=42, corner_radius=10,
            fg_color=GOLD if r["is_favorite"] else OLIVE_LT,
            hover_color="#C8860A" if r["is_favorite"] else OLIVE,
            command=toggle_fav)
        btn_fav.pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="✕  Закрыть",
            font=("Segoe UI", 13), height=42, corner_radius=10,
            fg_color=ACCENT, hover_color="#A93226",
            command=self.destroy
        ).pack(side="left", expand=True, fill="x")


# ════════════════════════════════════════════════════════════════════════════
# Окно администратора
# ════════════════════════════════════════════════════════════════════════════

class AdminWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Управление пользователями")
        self.geometry("540x460")
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=0, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="👥  Управление пользователями",
                     font=("Georgia", 15, "bold"), text_color="#F5ECD7").pack(
            side="left", padx=20, pady=14)

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14,
                            border_width=1, border_color=BORDER)
        card.pack(padx=20, pady=20, fill="both", expand=True)

        self.tree = ttk.Treeview(card, columns=("id", "login", "role"),
                                  show="headings", style="Admin.Treeview")
        for col, hd, w in [("id", "ID", 50), ("login", "Логин", 220), ("role", "Роль", 130)]:
            self.tree.heading(col, text=hd)
            self.tree.column(col, width=w, anchor="w")
        vsb = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 4), pady=8)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(padx=20, pady=(0, 16), fill="x")

        ctk.CTkButton(btn_row, text="🗑  Удалить пользователя",
                      font=("Segoe UI", 13), height=40, corner_radius=10,
                      fg_color=ACCENT, hover_color="#A93226",
                      command=self._delete_user).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(btn_row, text="🔑  Сбросить пароль",
                      font=("Segoe UI", 13), height=40, corner_radius=10,
                      fg_color="#D97706", hover_color="#B45309",
                      command=self._reset_password).pack(side="left", expand=True, fill="x")

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for u in db.get_all_users():
            role = "Администратор" if u["is_admin"] else "Пользователь"
            self.tree.insert("", "end", iid=str(u["id"]),
                             values=(u["id"], u["login"], role))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _delete_user(self):
        uid = self._selected_id()
        if not uid:
            return
        if uid == self.current_user["id"]:
            messagebox.showwarning("Ошибка", "Нельзя удалить себя.")
            return
        if not messagebox.askyesno("Удаление", "Удалить пользователя и все его рецепты?"):
            return
        db.delete_user(uid)
        self._load()

    def _reset_password(self):
        uid = self._selected_id()
        if not uid:
            return
        dlg = ctk.CTkInputDialog(text="Новый пароль:", title="Сброс пароля")
        new_p = dlg.get_input()
        if new_p and new_p.strip():
            db.reset_password(uid, new_p.strip())
            messagebox.showinfo("Готово", "Пароль изменён.")
        else:
            messagebox.showwarning("Ошибка", "Пароль не может быть пустым.")


# ════════════════════════════════════════════════════════════════════════════

def main():
    db.init_db()

    auth = AuthWindow()
    auth.mainloop()

    user = auth.get_user()
    if not user:
        return

    app = CookbookApp(user)
    app.mainloop()


if __name__ == "__main__":
    main()
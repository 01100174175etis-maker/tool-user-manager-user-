import datetime
import os
import random
import re
import string
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk


# --- مسار التشغيل ---
def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


base_path = get_base_path()
os.chdir(base_path)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class CardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nour4net يوزرمانجر Pro V7.3")
        self.root.geometry("500x760")
        self.root.minsize(480, 700)
        self.root.configure(fg_color="#F5F5F5")

        self.imported_usernames = []
        self.output_dir = os.path.join(base_path, "الكروت")

        self._build_ui()

    def _build_ui(self):
        self.title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.title_frame.pack(pady=18)
        ctk.CTkLabel(
            self.title_frame,
            text="Nour4net",
            font=("Segoe UI", 28, "bold"),
            text_color="#1A5276",
        ).pack(side="left")
        ctk.CTkLabel(
            self.title_frame,
            text=" Card Generator",
            font=("Segoe UI", 24),
            text_color="#5D6D7E",
        ).pack(side="left")

        self.frame = ctk.CTkFrame(
            self.root,
            corner_radius=20,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D5DBDB",
        )
        self.frame.pack(fill=tk.BOTH, expand=True, padx=26, pady=8)

        self.count_entry = self.create_input("العدد (Match):", "", 0)

        ctk.CTkLabel(self.frame, text="الطول (Length):", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=25, pady=12
        )
        self.length_var = tk.StringVar(value="10")
        self.length_menu = ctk.CTkOptionMenu(
            self.frame,
            width=200,
            values=[str(i) for i in range(8, 15)],
            variable=self.length_var,
        )
        self.length_menu.grid(row=1, column=1, padx=25, pady=12)

        self.prefix_entry = self.create_input("البادئة (Start):", "", 2)
        self.profile_entry = self.create_input("البروفايل (Profile):", "", 3)
        self.limit_entry = self.create_input("التحميل (MB):", "250", 4)

        self.btn_import = ctk.CTkButton(
            self.frame,
            text="📁 1. استيراد وتجميد البيانات",
            command=self.import_logic,
            fg_color="#566573",
            hover_color="#2C3E50",
            height=45,
            font=("Arial", 13, "bold"),
        )
        self.btn_import.grid(row=5, column=0, columnspan=2, pady=(25, 8), padx=25, sticky="ew")

        self.btn_generate = ctk.CTkButton(
            self.frame,
            text="⚡ 2. توليد وحفظ فوري",
            command=self.generate_and_save_instant,
            fg_color="#2E86C1",
            hover_color="#21618C",
            height=45,
            font=("Arial", 13, "bold"),
        )
        self.btn_generate.grid(row=6, column=0, columnspan=2, pady=8, padx=25, sticky="ew")

        self.btn_save = ctk.CTkButton(
            self.frame,
            text="💾 3. حفظ الملف النهائي",
            command=self.save_logic,
            fg_color="#28B463",
            hover_color="#1D8348",
            height=50,
            font=("Arial", 15, "bold"),
        )
        self.btn_save.grid(row=7, column=0, columnspan=2, pady=(15, 5), padx=25, sticky="ew")

        self.btn_open_dir = ctk.CTkButton(
            self.frame,
            text="📂 فتح مجلد الكروت",
            command=self.open_output_folder,
            fg_color="transparent",
            border_width=1,
            border_color="#2E86C1",
            text_color="#2E86C1",
            hover_color="#EBF5FB",
            height=35,
        )
        self.btn_open_dir.grid(row=8, column=0, columnspan=2, pady=(5, 10), padx=25, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.root,
            text="الحالة: جاهز",
            font=("Arial", 12),
            text_color="#7F8C8D",
        )
        self.status_label.pack(pady=10)

    def _set_status(self, text, color="#7F8C8D"):
        self.status_label.configure(text=f"الحالة: {text}", text_color=color)

    def create_input(self, text, default, row):
        ctk.CTkLabel(self.frame, text=text, font=("Arial", 12, "bold")).grid(
            row=row, column=0, sticky="w", padx=25, pady=12
        )
        entry = ctk.CTkEntry(self.frame, width=200, height=35)
        entry.grid(row=row, column=1, padx=25, pady=12)
        entry.insert(0, default)
        return entry

    def _safe_int(self, value, field_name="القيمة"):
        try:
            result = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} يجب أن يكون رقمًا صحيحًا.")
        if result < 0:
            raise ValueError(f"{field_name} لا يمكن أن يكون سالبًا.")
        return result

    def _index_to_suffix(self, index, length, charset):
        if length <= 0:
            return ""
        chars = []
        base = len(charset)
        while length > 0:
            index, remainder = divmod(index, base)
            chars.append(charset[remainder])
            length -= 1
        return "".join(reversed(chars))

    def _generate_usernames(self, prefix, count, total_length):
        prefix = prefix.strip()
        if not prefix:
            raise ValueError("يجب إدخال بادئة قبل التوليد.")

        count = int(count)
        total_length = int(total_length)

        if count <= 0:
            raise ValueError("يجب أن يكون العدد أكبر من صفر.")

        if total_length <= len(prefix):
            raise ValueError("الطول الإجمالي يجب أن يكون أكبر من طول البادئة.")

        suffix_length = total_length - len(prefix)
        charset = string.ascii_letters + string.digits
        max_capacity = len(charset) ** suffix_length

        if count > max_capacity:
            raise ValueError(
                f"الطول الحالي لا يسمح بإنتاج {count} اسم فريد. الحد الأقصى المفترض: {max_capacity}"
            )

        if count == 1:
            return [prefix + self._index_to_suffix(random.randrange(max_capacity), suffix_length, charset)]

        selected_indexes = random.sample(range(max_capacity), count)
        generated = [prefix + self._index_to_suffix(index, suffix_length, charset) for index in selected_indexes]
        return generated

    def _parse_file_users(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError("الملف غير موجود.")

        temp_users = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if file_path.lower().endswith(".rsc"):
                match = re.search(r'name="([^"]+)"', line)
                if match:
                    temp_users.append(match.group(1))
            else:
                temp_users.append(line)

        unique_users = []
        seen = set()
        for user in temp_users:
            if user and user not in seen:
                unique_users.append(user)
                seen.add(user)

        return unique_users

    def open_output_folder(self):
        if not os.path.exists(self.output_dir):
            messagebox.showinfo("تنبيه", "مجلد الكروت لم يتم إنشاؤه بعد.")
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(self.output_dir)
            elif sys.platform == "darwin":
                os.system(f'open "{self.output_dir}"')
            else:
                os.system(f'xdg-open "{self.output_dir}"')
        except Exception:
            messagebox.showerror("خطأ", "تعذر فتح مجلد الكروت.")

    def clear_all_fields(self):
        self.count_entry.configure(state="normal")
        self.prefix_entry.configure(state="normal")
        self.length_menu.configure(state="normal")
        self.count_entry.delete(0, tk.END)
        self.prefix_entry.delete(0, tk.END)
        self.profile_entry.delete(0, tk.END)
        self.limit_entry.delete(0, tk.END)
        self.length_var.set("10")
        self.imported_usernames = []
        self._set_status("تم الحفظ بنجاح وتفريغ الحقول", "#28B463")

    def import_logic(self):
        file_path = filedialog.askopenfilename(filetypes=[("MikroTik & Text", "*.rsc *.txt")])
        if not file_path:
            return

        try:
            imported_users = self._parse_file_users(file_path)
            if not imported_users:
                messagebox.showwarning("تنبيه", "لا توجد كروت صالحة!")
                return

            self.imported_usernames = imported_users
            sample = imported_users[0]

            self.count_entry.configure(state="normal")
            self.prefix_entry.configure(state="normal")
            self.count_entry.delete(0, tk.END)
            self.count_entry.insert(0, str(len(imported_users)))
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, sample[:3])
            self.length_var.set(str(len(sample)))

            self.count_entry.configure(state="disabled")
            self.prefix_entry.configure(state="disabled")
            self.length_menu.configure(state="disabled")
            self._set_status("تم الاستيراد وتجميد الحقول", "#28B463")
        except Exception as exc:
            messagebox.showerror("خطأ", str(exc))

    def _write_rsc(self, folder_path, prefix, profile, limit_bytes):
        rsc_file = os.path.join(folder_path, f"{prefix}.rsc")
        with open(rsc_file, "w", encoding="utf-8") as file:
            if limit_bytes > 0 and profile:
                file.write(f'/tool user-manager profile add name="{profile}" limit-bytes-total={limit_bytes}\n')

            for user in self.imported_usernames:
                file.write(
                    f'/tool user-manager user add customer=admin username="{user}" password="" '
                    f'profile="{profile}" shared-users=1\n'
                )

        return rsc_file

    def _write_txt(self, folder_path, prefix):
        txt_file = os.path.join(folder_path, f"{prefix}.txt")
        with open(txt_file, "w", encoding="utf-8") as file:
            file.write("\n".join(self.imported_usernames))
        return txt_file

    def generate_and_save_instant(self):
        try:
            count = self._safe_int(self.count_entry.get(), "العدد")
            prefix = self.prefix_entry.get().strip()
            total_length = self._safe_int(self.length_var.get(), "الطول")

            if not prefix:
                messagebox.showwarning("تنبيه", "يرجى إدخال البادئة")
                return

            users = self._generate_usernames(prefix, count, total_length)
            self.imported_usernames = users
            self.save_logic(is_instant=True)
            self.clear_all_fields()
        except ValueError as exc:
            messagebox.showerror("خطأ", str(exc))
        except Exception:
            messagebox.showerror("خطأ", "تحقق من صحة الأرقام")

    def save_logic(self, is_instant=False):
        if not self.imported_usernames:
            if not is_instant:
                messagebox.showwarning("تنبيه", "لا توجد بيانات!")
            return

        try:
            prefix = self.prefix_entry.get().strip() or self.imported_usernames[0][:3]
            profile = self.profile_entry.get().strip() or "default_profile"
            limit_gb = self.limit_entry.get().strip()
            limit_value = float(limit_gb) if limit_gb else 0
            limit_bytes = int(limit_value * 1024 ** 3) if limit_value > 0 else 0

            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            folder_name = f"{prefix}-{profile}-{limit_value}GB_{ts}"
            output_path = os.path.join(self.output_dir, folder_name)
            os.makedirs(output_path, exist_ok=True)

            self._write_rsc(output_path, prefix, profile, limit_bytes)
            self._write_txt(output_path, prefix)

            messagebox.showinfo("نجاح الحفظ", f"تم الحفظ باسم ({prefix}) في المجلد:\n{folder_name}")
            if not is_instant:
                self.clear_all_fields()
        except Exception as exc:
            messagebox.showerror("خطأ في الحفظ", str(exc))


if __name__ == "__main__":
    root = ctk.CTk()
    app = CardApp(root)
    root.mainloop()

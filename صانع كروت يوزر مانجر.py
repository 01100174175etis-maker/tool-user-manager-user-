import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import random
import os
import datetime
import string
import re
import sys
import traceback

# --- معالجة مسار التشغيل (حساس جداً لنسخ الـ EXE و 32 بت) ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        # إذا كان يعمل كملف EXE، نحصل على مسار ملف EXE نفسه
        return os.path.dirname(sys.executable)
    # إذا كان يعمل كسكربت بايثون عادي
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
os.chdir(base_path)

# إعدادات الواجهة (الألوان والسمة)
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue") 

class CardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nour4net يوزرمانجر Pro V7.3")
        self.root.geometry("500x750")
        self.root.configure(fg_color="#F5F5F5")
        
        self.imported_usernames = [] 

        # العنوان
        self.title_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.title_frame.pack(pady=20)
        ctk.CTkLabel(self.title_frame, text="Nour4net", font=("Segoe UI", 28, "bold"), text_color="#1A5276").pack(side="left")
        ctk.CTkLabel(self.title_frame, text=" Card Generator", font=("Segoe UI", 24), text_color="#5D6D7E").pack(side="left")

        # حاوية المدخلات
        self.frame = ctk.CTkFrame(root, corner_radius=20, fg_color="#FFFFFF", border_width=1, border_color="#D5DBDB") 
        self.frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10) 

        # الحقول
        self.count_entry = self.create_input("العدد (Match):", "", 0)
        
        ctk.CTkLabel(self.frame, text="الطول (Length):", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=25, pady=12)
        self.length_var = tk.StringVar(value="10")
        self.length_menu = ctk.CTkOptionMenu(self.frame, width=200, values=[str(i) for i in range(8, 15)], variable=self.length_var)
        self.length_menu.grid(row=1, column=1, padx=25, pady=12)

        self.prefix_entry = self.create_input("البادئة (Start):", "", 2)
        self.profile_entry = self.create_input("البروفايل (Profile):", "", 3)
        self.limit_entry = self.create_input("التحميل (MB):", "250", 4)

        # الأزرار
        self.btn_import = ctk.CTkButton(self.frame, text="📁 1. استيراد وتجميد البيانات", command=self.import_logic, 
                                        fg_color="#566573", hover_color="#2C3E50", height=45, font=("Arial", 13, "bold"))
        self.btn_import.grid(row=5, column=0, columnspan=2, pady=(25, 8), padx=25, sticky="ew")

        self.btn_generate = ctk.CTkButton(self.frame, text="⚡ 2. توليد وحفظ فوري", command=self.generate_and_save_instant, 
                                         fg_color="#2E86C1", hover_color="#21618C", height=45, font=("Arial", 13, "bold"))
        self.btn_generate.grid(row=6, column=0, columnspan=2, pady=8, padx=25, sticky="ew")

        self.btn_save = ctk.CTkButton(self.frame, text="💾 3. حفظ الملف النهائي", command=self.save_logic, 
                                      fg_color="#28B463", hover_color="#1D8348", height=50, font=("Arial", 15, "bold"))
        self.btn_save.grid(row=7, column=0, columnspan=2, pady=(15, 5), padx=25, sticky="ew")

        self.btn_open_dir = ctk.CTkButton(self.frame, text="📂 فتح مجلد الكروت", command=self.open_output_folder,
                                          fg_color="transparent", border_width=1, border_color="#2E86C1", 
                                          text_color="#2E86C1", hover_color="#EBF5FB", height=35)
        self.btn_open_dir.grid(row=8, column=0, columnspan=2, pady=(5, 10), padx=25, sticky="ew")

        self.status_label = ctk.CTkLabel(root, text="الحالة: جاهز", font=("Arial", 12), text_color="#7F8C8D")
        self.status_label.pack(pady=10)

    def create_input(self, text, default, row):
        ctk.CTkLabel(self.frame, text=text, font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", padx=25, pady=12)
        entry = ctk.CTkEntry(self.frame, width=200, height=35)
        entry.grid(row=row, column=1, padx=25, pady=12)
        entry.insert(0, default)
        return entry

    def open_output_folder(self):
        folder_path = os.path.join(base_path, "الكروت")
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showinfo("تنبيه", "مجلد الكروت لم يتم إنشاؤه بعد.")

    def clear_all_fields(self):
        self.count_entry.configure(state="normal")
        self.prefix_entry.configure(state="normal")
        self.length_menu.configure(state="normal")
        self.count_entry.delete(0, tk.END)
        self.prefix_entry.delete(0, tk.END)
        self.profile_entry.delete(0, tk.END)
        self.limit_entry.delete(0, tk.END)
        self.length_var.set("") 
        self.imported_usernames = []
        self.status_label.configure(text="الحالة: تم الحفظ بنجاح وتفريغ الحقول", text_color="#28B463")

    def generate_and_save_instant(self):
        try:
            c, p, l = self.count_entry.get(), self.prefix_entry.get(), self.length_var.get()
            if not c or not l or not p:
                messagebox.showwarning("تنبيه", "يرجى ملء الخانات")
                return
            count, total_len = int(c), int(l)
            rem_len = total_len - len(p)
            if count > 10**rem_len:
                messagebox.showerror("خطأ", "الطول لا يستوعب العدد المطلوب!")
                return
            users = set()
            while len(users) < count:
                users.add(p + "".join(random.choices(string.digits, k=rem_len)))
            self.imported_usernames = list(users)
            self.save_logic(is_instant=True)
            self.clear_all_fields()
        except:
            messagebox.showerror("خطأ", "تحقق من صحة الأرقام")

    def import_logic(self):
        path = filedialog.askopenfilename(filetypes=[("MikroTik & Text", "*.rsc *.txt")])
        if not path: return
        try:
            temp_users = []
            with open(path, 'r', encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if path.lower().endswith('.rsc'):
                    match = re.search(r'name="([^"]+)"', line)
                    if match: temp_users.append(match.group(1))
                else:
                    if line: temp_users.append(line)
            if temp_users:
                self.imported_usernames = temp_users
                sample = temp_users[0]
                self.count_entry.configure(state="normal")
                self.prefix_entry.configure(state="normal")
                self.count_entry.delete(0, tk.END); self.count_entry.insert(0, str(len(temp_users)))
                self.prefix_entry.delete(0, tk.END); self.prefix_entry.insert(0, sample[:3])
                self.length_var.set(str(len(sample)))
                self.count_entry.configure(state="disabled")
                self.prefix_entry.configure(state="disabled")
                self.length_menu.configure(state="disabled")
                self.status_label.configure(text="الحالة: تم الاستيراد وتجميد الحقول", text_color="#28B463")
            else:
                messagebox.showwarning("تنبيه", "لا توجد كروت صالحة!")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def save_logic(self, is_instant=False):
        if not self.imported_usernames:
            if not is_instant: messagebox.showwarning("تنبيه", "لا توجد بيانات!")
            return
        try:
            prefix = self.prefix_entry.get().strip()
            profile = self.profile_entry.get().strip()
            limit_gb = self.limit_entry.get().strip()
            limit_val = float(limit_gb) if limit_gb else 0
            limit_cmd = f'limit-bytes-total={int(limit_val * 1024**3)}' if limit_val > 0 else ""
            
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            folder_name = f"{prefix}-{profile}-{limit_val}GB_{ts}"
            
            # ضمان الحفظ في المجلد الرئيسي بجانب البرنامج
            output_path = os.path.join(base_path, "الكروت", folder_name)
            os.makedirs(output_path, exist_ok=True)
            
            rsc_filename = os.path.join(output_path, f"{prefix}.rsc")
            txt_filename = os.path.join(output_path, f"{prefix}.txt")
            
            with open(rsc_filename, "w", encoding="utf-8") as f:
                for u in self.imported_usernames:
                    f.write(f'/tool user-manager user add customer=admin username="{u}" password="" shared-users=1 ;/tool user-manager user create-and-activate-profile customer=admin profile="{profile}" "{u}"')
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.imported_usernames))
                
            messagebox.showinfo("نجاح الحفظ", f"تم الحفظ باسم ({prefix}) في المجلد:\n{folder_name}")
            if not is_instant: self.clear_all_fields()
        except Exception as e:
            messagebox.showerror("خطأ في الحفظ", str(e))

if __name__ == "__main__":
    root = ctk.CTk()
    app = CardApp(root)
    root.mainloop()

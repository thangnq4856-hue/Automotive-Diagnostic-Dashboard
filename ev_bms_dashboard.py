import random
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Cấu hình giao diện tối (Dark Theme) phù hợp cho kỹ sư Automotive
plt.style.use("dark_background")

class BMSDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("EV Battery Management System (BMS) - Digital Twin v2.0")
        self.root.geometry("1000x780")
        self.root.config(bg="#121212")

        # --- KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE ---
        self.init_database()

        # Biến trạng thái hệ thống làm mát
        self.cooling_active = False

        # --- TIÊU ĐỀ ỨNG DỤNG ---
        title_label = tk.Label(
            root,
            text="HỆ THỐNG GIÁM SÁT & QUẢN LÝ PIN XE ĐIỆN (EV-BMS)",
            font=("Arial", 14, "bold"),
            fg="#00ffcc",
            bg="#121212"
        )
        title_label.pack(pady=10)

        # --- KHUNG THÔNG SỐ TỔNG QUAN (TOP PANEL) ---
        top_frame = tk.Frame(root, bg="#1e1e1e", relief=tk.RAISED, bd=1)
        top_frame.pack(fill=tk.X, padx=15, pady=5)

        self.soc_label = tk.Label(top_frame, text="SoC: 85.5%", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1e1e1e")
        self.soc_label.pack(side=tk.LEFT, padx=15, pady=10)

        self.soh_label = tk.Label(top_frame, text="SoH: 98.2%", font=("Arial", 11, "bold"), fg="#00ffcc", bg="#1e1e1e")
        self.soh_label.pack(side=tk.LEFT, padx=15, pady=10)

        self.voltage_label = tk.Label(top_frame, text="Pack Voltage: 400.5 V", font=("Arial", 11, "bold"), fg="#ffaa00", bg="#1e1e1e")
        self.voltage_label.pack(side=tk.LEFT, padx=15, pady=10)

        self.temp_status = tk.Label(top_frame, text="Status: NORMAL", font=("Arial", 11, "bold"), fg="#00ff00", bg="#1e1e1e")
        self.temp_status.pack(side=tk.RIGHT, padx=15, pady=10)

        # --- KHUNG ĐIỀU KHIỂN & TÍNH NĂNG (CONTROL PANEL) ---
        control_frame = tk.Frame(root, bg="#121212")
        control_frame.pack(fill=tk.X, padx=15, pady=5)

        # Nút Bật/Tắt Quạt làm mát
        self.cool_btn = tk.Button(
            control_frame, 
            text="❄️ Bật Quạt Làm Mát (Active Cooling)", 
            font=("Arial", 10, "bold"), 
            bg="#007acc", 
            fg="#ffffff", 
            activebackground="#E4E6E7",
            activeforeground="#a71212",
            command=self.toggle_cooling,
            relief=tk.FLAT,
            padx=10, pady=5
        )
        self.cool_btn.pack(side=tk.LEFT, padx=5)

        # Nút Xem lịch sử lỗi từ SQLite Database
        self.log_btn = tk.Button(
            control_frame, 
            text="📊 Xem Lịch Sử Cảnh Báo (DB)", 
            font=("Arial", 10, "bold"), 
            bg="#333333", 
            fg="#00ffcc", 
            activebackground="#444444",
            activeforeground="#00ffcc",
            command=self.view_alarm_logs,
            relief=tk.FLAT,
            padx=10, pady=5
        )
        self.log_btn.pack(side=tk.LEFT, padx=15)

        # --- KHUNG GIÁM SÁT NHIỆT ĐỘ CELL PIN (MIDDLE PANEL) ---
        cell_frame = tk.LabelFrame(root, text=" Cell Temperature Monitoring (°C) ", font=("Arial", 10, "bold"), fg="#aaaaaa", bg="#121212")
        cell_frame.pack(fill=tk.X, padx=15, pady=8)

        self.cell_labels = []
        for i in range(12):
            lbl = tk.Label(cell_frame, text=f"Cell {i+1}\n-- °C", font=("Arial", 9), width=10, height=2, bg="#2a2a2a", fg="#ffffff")
            lbl.grid(row=i//6, column=i%6, padx=8, pady=8)
            self.cell_labels.append(lbl)

        # --- KHUNG BIỂU ĐỒ TELEMETRY (BOTTOM PANEL) ---
        self.fig, self.ax = plt.subplots(figsize=(9, 3.2))
        self.fig.patch.set_facecolor('#121212')
        self.ax.set_facecolor('#1a1a1a')
        
        self.time_x = []
        self.temp_y = []
        self.line, = self.ax.plot([], [], color="#00ffcc", linewidth=2, marker='o', markersize=4)
        
        self.ax.set_title("Max Cell Temperature over Time", color="#ffffff", fontsize=10)
        self.ax.set_xlabel("Time (s)", color="#aaaaaa")
        self.ax.set_ylabel("Temp (°C)", color="#aaaaaa")
        self.ax.tick_params(colors='white')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        canvas_frame = tk.Frame(root, bg="#121212")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bộ đếm thời gian giả lập dữ liệu thời gian thực
        self.counter = 0
        self.update_bms_data()

    def init_database(self):
        """Khởi tạo SQLite database lưu lịch sử cảnh báo"""
        self.conn = sqlite3.connect("bms_logs.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS alarm_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                max_temp REAL,
                status TEXT
            )
        """)
        self.conn.commit()

    def log_alarm_to_db(self, max_temp, status):
        """Ghi nhận sự kiện cảnh báo vào SQLite"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO alarm_logs (timestamp, max_temp, status)
            VALUES (?, ?, ?)
        """, (timestamp, max_temp, status))
        self.conn.commit()

    def toggle_cooling(self):
        """Bật/Tắt hệ thống quạt làm mát chủ động"""
        self.cooling_active = not self.cooling_active
        if self.cooling_active:
            self.cool_btn.config(text="🔥 Đang Làm Mát (Active: ON)", bg="#ff4444")
        else:
            self.cool_btn.config(text="❄️ Bật Quạt Làm Mát (Active Cooling)", bg="#007acc")

    def update_bms_data(self):
        self.counter += 1
        
        # Giả lập nhiệt độ cell pin
        max_temp = 0
        for i, lbl in enumerate(self.cell_labels):
            # Nếu bật làm mát, nhiệt độ giảm sâu hơn; ngược lại tăng tự nhiên
            if self.cooling_active:
                temp = round(random.uniform(25.0, 32.5), 1)
            else:
                temp = round(random.uniform(28.0, 41.5), 1)
                
            if temp > max_temp:
                max_temp = temp
            
            # Đổi màu cảnh báo
            bg_color = "#2a2a2a"
            fg_color = "#ffffff"
            if temp > 38.0:
                bg_color = "#ff4444" # Đỏ (Quá nhiệt)
            elif temp > 35.0:
                bg_color = "#ffbb33" # Vàng (Cảnh báo)
                fg_color = "#000000"
            
            lbl.config(text=f"Cell {i+1}\n{temp} °C", bg=bg_color, fg=fg_color)

        # Cập nhật trạng thái tổng hệ thống & Lưu Database nếu quá nhiệt
        if max_temp > 38.0:
            status_text = "OVERHEAT WARNING!"
            self.temp_status.config(text=f"Status: {status_text}", fg="#ff4444")
            # Ghi log vào SQLite (mỗi 5 giây ghi 1 lần hoặc khi lỗi để tránh tràn log)
            if self.counter % 5 == 0:
                self.log_alarm_to_db(max_temp, status_text)
        else:
            status_text = "NORMAL (Cooling)" if self.cooling_active else "NORMAL"
            color = "#00ffcc" if self.cooling_active else "#00ff00"
            self.temp_status.config(text=f"Status: {status_text}", fg=color)

        # Cập nhật biểu đồ
        self.time_x.append(self.counter)
        self.temp_y.append(max_temp)
        if len(self.time_x) > 15:
            self.time_x.pop(0)
            self.temp_y.pop(0)

        self.ax.clear()
        self.ax.set_facecolor('#1a1a1a')
        self.ax.plot(self.time_x, self.temp_y, color="#00ffcc", linewidth=2, marker='o', markersize=4)
        self.ax.set_title("Max Cell Temperature over Time", color="#ffffff", fontsize=10)
        self.ax.tick_params(colors='white')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.canvas.draw()

        self.root.after(1000, self.update_bms_data)

    def view_alarm_logs(self):
        """Mở cửa sổ phụ xem lịch sử cảnh báo từ SQLite"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Lịch Sử Cảnh Báo Quá Nhiệt (SQLite Logs)")
        log_window.geometry("600x400")
        log_window.config(bg="#1e1e1e")

        lbl = tk.Label(log_window, text="Danh Sách Sự Kiện Quá Nhiệt Đã Lưu", font=("Arial", 12, "bold"), fg="#00ffcc", bg="#1e1e1e")
        lbl.pack(pady=10)

        # Tạo bảng hiển thị dữ liệu (Treeview)
        tree = ttk.Treeview(log_window, columns=("ID", "Time", "MaxTemp", "Status"), show="headings", height=12)
        tree.heading("ID", text="ID")
        tree.heading("Time", text="Thời Gian")
        tree.heading("MaxTemp", text="Nhiệt Độ Max (°C)")
        tree.heading("Status", text="Trạng Thái")
        
        tree.column("ID", width=50, anchor=tk.CENTER)
        tree.column("Time", width=180, anchor=tk.CENTER)
        tree.column("MaxTemp", width=120, anchor=tk.CENTER)
        tree.column("Status", width=180, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Lấy dữ liệu từ Database
        self.cursor.execute("SELECT id, timestamp, max_temp, status FROM alarm_logs ORDER BY id DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        if not rows:
            messagebox.showinfo("Thông báo", "Chưa có sự kiện quá nhiệt nào được ghi nhận vào Database.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BMSDashboard(root)
    root.mainloop()
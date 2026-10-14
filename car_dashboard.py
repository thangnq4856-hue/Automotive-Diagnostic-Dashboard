import random
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Cấu hình giao diện tối màu cho biểu đồ phù hợp phong cách kỹ thuật
plt.style.use("dark_background")

root = tk.Tk()
root.title("Automotive HiL Diagnostic Dashboard - Live Plotting")
root.geometry("800x650")
root.config(bg="#1e1e1e")

is_fault_cleared = False

# Danh sách lưu trữ dữ liệu lịch sử để vẽ biểu đồ
time_x = []
speed_y = []
rpm_y = []
counter = 0

# Tiêu đề ứng dụng
title_label = tk.Label(
    root,
    text="HỆ THỐNG GIÁM SÁT, CHẨN ĐOÁN ECU & BIỂU ĐỒ TRỰC QUAN",
    font=("Arial", 14, "bold"),
    fg="#00ffcc",
    bg="#1e1e1e",
)
title_label.pack(pady=10)

# Khung chứa các thông số và trạng thái lỗi ở trên
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(fill="x", padx=20)

frame_data = tk.Frame(top_frame, bg="#2d2d2d", bd=2, relief="groove")
frame_data.pack(side="left", fill="both", expand=True, padx=5)

lbl_speed = tk.Label(
    frame_data, text="Tốc độ: 0 km/h", font=("Arial", 11), fg="white", bg="#2d2d2d"
)
lbl_speed.pack(anchor="w", padx=10, pady=4)
lbl_rpm = tk.Label(
    frame_data,
    text="Vòng tua: 800 RPM",
    font=("Arial", 11),
    fg="white",
    bg="#2d2d2d",
)
lbl_rpm.pack(anchor="w", padx=10, pady=4)
lbl_temp = tk.Label(
    frame_data,
    text="Nhiệt độ: 88 °C",
    font=("Arial", 11),
    fg="white",
    bg="#2d2d2d",
)
lbl_temp.pack(anchor="w", padx=10, pady=4)

frame_status = tk.Frame(top_frame, bg="#2d2d2d", bd=2, relief="groove")
frame_status.pack(side="right", fill="both", expand=True, padx=5)

lbl_dtc = tk.Label(
    frame_status,
    text="✅ Bình thường (No Fault)",
    font=("Arial", 10, "bold"),
    fg="#00ff00",
    bg="#2d2d2d",
)
lbl_dtc.pack(anchor="w", padx=10, pady=5)


def clear_dtc():
  global is_fault_cleared
  is_fault_cleared = True
  lbl_dtc.config(text="✅ Đã xóa mã lỗi (DTC Cleared)", fg="#00ffcc")
  frame_status.config(bg="#2d2d2d")
  frame_data.config(bg="#2d2d2d")


btn_clear = tk.Button(
    frame_status,
    text="🧹 Xóa lỗi (Clear DTC)",
    font=("Arial", 9, "bold"),
    bg="#00ffcc",
    fg="#1e1e1e",
    command=clear_dtc,
)
btn_clear.pack(anchor="w", padx=10, pady=5)

# Khung vẽ biểu đồ Matplotlib thời gian thực (Live Plot)
fig, ax = plt.subplots(figsize=(7, 3.5), dpi=100)
fig.patch.set_facecolor("#1e1e1e")
ax.set_facecolor("#2d2d2d")

(line_speed,) = ax.plot([], [], label="Tốc độ (km/h)", color="#00ffcc", linewidth=2)
(line_rpm,) = ax.plot(
    [], [], label="Vòng tua (RPM / 30)", color="#ff4444", linewidth=2
)

ax.set_title(
    "Đồ thị theo dõi thông số vận hành thời gian thực", fontsize=10, color="white"
)
ax.set_xlabel("Chu kỳ thời gian", fontsize=8, color="white")
ax.set_ylabel("Giá trị thông số", fontsize=8, color="white")
ax.tick_params(colors="white", labelsize=8)
ax.legend(loc="upper left", fontsize=8)
ax.grid(True, linestyle="--", alpha=0.3)

# Nhúng biểu đồ vào cửa sổ Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10, padx=20, fill="both", expand=True)


# Hàm cập nhật dữ liệu và vẽ lại đồ thị liên tục
def update_data():
  global counter, is_fault_cleared
  speed = random.randint(0, 110)
  rpm = 800 if speed == 0 else 900 + (speed * 30)
  temp = random.choice([88, 90, 92, 102, 89])

  if temp <= 90:
    is_fault_cleared = False

  lbl_speed.config(text=f"Tốc độ: {speed} km/h")
  lbl_rpm.config(text=f"Vòng tua: {rpm} RPM")
  lbl_temp.config(text=f"Nhiệt độ: {temp} °C")

  if temp > 100:
    if not is_fault_cleared:
      lbl_dtc.config(text="🚨 DTC: P0217 (Quá nhiệt động cơ!)", fg="#ff4444")
      frame_status.config(bg="#4a1515")
      frame_data.config(bg="#4a1515")
    else:
      lbl_dtc.config(
          text="⚠️ Lỗi đã xóa nhưng cảm biến vẫn quá nhiệt!", fg="#ffaa00"
      )
      frame_status.config(bg="#3d3315")
      frame_data.config(bg="#3d3315")
  else:
    if not is_fault_cleared:
      lbl_dtc.config(text="✅ Bình thường (No Fault)", fg="#00ff00")
      frame_status.config(bg="#2d2d2d")
      frame_data.config(bg="#2d2d2d")

  # Cập nhật điểm dữ liệu cho biểu đồ
  counter += 1
  time_x.append(counter)
  speed_y.append(speed)
  rpm_y.append(
      rpm / 30
  )  # Quy đổi tỷ lệ vòng tua nhỏ lại để hiển thị cân đối trên đồ thị

  # Giới hạn giữ lại 15 điểm dữ liệu gần nhất giúp biểu đồ trượt mượt mà
  if len(time_x) > 15:
    time_x.pop(0)
    speed_y.pop(0)
    rpm_y.pop(0)

  line_speed.set_data(time_x, speed_y)
  line_rpm.set_data(time_x, rpm_y)

  ax.relim()
  ax.autoscale_view()
  canvas.draw()

  root.after(1500, update_data)


root.after(100, update_data)
root.mainloop()
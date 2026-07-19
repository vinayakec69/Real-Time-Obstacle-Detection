import tkinter as tk
from tkinter import ttk
import subprocess

class CareLensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CareLens Control Panel")
        self.root.geometry("400x450")
        self.root.configure(bg="#1E1E1E")
        
        self.current_process = None
        
        # Styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TButton", font=("Arial", 12, "bold"), padding=10, background="#007ACC", foreground="white")
        style.map("TButton", background=[("active", "#005999")])
        
        # Title Label
        title = tk.Label(root, text="CareLens Interface", font=("Arial", 20, "bold"), bg="#1E1E1E", fg="white")
        title.pack(pady=20)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: System Idle")
        status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 12), bg="#1E1E1E", fg="#00FF00")
        status_label.pack(pady=10)
        
        # Mode 1: Obstacle Warning
        btn_obstacle = ttk.Button(root, text="👁️ Start Obstacle Warning", command=self.start_obstacle_mode)
        btn_obstacle.pack(fill="x", padx=40, pady=15)
        
        # Mode 2: Navigation
        nav_frame = tk.Frame(root, bg="#1E1E1E")
        nav_frame.pack(fill="x", padx=40, pady=15)
        
        self.target_var = tk.StringVar(value="cell phone")
        targets = ["cell phone", "bottle", "cup", "person"]
        dropdown = ttk.Combobox(nav_frame, textvariable=self.target_var, values=targets, font=("Arial", 12), state="readonly")
        dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_nav = ttk.Button(nav_frame, text="🧭 Find Object", command=self.start_nav_mode)
        btn_nav.pack(side="right")
        
        # Stop Button
        btn_stop = tk.Button(root, text="🛑 STOP SYSTEM", font=("Arial", 14, "bold"), bg="#FF4C4C", fg="white", command=self.stop_system)
        btn_stop.pack(fill="x", padx=40, pady=40)
        
    def start_obstacle_mode(self):
        self.stop_system()
        self.status_var.set("Status: Running Obstacle Mode...")
        # We run the script in the background with --no-gui to save RAM
        self.current_process = subprocess.Popen(["python", "src/detect.py", "--no-gui"])
        
    def start_nav_mode(self):
        target = self.target_var.get()
        self.stop_system()
        self.status_var.set(f"Status: Navigating to {target}...")
        self.current_process = subprocess.Popen(["python", "src/navigate.py", "--target", target])
        
    def stop_system(self):
        if self.current_process:
            self.status_var.set("Status: Stopping...")
            self.root.update()
            self.current_process.terminate()
            self.current_process.wait()
            self.current_process = None
            self.status_var.set("Status: System Idle")

if __name__ == "__main__":
    root = tk.Tk()
    app = CareLensGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_system(), root.destroy()))
    root.mainloop()

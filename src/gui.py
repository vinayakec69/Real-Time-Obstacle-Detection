import tkinter as tk
import subprocess

class CareLensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CareLens Control Panel")
        self.root.geometry("400x450")
        self.root.configure(bg="#1E1E1E")
        
        self.current_process = None
        
        # Title Label
        title = tk.Label(root, text="CareLens Interface", font=("Arial", 20, "bold"), bg="#1E1E1E", fg="white")
        title.pack(pady=20)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: System Idle")
        status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 12), bg="#1E1E1E", fg="#00FF00")
        status_label.pack(pady=10)
        
        # Mode 1: Obstacle Warning
        btn_obstacle = tk.Button(root, text="👁️ Start Obstacle Warning", font=("Arial", 12, "bold"), bg="#007ACC", fg="white", activebackground="#005999", activeforeground="white", command=self.start_obstacle_mode)
        btn_obstacle.pack(fill="x", padx=40, pady=15)
        
        # Mode 2: Navigation
        nav_frame = tk.Frame(root, bg="#1E1E1E")
        nav_frame.pack(fill="x", padx=40, pady=15)
        
        self.target_var = tk.StringVar(value="cell phone")
        targets = ["cell phone", "bottle", "cup", "person"]
        
        # Pure tk OptionMenu to avoid ttk segfaults on Jetson
        dropdown = tk.OptionMenu(nav_frame, self.target_var, *targets)
        dropdown.config(font=("Arial", 12), bg="#333333", fg="white", activebackground="#444444", activeforeground="white", highlightthickness=0)
        dropdown["menu"].config(font=("Arial", 12), bg="#333333", fg="white")
        dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_nav = tk.Button(nav_frame, text="🧭 Find Object", font=("Arial", 12, "bold"), bg="#007ACC", fg="white", activebackground="#005999", activeforeground="white", command=self.start_nav_mode)
        btn_nav.pack(side="right")
        
        # Stop Button
        btn_stop = tk.Button(root, text="🛑 STOP SYSTEM", font=("Arial", 14, "bold"), bg="#FF4C4C", fg="white", activebackground="#CC0000", activeforeground="white", command=self.stop_system)
        btn_stop.pack(fill="x", padx=40, pady=40)
        
    def start_obstacle_mode(self):
        self.stop_system()
        self.status_var.set("Status: Running Obstacle Mode...")
        self.current_process = subprocess.Popen(["python3", "src/detect.py", "--no-gui"])
        
    def start_nav_mode(self):
        target = self.target_var.get()
        self.stop_system()
        self.status_var.set(f"Status: Navigating to {target}...")
        self.current_process = subprocess.Popen(["python3", "src/navigate.py", "--target", target])
        
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

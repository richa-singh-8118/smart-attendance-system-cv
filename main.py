import tkinter as tk
from tkinter import messagebox
import threading
from face_capture import capture_faces
from face_train import train_system
from face_recognize import FaceRecognizer
from surveillance_extension import SurveillanceMonitor

class SmartAttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System")
        self.root.geometry("900x420")
        self.root.configure(bg="#2c3e50")
        
        # Heading
        title = tk.Label(self.root, text="Smart Face Attendance", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=20)
        
        # Main Frame setup
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(pady=10)
        
        # --- Registration Frame ---
        reg_frame = tk.LabelFrame(main_frame, text="1. Register New User", font=("Helvetica", 12, "bold"), 
                                  bg="#34495e", fg="#ecf0f1", padx=20, pady=20)
        reg_frame.grid(row=0, column=0, padx=10, pady=10)
        
        tk.Label(reg_frame, text="Enter Name:", font=("Helvetica", 11), bg="#34495e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(reg_frame, font=("Helvetica", 11), width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        capture_btn = tk.Button(reg_frame, text="Capture Faces", command=self.do_capture, 
                                bg="#3498db", fg="white", font=("Helvetica", 11, "bold"), width=15)
        capture_btn.grid(row=1, column=0, columnspan=2, pady=15)
        
        # --- Train & Recognize Frame ---
        ops_frame = tk.LabelFrame(main_frame, text="2. System Operations", font=("Helvetica", 12, "bold"), 
                                  bg="#34495e", fg="#ecf0f1", padx=20, pady=20)
        ops_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        train_btn = tk.Button(ops_frame, text="Train Database", command=self.do_train, 
                              bg="#f39c12", fg="white", font=("Helvetica", 11, "bold"), width=20)
        train_btn.pack(pady=10)
        
        recognize_btn = tk.Button(ops_frame, text="Start Recognition App", command=self.do_recognize, 
                                  bg="#2ecc71", fg="white", font=("Helvetica", 11, "bold"), width=20)
        recognize_btn.pack(pady=10)
        
        # --- Surveillance Extension Frame ---
        surv_frame = tk.LabelFrame(main_frame, text="3. Surveillance & Safety Mode",
                                   font=("Helvetica", 12, "bold"),
                                   bg="#34495e", fg="#ecf0f1", padx=20, pady=20)
        surv_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
        
        tk.Label(surv_frame, text="Zone Label:", font=("Helvetica", 11),
                 bg="#34495e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        self.zone_entry = tk.Entry(surv_frame, font=("Helvetica", 11), width=20)
        self.zone_entry.insert(0, "Office - Main Gate")
        self.zone_entry.grid(row=0, column=1, padx=5, pady=5)
        
        surv_btn = tk.Button(surv_frame, text="Start Surveillance",
                             command=self.do_surveillance,
                             bg="#8e44ad", fg="white",
                             font=("Helvetica", 11, "bold"), width=18)
        surv_btn.grid(row=1, column=0, columnspan=2, pady=15)
        
        info_label = tk.Label(surv_frame,
                              text="Motion • Crowd • Intruder alerts\nLogged to database/surveillance_logs",
                              font=("Helvetica", 9), bg="#34495e", fg="#bdc3c7",
                              justify=tk.CENTER)
        info_label.grid(row=2, column=0, columnspan=2)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, 
                              anchor=tk.W, bg="#2c3e50", fg="white", font=("Helvetica", 10))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def do_capture(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name first.")
            return
            
        self.status_var.set(f"Capturing face data for '{name}'...")
        self.root.update()
        
        # We temporarily hide main window or just let cv2 window open
        success = capture_faces(name, num_images=5)
        if success:
            messagebox.showinfo("Success", f"Face data successfully captured for {name}.")
            self.name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Incomplete", "Capture was exited early or failed. Try again if needed.")
            
        self.status_var.set("Ready")
        
    def do_train(self):
        self.status_var.set("Training system... Please wait.")
        self.root.update()
        
        def run_train():
            success = train_system()
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", "System training completed successfully."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to train. Make sure you have trained folders in 'dataset'."))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            
        threading.Thread(target=run_train).start()

    def do_recognize(self):
        self.status_var.set("Starting webcam for recognition...")
        self.root.update()
        
        # Use simple try-catch and run recognizer
        # It needs main thread for cv2.imshow
        self.root.iconify() # Minimize GUI
        try:
            recognizer = FaceRecognizer()
            recognizer.start_recognition()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        self.root.deiconify() # Restore GUI when cv2 window closes
        self.status_var.set("Ready")

    def do_surveillance(self):
        zone = self.zone_entry.get().strip() or "Office - Main Gate"
        self.status_var.set(f"Surveillance active for zone: {zone}")
        self.root.update()
        self.root.iconify()  # Minimise GUI while feed is open
        try:
            monitor = SurveillanceMonitor(zone=zone)
            monitor.start_monitoring()
        except Exception as e:
            messagebox.showerror("Error", f"Surveillance error: {str(e)}")
        self.root.deiconify()
        self.status_var.set("Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartAttendanceApp(root)
    root.mainloop()

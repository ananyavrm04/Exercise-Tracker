import tkinter as tk
from tkinter import messagebox

try:
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showinfo("Tkinter Test", "Tkinter window opened successfully!")
    root.destroy()
except Exception as e:
    print(f"Error initializing Tkinter: {e}")
    messagebox.showerror("Tkinter Error", f"Failed to initialize Tkinter: {e}")
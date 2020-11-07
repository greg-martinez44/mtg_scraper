import tkinter as tk
from tkinter import ttk

from src.main import main

def on_click():
    main()

root = tk.Tk()
frame = tk.Frame(root)
frame.grid(row=0, column=0)
label = ttk.Label(frame, text="Scraping Data from MTGTop8")
label.grid(row=0, column=0)
button = tk.Button(root, text="Scrape Data", command=on_click)
button.grid(row=1, column=0)

root.mainloop()


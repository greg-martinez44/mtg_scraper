import os
import tkinter as tk
from tkinter import ttk

from src.main import main as start_scraping



class LabelInput(tk.Frame):
    def __init__(
        self,
        parent,
        label="",
        input_class=ttk.Entry,
        input_var=None,
        input_args=None,
        label_args=None,
        **kwargs
        ):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var

        if input_class in (ttk.Checkbutton, ttk.Radiobutton, ttk.Button):
            input_args["text"] = label
            input_args["variable"] = input_var
        else:
            self.label = tk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = input_var

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    # Look at the source code - some of the get methods for the variable types have try/except
    # So it makes sense that the get method here should have it too
    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            # You can see in the source code that the Text widget has its own get method
            elif isinstance(self.input, tk.Text):
                return self.input.get("1.0", tk.END)
            elif isinstance(self.input, tk.Listbox):
                return self.input.get(0, tk.END)
            else:
                return self.input.get()
        except (TypeError, TclError):
            return ""

    def set(self, value, *args, **kwargs):
        if isinstance(self.variable, tk.BooleanVar):
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif isinstance(self.input, (ttk.Radiobutton, ttk.Checkbutton)):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif isinstance(self.input, tk.Text):
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        elif isinstance(self.input, tk.Button):
            pass
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value)

# class ScraperAppFrame(tk.Frame):
#     def __init__(self, parent, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
        
#         self.inputs = {}
#         self.build_scraper()
#         self.build_closer()
        
#         self.reset()

#     def build_scraper(self):
#         scraper_frame = tk.LabelFrame(self, text="Scraper")
#         image = tk.PhotoImage(name="card", file=path_to_cardback, height=470, width=335)
#         self.inputs["scraper_button"] = LabelInput(
#             scraper_frame,
#             input_class=tk.Button,
#             input_args={
#                 "command": self.on_click,
#                 "image": image
#                 }
#             )
#         self.inputs["scraper_button"].grid(row=0, column=0)
#         scraper_frame.grid(row=0, column=0)

#     def build_closer(self):
#         closer_frame = tk.LabelFrame(self)
#         self.inputs["close_button"] = LabelInput(
#             closer_frame,
#             input_class=tk.Button,
#             input_args={
#                 "command": self.destroy,
#                 "text": "Close"
#                 }
#             )
#         self.inputs["close_button"].grid(row=0, column=0)
#         closer_frame.grid(row=1, column=0)

#     def get(self):
#         return {key: widget.get() for key, widget in self.inputs.items()}

#     def reset(self):
#         for widget in self.inputs:
#             self.inputs[widget].set("")

#     def on_click(self):
#         start_scraping()

#     def destroy(self):
#         super().destroy

path_to_cardback = os.path.join(os.path.dirname(__file__), "images/magic_card.png")
class ScraperApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = tk.PhotoImage(name="card", file=path_to_cardback, height=470, width=335),

        self.title("MTG Top 8 Scraper")

        ttk.Label(
            self,
            text="MTG Top 8 Scraper",
            font=("TkDefaultFont", 16)
            ).grid(row=0)

        app_frame = tk.Frame(self)
        tk.Button(
            app_frame,
            text="scraper",
            image=self.image,
            command=self.on_click
            ).grid(row=0)

        tk.Button(
            app_frame,
            text="Close",
            command=super().destroy
            ).grid(row=1)

        app_frame.grid(row=1)
        
        # test_frame = tk.Frame(self)
        # wrapped_fxn = super().register(self.test_validation)
        # test_textbox = LabelInput(
        #     test_frame,
        #     input_args={
        #         "validate": "key",
        #         "validatecommand": (wrapped_fxn, "%P")
        #         }
        #     )
        # test_textbox.grid(row=0)
        # test_frame.grid(row=2)

    def on_click(self):
        start_scraping()

    def test_validation(self, string):
        return len(string) <= 5


if __name__ == "__main__":
    app = ScraperApp()
    app.mainloop()

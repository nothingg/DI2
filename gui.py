import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import importlib
import logging

# Your script files mapped to their respective main functions
scripts = {
    'baac': 'baac',
    'counter_service': 'counter_service',
    'lotus': 'lotus',
    'lotus_tims': 'lotus_tims',
    'mpay': 'mpay',
    'thaipost': 'thaipost',
    'true': 'true'
}

scripts['All'] = 'all'

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(filename)s - %(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
# Add "All" option to run all scripts


# Main GUI application class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Script Runner")

        # Dropdown menu
        self.label_script = tk.Label(self, text="Select Script:")
        self.label_script.pack(pady=10)

        self.script_var = tk.StringVar()
        self.script_menu = ttk.Combobox(self, textvariable=self.script_var)
        self.script_menu['values'] = list(scripts.keys())
        self.script_menu.pack(pady=10)

        # Calendar
        self.label_date = tk.Label(self, text="Select Date:")
        self.label_date.pack(pady=10)

        self.calendar = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=10)

        # Run button
        self.run_button = tk.Button(self, text="Run Script", command=self.run_script)
        self.run_button.pack(pady=20)

        # Result frame
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(pady=20)

        # Status label
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status_var)
        self.status_label.pack(pady=10)

    def run_script(self):
        selected_script = self.script_var.get()
        selected_date = self.calendar.get_date()

        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if selected_script and selected_date:
            self.status_var.set("Running...")
            self.run_button.config(state=tk.DISABLED)
            self.script_menu.config(state=tk.DISABLED)
            self.calendar.config(state=tk.DISABLED)
            threading.Thread(target=self.execute_scripts, args=(selected_script, selected_date)).start()
        else:
            messagebox.showwarning("Input Error", "Please select both script and date")

    def execute_scripts(self, selected_script, selected_date):
        if selected_script == 'All':
            self.run_all_scripts(selected_date)
        else:
            self.run_single_script(selected_script, selected_date)

        self.status_var.set("Finished")
        self.run_button.config(state=tk.NORMAL)
        self.script_menu.config(state=tk.NORMAL)
        self.calendar.config(state=tk.NORMAL)

    def run_single_script(self, script_name, input_date):
        script_module_name = scripts[script_name]
        try:
            script_module = importlib.import_module(script_module_name)
            script_module.main(input_date=input_date)
            result = f"Success : {script_name}"
            # Add result label for success
            label = tk.Label(self.result_frame, text=result, bg="green")
            label.pack(anchor='w')
        except Exception as e:
            result = f"Failed : {script_name}"
            # Show error message in a messagebox
            messagebox.showerror("Error", result)

            # Add result label for Failed
            label = tk.Label(self.result_frame, text=f"Failed : {script_name}",bg="red")
            label.pack(anchor='w')

    def run_all_scripts(self, input_date):
        errors = []
        for script_name in scripts:
            if script_name != 'All':
                try:
                    script_module = importlib.import_module(scripts[script_name])
                    script_module.main(input_date=input_date)
                    result = f"Success : {script_name}"
                    # Add result label for success
                    label = tk.Label(self.result_frame, text=result , bg="green")
                    label.pack(anchor='w')
                except Exception as e:
                    errors.append(f"{script_name}")

        if errors:
            error_messages = "\n".join(errors)
            messagebox.showerror("Error", f"Some scripts failed to run:\n{error_messages}")

            # Add result label for Failed
            label = tk.Label(self.result_frame, text=f"Failed : {error_messages}", bg="red")
            label.pack(anchor='w')

        else:
            messagebox.showinfo("Success", f"All scripts ran successfully with date {input_date}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os

# Global değişkenler
OUTPUT_TXT_PATH = "results/output.txt"

def select_video():
    """Opens a file dialog to select a video file."""
    video_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
    )
    if video_path:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, video_path)

def process_video():
    """Processes the selected video using main_with_txt_output.py."""
    video_path = video_entry.get()
    if not video_path:
        messagebox.showerror("Error", "Please select a video file!")
        return

    try:
        # main_with_txt_output.py çağrısı
        subprocess.run(
            ["python", "main_with_txt_output.py", 
             "--source", video_path, 
             "--output-txt", OUTPUT_TXT_PATH],
            check=True
        )
        messagebox.showinfo("Success", "Video processing completed. You can now filter results.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "An error occurred during video processing.")

def start_filtering():
    """Starts the filtering process based on user input."""
    if not os.path.exists(OUTPUT_TXT_PATH):
        messagebox.showerror("Error", "Processed results not found! Please process a video first.")
        return

    try:
        min_age = int(min_age_entry.get())
        max_age = int(max_age_entry.get())
        gender = gender_var.get()

        # Sonuçları filtrele
        filtered_results = filter_results(min_age, max_age, gender)

        # Sonuçları göster
        results_list.delete(0, tk.END)
        if filtered_results:
            for result in filtered_results:
                results_list.insert(tk.END, result)
        else:
            results_list.insert(tk.END, "No matches found.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid age values.")

def filter_results(min_age, max_age, gender):
    """Filters results from the output.txt file."""
    try:
        with open(OUTPUT_TXT_PATH, "r") as f:
            lines = f.readlines()

        filtered_results = []
        for line in lines:
            result = eval(line.strip())  # Her satırı bir sözlük olarak işleme
            if (
                min_age <= result["age"] <= max_age and
                (gender == "All" or (gender == "Male" and result["gender"] == 1) or (gender == "Female" and result["gender"] == 0))
            ):
                filtered_results.append(
                    f"Age: {result['age']}, Gender: {'Male' if result['gender'] == 1 else 'Female'}, Time: {result['time']}s"
                )
        return filtered_results
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading results: {e}")
        return []

# GUI Setup
root = tk.Tk()
root.title("Video Filter - Age & Gender")

# Video File Selection
video_label = tk.Label(root, text="Video File:")
video_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

video_entry = tk.Entry(root, width=40)
video_entry.grid(row=0, column=1, padx=10, pady=5)

video_button = tk.Button(root, text="Browse", command=select_video)
video_button.grid(row=0, column=2, padx=10, pady=5)

process_button = tk.Button(root, text="Process Video", command=process_video)
process_button.grid(row=1, column=0, columnspan=3, pady=10)

# Age Range Input
age_label = tk.Label(root, text="Age Range:")
age_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

min_age_entry = tk.Entry(root, width=10)
min_age_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
min_age_entry.insert(0, "20")

tk.Label(root, text="to").grid(row=2, column=1, padx=70, pady=5, sticky="w")

max_age_entry = tk.Entry(root, width=10)
max_age_entry.grid(row=2, column=1, padx=100, pady=5, sticky="w")
max_age_entry.insert(0, "30")

# Gender Selection
gender_label = tk.Label(root, text="Gender:")
gender_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

gender_var = tk.StringVar(value="All")
gender_dropdown = ttk.Combobox(root, textvariable=gender_var, values=["All", "Male", "Female"])
gender_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Start Button
start_button = tk.Button(root, text="Start Filtering", command=start_filtering)
start_button.grid(row=4, column=0, columnspan=3, pady=10)

# Results Display
results_label = tk.Label(root, text="Results:")
results_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

results_list = tk.Listbox(root, width=60, height=10)
results_list.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

# Run the GUI
root.mainloop()

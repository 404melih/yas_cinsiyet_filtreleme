import tkinter as tk
from tkinter import filedialog, ttk, messagebox

def select_video():
    """Opens a file dialog to select a video file."""
    video_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
    )
    if video_path:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, video_path)

def start_filtering():
    """Starts the filtering process based on user input."""
    video_path = video_entry.get()
    if not video_path:
        messagebox.showerror("Error", "Please select a video file!")
        return

    try:
        min_age = int(min_age_entry.get())
        max_age = int(max_age_entry.get())
        gender = gender_var.get()

        # Mockup: Replace with actual video processing
        results = process_video(video_path, min_age, max_age, gender)
        
        # Display results
        results_list.delete(0, tk.END)
        if results:
            for result in results:
                results_list.insert(tk.END, result)
        else:
            results_list.insert(tk.END, "No matches found.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid age values.")

def process_video(video_path, min_age, max_age, gender):
    """
    Mockup function for processing video and filtering results.
    Replace with actual logic for filtering faces based on age and gender.
    """
    # Example results
    mock_results = [
        {"age": 25, "gender": "Male", "time": "12.5s"},
        {"age": 30, "gender": "Female", "time": "25.0s"},
        {"age": 20, "gender": "Male", "time": "40.0s"}
    ]
    filtered_results = [
        f"Age: {res['age']}, Gender: {res['gender']}, Time: {res['time']}"
        for res in mock_results
        if min_age <= res["age"] <= max_age and (gender == "All" or res["gender"] == gender)
    ]
    return filtered_results

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

# Age Range Input
age_label = tk.Label(root, text="Age Range:")
age_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

min_age_entry = tk.Entry(root, width=10)
min_age_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
min_age_entry.insert(0, "20")

tk.Label(root, text="to").grid(row=1, column=1, padx=70, pady=5, sticky="w")

max_age_entry = tk.Entry(root, width=10)
max_age_entry.grid(row=1, column=1, padx=100, pady=5, sticky="w")
max_age_entry.insert(0, "30")

# Gender Selection
gender_label = tk.Label(root, text="Gender:")
gender_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

gender_var = tk.StringVar(value="All")
gender_dropdown = ttk.Combobox(root, textvariable=gender_var, values=["All", "Male", "Female"])
gender_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Start Button
start_button = tk.Button(root, text="Start Filtering", command=start_filtering)
start_button.grid(row=3, column=0, columnspan=3, pady=10)

# Results Display
results_label = tk.Label(root, text="Results:")
results_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

results_list = tk.Listbox(root, width=60, height=10)
results_list.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

# Run the GUI
root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
from video_processing import interpolate_video, add_audio_to_video


class VideoInterpolationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Frame Interpolation")
        self.create_widgets()

    def create_widgets(self):
        # Input file selection
        tk.Label(self, text="Input Video File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.input_entry = tk.Entry(self, width=40)
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, padx=10, pady=5)

        # Output file selection
        tk.Label(self, text="Output Video File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.output_entry = tk.Entry(self, width=40)
        self.output_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self, text="Browse...", command=self.browse_output_file).grid(row=1, column=2, padx=10, pady=5)

        # Interpolation factor
        tk.Label(self, text="Interpolation Factor:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.factor_entry = tk.Entry(self, width=10)
        self.factor_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.factor_entry.insert(0, "2")

        # Audio option checkbox
        self.audio_var = tk.BooleanVar()
        self.audio_check = tk.Checkbutton(self, text="Include Audio", variable=self.audio_var)
        self.audio_check.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Start button
        tk.Button(self, text="Start Interpolation", command=self.start_interpolation).grid(row=5, column=1, padx=10, pady=10)

    def browse_input_file(self):
        filename = filedialog.askopenfilename(title="Select input video file", filetypes=[("MP4 files", "*.mp4")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filename)

    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(title="Save output video file", defaultextension=".mp4",
                                                filetypes=[("MP4 files", "*.mp4")])
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, filename)

    def update_progress(self, value):
        self.progress['value'] = value
        self.update_idletasks()

    def start_interpolation(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        try:
            factor = int(self.factor_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid number for interpolation factor.")
            return

        if not input_file or not output_file:
            messagebox.showerror("Input error", "Please select both input and output files.")
            return

        if factor < 1:
            messagebox.showerror("Input error", "Interpolation factor must be at least 1.")
            return

        # Start the interpolation in a new thread
        threading.Thread(target=self.run_interpolation, args=(input_file, output_file, factor, self.audio_var.get())).start()

    def run_interpolation(self, input_file, output_file, factor, include_audio):
        try:
            # Interpolacja wideo
            interpolate_video(input_file, output_file, factor, progress_callback=self.update_progress)

            # Reset progress bar before starting audio addition
            self.progress['value'] = 0
            self.update_idletasks()

            # Dodanie audio i nadpisanie pliku
            if include_audio:
                self.add_audio_with_progress(input_file, output_file)

            # Powiadomienie o zakończeniu całego procesu
            messagebox.showinfo("Success", "Final video has been created successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_audio_with_progress(self, input_file, output_file):
        """Dodaje audio do pliku wideo, aktualizując pasek postępu."""

        # Dodanie audio z aktualizacją paska postępu
        def progress_callback(current, total):
            progress = (current / total) * 100
            self.update_progress(progress)

        add_audio_to_video(input_file, output_file, progress_callback)


if __name__ == "__main__":
    app = VideoInterpolationApp()
    app.mainloop()

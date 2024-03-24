import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from threading import Thread
from pytube import YouTube
import requests
import os

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")

        self.style = ttk.Style()
        self.style.configure('TButton', font=('calibri', 12, 'bold'), foreground='green')
        self.style.configure('TLabel', font=('calibri', 12), foreground='black')

        self.url_label = ttk.Label(master, text="Enter YouTube URL:")
        self.url_label.pack()

        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.pack()

        self.download_button = ttk.Button(master, text="Download", command=self.download_thread)
        self.download_button.pack()

        self.thumbnail_label = ttk.Label(master)
        self.thumbnail_label.pack()

        self.title_label = ttk.Label(master, text="")
        self.title_label.pack()

        self.progress_label = ttk.Label(master, text="")
        self.progress_label.pack()

        self.progressbar = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progressbar.pack()

        # Set initial state
        self.download_button_state('normal')
        self.progress_label.config(text="")

    def download_thread(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        self.download_button_state('disabled')
        self.progressbar.start(10)
        self.download_thread = Thread(target=self.download_video, args=(url,))
        self.download_thread.start()

    def download_video(self, url):
        try:
            yt = YouTube(url, on_progress_callback=self.show_progress)
            stream = yt.streams.get_highest_resolution()
            video_title = yt.title
            thumbnail_url = yt.thumbnail_url

            # Download the thumbnail image
            thumbnail_filename = os.path.basename(thumbnail_url)
            thumbnail_path = os.path.join(os.getcwd(), thumbnail_filename)
            if not os.path.exists(thumbnail_path):
                img_data = requests.get(thumbnail_url).content
                with open(thumbnail_path, 'wb') as handler:
                    handler.write(img_data)

            # Update GUI with thumbnail and title
            self.update_thumbnail(thumbnail_path)
            self.update_title(video_title)

            # Download the video
            print("Downloading:", video_title)
            stream.download()
            print("Download completed!")
            messagebox.showinfo("Success", "Download completed successfully.")
        except Exception as e:
            print("Error:", str(e))
            messagebox.showerror("Error", "An error occurred during download.")

        self.progressbar.stop()
        self.download_button_state('normal')

    def show_progress(self, stream, chunk, bytes_remaining):
        total_bytes = stream.filesize
        bytes_downloaded = total_bytes - bytes_remaining
        percentage = (bytes_downloaded / total_bytes) * 100
        self.progress_label.config(text="Downloading: {:.1f}%".format(percentage))
        self.progressbar['value'] = percentage

    def update_thumbnail(self, thumbnail_path):
        img = Image.open(thumbnail_path)
        img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        self.thumbnail_label.config(image=img)
        self.thumbnail_label.image = img

    def update_title(self, title):
        self.title_label.config(text="Title: " + title)

    def download_button_state(self, state):
        self.download_button.config(state=state)

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

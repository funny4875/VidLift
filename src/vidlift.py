"""Extract embedded video files from PowerPoint presentations."""

from pathlib import Path
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile


VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".wmv", ".avi", ".mpeg", ".mpg", ".webm", ".mkv", ".3gp"}


def extract_videos(source: Path, destination: Path, report=lambda message: None) -> list[Path]:
    if source.suffix.lower() != ".pptx":
        raise ValueError("請選擇 .pptx 簡報檔。")
    if not source.is_file():
        raise FileNotFoundError("找不到選取的簡報檔。")
    try:
        archive = zipfile.ZipFile(source)
    except zipfile.BadZipFile as exc:
        raise ValueError("這不是有效的 PPTX 檔案，或檔案已損毀。") from exc

    with archive:
        videos = [info for info in archive.infolist()
                  if info.filename.startswith("ppt/media/")
                  and Path(info.filename).suffix.lower() in VIDEO_EXTENSIONS
                  and not info.is_dir()]
        if not videos:
            return []
        destination.mkdir(parents=True, exist_ok=True)
        written = []
        for info in videos:
            original = Path(info.filename).name
            stem, suffix = Path(original).stem, Path(original).suffix
            target = destination / original
            index = 2
            while target.exists():
                target = destination / f"{stem}_{index}{suffix}"
                index += 1
            with archive.open(info) as source_file, target.open("wb") as output_file:
                shutil.copyfileobj(source_file, output_file)
            written.append(target)
            report(f"已匯出：{target.name} ({target.stat().st_size:,} 位元組)")
        return written


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("VidLift - 簡報影片匯出工具")
        root.geometry("650x370")
        root.minsize(550, 320)
        self.source = tk.StringVar()
        self.destination = tk.StringVar()
        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="PPTX 簡報").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.source).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="選取檔案", command=self.choose_source).grid(row=0, column=2)
        ttk.Label(frame, text="輸出資料夾").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.destination).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="選取資料夾", command=self.choose_destination).grid(row=1, column=2)

        self.run_button = ttk.Button(frame, text="匯出影片", command=self.start)
        self.run_button.grid(row=2, column=0, columnspan=3, pady=15)
        self.log = tk.Text(frame, height=11, state="disabled", wrap="word")
        self.log.grid(row=3, column=0, columnspan=3, sticky="nsew")
        frame.rowconfigure(3, weight=1)

    def choose_source(self):
        filename = filedialog.askopenfilename(filetypes=[("PowerPoint 簡報", "*.pptx")])
        if filename:
            self.source.set(filename)
            self.destination.set(str(Path(filename).with_suffix("").parent / (Path(filename).stem + "_影片")))

    def choose_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination.set(folder)

    def write_log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        source = Path(self.source.get().strip())
        destination_text = self.destination.get().strip()
        if not destination_text:
            messagebox.showerror("缺少資料夾", "請選擇輸出資料夾。")
            return
        self.run_button.configure(state="disabled")
        self.write_log(f"開始處理：{source}")
        threading.Thread(target=self.worker, args=(source, Path(destination_text)), daemon=True).start()

    def worker(self, source, destination):
        try:
            files = extract_videos(source, destination, lambda m: self.root.after(0, self.write_log, m))
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            self.root.after(0, self.finish, f"匯出失敗：{exc}", True)
        else:
            self.root.after(0, self.finish, f"完成，共匯出 {len(files)} 個影片。輸出位置：{destination}" if files else "完成，簡報內沒有找到嵌入的影片。", False)

    def finish(self, message, error):
        self.write_log(message)
        self.run_button.configure(state="normal")
        (messagebox.showerror if error else messagebox.showinfo)("匯出結果", message)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--self-test":
        files = extract_videos(Path(sys.argv[2]), Path(sys.argv[3]))
        if not files:
            raise SystemExit("No embedded videos found")
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()

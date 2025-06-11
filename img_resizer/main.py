import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# Try to import drag and drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # type: ignore
    DND_AVAILABLE = True
except ImportError:  # pragma: no cover - optional feature
    DND_AVAILABLE = False
    TkinterDnD = None
    DND_FILES = None

from PIL import Image

class ImageResizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Image Resizer & Compressor")
        self.file_path: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        self.drop_label = ttk.Label(
            frame,
            text="ここに画像をドロップ\nまたはボタンで選択",
            relief="ridge",
            padding=20,
            width=40,
        )
        self.drop_label.pack(fill="both", expand=True)
        if DND_AVAILABLE:
            assert TkinterDnD is not None and DND_FILES is not None
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

        open_btn = ttk.Button(frame, text="ファイルを選択", command=self._open_file)
        open_btn.pack(pady=5)

        size_frame = ttk.Frame(frame)
        size_frame.pack(pady=5)
        ttk.Label(size_frame, text="幅:").pack(side="left")
        self.width_var = tk.StringVar()
        ttk.Entry(size_frame, textvariable=self.width_var, width=6).pack(side="left")
        ttk.Label(size_frame, text="高さ:").pack(side="left")
        self.height_var = tk.StringVar()
        ttk.Entry(size_frame, textvariable=self.height_var, width=6).pack(side="left")
        self.keep_ratio = tk.BooleanVar(value=True)
        ttk.Checkbutton(size_frame, text="比率固定", variable=self.keep_ratio).pack(
            side="left", padx=5
        )

        quality_frame = ttk.Frame(frame)
        quality_frame.pack(pady=5)
        ttk.Label(quality_frame, text="JPEG品質(1-95):").pack(side="left")
        self.quality_var = tk.IntVar(value=85)
        ttk.Entry(quality_frame, textvariable=self.quality_var, width=5).pack(
            side="left"
        )

        ttk.Button(frame, text="保存", command=self._save).pack(pady=10)

    def _open_file(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*"),
            ]
        )
        if path:
            self._set_file(path)

    def _on_drop(self, event: tk.Event) -> None:
        path = event.data
        if path:
            if path.startswith("{") and path.endswith("}"):
                path = path[1:-1]
            path = path.split()[0]
            self._set_file(path)

    def _set_file(self, path: str) -> None:
        self.file_path = path
        self.drop_label.config(text=os.path.basename(path))
        try:
            with Image.open(path) as img:
                self.width_var.set(str(img.width))
                self.height_var.set(str(img.height))
        except Exception as e:  # pragma: no cover - GUI feedback
            messagebox.showerror("エラー", f"画像を開けません: {e}")

    def _save(self) -> None:
        if not self.file_path:
            messagebox.showerror("エラー", "画像が選択されていません")
            return
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError:
            messagebox.showerror("エラー", "幅と高さは整数で指定してください")
            return
        quality = self.quality_var.get()
        out_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*")],
        )
        if not out_path:
            return
        try:
            with Image.open(self.file_path) as img:
                if self.keep_ratio.get():
                    img.thumbnail((width, height))
                else:
                    img = img.resize((width, height))
                if out_path.lower().endswith((".jpg", ".jpeg")):
                    img = img.convert("RGB")
                    img.save(out_path, quality=quality, optimize=True)
                else:
                    img.save(out_path)
            messagebox.showinfo("完了", f"保存しました:\n{out_path}")
        except Exception as e:  # pragma: no cover
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")


def main() -> None:
    root_cls = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk
    root = root_cls()
    app = ImageResizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

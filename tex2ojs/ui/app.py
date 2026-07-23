"""Interface gráfica (Tkinter) do conversor."""

from __future__ import annotations

import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from ..deps import check_dependencies


class App:
    def __init__(self, root):
        self.root = root
        self.log_queue = queue.Queue()
        self.output_dir = None
        self.running = False

        root.title("Tex2HTML — Conversor para o OJS")
        root.geometry("720x560")
        root.minsize(640, 480)

        main = ttk.Frame(root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Conversor LaTeX → HTML (OJS)",
                  font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            main,
            text="Selecione a pasta do artigo (com o .tex, o .bib e a pasta de figuras).\n"
                 "O programa gera uma pasta pronta para o OJS: o HTML e todas as imagens em PNG.",
            foreground="#555",
        ).pack(anchor="w", pady=(2, 12))

        row = ttk.Frame(main)
        row.pack(fill="x")
        self.path_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Selecionar pasta…", command=self.pick_folder).pack(side="left", padx=(8, 0))

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=12)
        self.convert_btn = ttk.Button(actions, text="Converter", command=self.start_conversion)
        self.convert_btn.pack(side="left")
        self.open_btn = ttk.Button(actions, text="Abrir pasta de saída",
                                   command=self.open_output, state="disabled")
        self.open_btn.pack(side="left", padx=(8, 0))
        self.progress = ttk.Progressbar(actions, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(12, 0))

        ttk.Label(main, text="Registro:", foreground="#555").pack(anchor="w")
        self.log_widget = scrolledtext.ScrolledText(main, height=16, state="disabled", wrap="word")
        self.log_widget.pack(fill="both", expand=True, pady=(4, 0))

        self.root.after(100, self.drain_log)

        problems = check_dependencies()
        if problems:
            self.log("Atenção — dependências faltando:")
            for p in problems:
                self.log(f"  • {p}")
            self.log("")

    # -- logging thread-safe ------------------------------------------------ #
    def log(self, message):
        self.log_queue.put(message)

    def drain_log(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_widget.configure(state="normal")
                self.log_widget.insert("end", message + "\n")
                self.log_widget.see("end")
                self.log_widget.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self.drain_log)

    # -- ações -------------------------------------------------------------- #
    def pick_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta do artigo")
        if folder:
            self.path_var.set(folder)

    def start_conversion(self):
        if self.running:
            return
        folder = self.path_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Pasta inválida", "Selecione uma pasta de artigo válida.")
            return
        problems = check_dependencies()
        if problems:
            messagebox.showerror("Dependências faltando", "\n\n".join(problems))
            return

        self.running = True
        self.output_dir = None
        self.convert_btn.configure(state="disabled")
        self.open_btn.configure(state="disabled")
        self.progress.start(12)
        self.log_widget.configure(state="normal")
        self.log_widget.delete("1.0", "end")
        self.log_widget.configure(state="disabled")

        threading.Thread(target=self._worker, args=(folder,), daemon=True).start()

    def _worker(self, folder):
        from .. import convert_article

        try:
            result = convert_article(folder, log=self.log)
            self.output_dir = result.output_dir
            self.log("")
            self.log(f"✓ Concluído! {len(result.images)} imagem(ns) em PNG.")
            if result.warnings:
                self.log("Avisos:")
                for w in result.warnings:
                    self.log(f"  • {w}")
            self.root.after(0, self._finish, True, None)
        except Exception as exc:  # noqa: BLE001
            self.log(f"ERRO: {exc}")
            self.root.after(0, self._finish, False, str(exc))

    def _finish(self, ok, error):
        self.running = False
        self.progress.stop()
        self.convert_btn.configure(state="normal")
        if ok and self.output_dir:
            self.open_btn.configure(state="normal")
            messagebox.showinfo("Concluído", f"Pasta pronta para o OJS:\n{self.output_dir}")
        elif error:
            messagebox.showerror("Erro na conversão", error)

    def open_output(self):
        if not self.output_dir or not os.path.isdir(self.output_dir):
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.output_dir)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", self.output_dir])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", self.output_dir])
        except Exception as exc:  # noqa: BLE001
            messagebox.showwarning("Não foi possível abrir", str(exc))


def run_gui() -> int:
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0

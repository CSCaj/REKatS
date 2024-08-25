import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_file_path):
    docx_file_path = pdf_file_path.replace('.pdf', '.docx')
    cv = Converter(pdf_file_path)
    cv.convert(docx_file_path, start=0, end=None)
    cv.close()
    return docx_file_path

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        try:
            docx_path = convert_pdf_to_docx(file_path)
            messagebox.showinfo("Erfolg", f"Konvertierung abgeschlossen: {docx_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Konvertierung: {str(e)}")

# GUI einrichten
root = tk.Tk()
root.title("PDF zu Word Konverter")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="PDF zu Word Konverter", font=("Helvetica", 16))
label.pack(pady=10)

button = tk.Button(frame, text="PDF Datei auswählen", command=open_file)
button.pack(pady=5)

root.mainloop()

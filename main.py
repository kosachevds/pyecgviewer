import tkinter as tk
import viewer


def main():
    root = tk.Tk()
    root.withdraw()
    dir_ = (r'C:\Users\kdaniil\Desktop\EcgInterpreter\testing'
            r'\check_standard\cse')
    filename = tk.filedialog.askopenfilename(
        filetypes=[("CTS-ECG / CSE-Multilead", "*.cts; M*.dcd")],
        initialdir=dir_
    )
    root.destroy()
    if filename is None:
        return
    if filename.endswith("cts"):
        viewer.show_cts(filename)
    elif filename.lower().endswith("dcd"):
        viewer.show_cse(filename)


if __name__ == '__main__':
    main()

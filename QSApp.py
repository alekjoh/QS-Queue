from tkinter import Tk, Text, BOTH, W, N, E, S, OptionMenu, StringVar, Listbox
from tkinter.ttk import Frame, Button, Label, Style

from QSFokker import QS

subjects = {
    "Machine Learning": "ml",
    "Math": "meth",
    "Security": "sik"
}


class QSApp(Frame):

    def __init__(self):
        super().__init__()

        self.qs = QS()
        self.queue = []

        self.initUI()


    def on_subject_change(self, subject):
        self.queue = self.qs.get_queue(subject=subjects[subject])

        names = [" ".join([q["personFirstName"], q["personLastName"]]) for q in self.queue]
        self.update_queue(names)


    def initUI(self):

        self.master.title("QS")
        self.pack(fill=BOTH, expand=True)

        # self.columnconfigure(1, weight=1)
        # self.columnconfigure(3, pad=7)
        # self.rowconfigure(3, weight=1)
        # self.rowconfigure(5, pad=7)

        self.subject_label = Label(self, text="Choose a subject")
        self.subject_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

        # Subject dropdown menu
        subjects_options = ["Machine Learning", "Security", "Math"]

        self.var = StringVar(self)
        self.var.set(subjects_options[0])

        self.subject_dropdown = OptionMenu(self, self.var, *subjects_options, command=self.on_subject_change)
        self.subject_dropdown.config(width=len(max(subjects_options, key=len)))
        self.subject_dropdown.grid(row=1, column=0, padx=(20, 0), pady=(0, 20), sticky="ew")

        self.queue_label_text = StringVar(self)
        self.queue_label_text.set("People in queue: 0")

        self.queue_label = Label(self, textvariable=self.queue_label_text)
        self.queue_label.grid(row=2, column=0)

        self.queue_listbox = Listbox(self)
        self.queue_listbox.config(width=24)
        self.queue_listbox.grid(row=3, column=0, padx=(20, 0))

        # area = Text(self)
        # area.grid(row=2, column=0, columnspan=6, rowspan=4,
        #     padx=5, sticky=E+W+S+N)
        #
        # abtn = Button(self, text="Activate")
        # abtn.grid(row=0, column=3)
        #
        # cbtn = Button(self, text="Close")
        # cbtn.grid(row=7, column=8, pady=4)
        #
        # hbtn = Button(self, text="Help")
        # hbtn.grid(row=5, column=0, padx=5)
        #
        # obtn = Button(self, text="OK")
        # obtn.grid(row=5, column=3)

    def update_queue(self, values):
        self.queue_listbox.delete(0, "end")
        for val in values:
            self.queue_listbox.insert("end", val)
        self.queue_label_text.set("People in queue: {}".format(len(values)))


def main():

    root = Tk()
    root.geometry("800x600")
    app = QSApp()
    root.mainloop()


if __name__ == '__main__':
    main()
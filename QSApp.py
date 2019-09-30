from tkinter import Tk, Text, BOTH, W, N, E, S, OptionMenu, StringVar, Listbox, Checkbutton, IntVar
from tkinter.ttk import Frame, Button, Label, Style, Combobox

from QSFokker import QS
import random
import time

# Map because I have hardcoded these in QSFokker.... This needs to be fixed.
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
        result = self.qs.get_rooms()

        if result[0] == 200: # Checks if we managed to get the rooms
            self.rooms = result[-1] # Final element is the content
        else:
            raise Exception("Could not load rooms. #RIP") # Why not throw a good ol' error if we cannot find rooms?

        # Stored variables needed for queueing up.
        self.current_subject = None
        self.current_selected_student = None
        self.current_room = None
        self.current_desk = None
        self.students = []

        # Checkbox variables
        self.columns = 5 # Number of checkboxes per row when selecting exercises.
        self.start_row = 2
        self.start_column = 2

        # List of checkboxes and their values.
        self.checkboxes = []
        self.checkvalues = []

        self.initUI()


    def initUI(self):

        self.master.title("QS")
        self.pack(fill=BOTH, expand=True)


        # Mad ghetto code. Needs to be fixed.
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=2)
        self.columnconfigure(4, weight=2)
        self.columnconfigure(5, weight=2)
        self.columnconfigure(6, weight=2)
        self.columnconfigure(7, weight=2)
        self.columnconfigure(8, weight=2)

        self.subject_label = Label(self, text="Choose a subject")
        self.subject_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))

        # Subject dropdown menu
        subjects_options = ["Machine Learning", "Security", "Math"]
        self.current_subject = subjects_options[0]

        # Value used in the dropdown
        self.var = StringVar(self)
        self.var.set(subjects_options[0])

        # Dropdown box. Could potentially used a combobox, idk. But this works I guess.
        self.subject_dropdown = OptionMenu(self, self.var, *subjects_options, command=self.on_subject_change)
        self.subject_dropdown.config(width=len(max(subjects_options, key=len)))
        self.subject_dropdown.grid(row=1, column=0, padx=(20, 0), pady=(0, 20), sticky="ew", columnspan=2)

        # Text with info about how many people there are in the queue.
        self.queue_label_text = StringVar(self)
        self.queue_label_text.set("People in queue: 0")

        # Label with text containing the number of people in the queue.
        self.queue_label = Label(self, textvariable=self.queue_label_text)
        self.queue_label.grid(row=2, column=0, sticky="w", padx=(20, 0))

        # Listbox with everyone in the queue.
        self.queue_listbox = Listbox(self)
        self.queue_listbox.bind("<<ListboxSelect>>", func=self.selected_item) # Runs the selected_item function every time a item is selected.
        self.queue_listbox.config(width=24)
        self.queue_listbox.grid(row=3, column=0, padx=(20, 20), columnspan=2, rowspan=5, sticky="nsew")

        self.random_add_button = Button(self, text="Add Random", command=self.add_random_student)
        self.random_add_button.grid(row=8, column=0, sticky="ew", padx=(20, 0))

        self.delete_button = Button(self, text="Delete", command=self.delete_student)
        self.delete_button.grid(row=8, column=1, sticky="ew")

        self.add_label_info = Label(self, text="Add yourself to the queue")
        self.add_label_info.grid(row=0, column=2, padx=(40, 0), sticky="ew", columnspan=self.columns)


        """
        TODO: FIX this broken space between checkboxes. Have no idead who or what is cucking me so hard.
        """

        self.exercises_var = StringVar(self)
        self.exercises_var.set("Exercises chosen: (None)")
        self.exercises_label = Label(self, textvariable=self.exercises_var)
        self.exercises_label.grid(row=1, column=2, columnspan=self.columns)


        self.room_label = Label(self, text="Room")
        self.room_label.grid(row=8, column=2)
        self.room_list = Combobox(self, values=["{} ({})".format(room["roomName"], room["roomNumber"]) for room in self.rooms], width=44)
        self.room_list.bind("<<ComboboxSelected>>", self.on_room_select)
        self.room_list.grid(row=9, column=2)

        self.desk_label = Label(self, text="Desk")
        self.desk_label.grid(row=10, column=2, pady=(20, 0))
        self.desk_list = Combobox(self, values=["Select a room fgt"])
        self.desk_list.grid(row=11, column=2)

        self.add_to_queue_button = Button(self, text="Add to queue", command=self.add_to_queue)
        self.add_to_queue_button.grid(row=12, column=2, sticky="ew", pady=(20, 0))


    def on_room_select(self, useless_event):
        room = self.rooms[self.room_list.current()]

        desks = room["roomDesks"]
        self.desk_list.delete(0, "end")

        self.desk_list["values"] = [i for i in range(1, desks + 1)]

    def popup(self, message):
        popup = Tk()
        popup.wm_title("!")
        label = Label(popup, text=message)
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Okay", command=popup.destroy)
        B1.pack()
        popup.mainloop()

    def add_to_queue(self):
        room = self.rooms[self.room_list.current()]
        room_id = room["roomID"]

        desk = self.desk_list.get()

        exercises = self.get_selected_exercises()
        if len(exercises) <  1:
            self.popup("You must deliver at least 1 exercise!")

        exercises = [int(ex) for ex in exercises] # Because shit needs to be int (can be float too actually)
        subject = subjects[self.current_subject]

        status_code, reason, content = self.qs.add_to_queue(subject=subject, roomID=room_id, desk=desk, exercises=exercises)

        while status_code != 200:
            status_code, reason, content = self.qs.add_to_queue(subject=subject, roomID=room_id, desk=desk, exercises=exercises)
            time.sleep(0.2)

        self.update_queue()

    def test(self):
        print("Exercises selected:", self.get_selected_exercises())

    """
    Method for updating info about the current selected student in queue.
    """
    def selected_item(self, event):
        w = event.widget

        # Need a try catch here in case someone tries to click on the list when no one is in the queue.
        try:
            index = int(w.curselection()[0])
            person = self.queue[index]
            self.current_selected_student = person
        except Exception as e:
            pass

    """
    Random troll method for placing a random student into the queue. This of course is not abuse, I promise.
    """
    def add_random_student(self):
        subject = subjects[self.current_subject]

        people_not_in_queue = self.qs.get_people(subject=subject)
        rand = random.choice(people_not_in_queue)
        subject_person_id = rand["subjectPersonID"]

        self.qs.add_person_id(subject=subject, personID=subject_person_id)
        self.update_queue()
    """
    Method used by update_queue. It takes in an array and fills the listbox with said values.
    """
    def set_queue(self, values):
        self.queue_listbox.delete(0, "end")
        for val in values:
            self.queue_listbox.insert("end", val)
        self.queue_label_text.set("People in queue: {}".format(len(values)))

    """
    Method called every time the user changes subject. When changing subject, the queue is updated based on the subject
    selected from the dropdown.
    """
    def on_subject_change(self, subject):
        self.current_subject = subject
        self.queue = self.qs.get_queue(subject=subjects[subject])

        self.update_queue()

    """
    Method for deleting a student. Because this cannot be abused what so ever. This method is run every time the delete
    button is pressed.
    """
    def delete_student(self):
        if self.current_selected_student == None: return
        self.qs.remove_from_queue_by_id(subject=subjects[self.current_subject], queueID=self.current_selected_student["queueElementID"])
        self.update_queue()
        self.current_selected_student = None

    """
    Method for updating the queue. It will get the current queue for the current subject selected and load it into the 
    listbox.
    """
    def update_queue(self):
        if self.current_subject != None:
            self.queue = self.qs.get_queue(subject=subjects[self.current_subject])

            values = []
            for q in self.queue:
                exercises = q["queueElementExercises"]

                if exercises == "":
                    exercises = "He hacked!"

                values.append("{} {}     {}  {}  {}".format(q["personFirstName"], q["personLastName"], exercises, q["roomNumber"], q["queueElementDesk"]))

            self.set_queue(values)
            self.set_exercises()

    def get_number_of_subjects(self):
        info = self.qs.get_subject_info(subject=subjects[self.current_subject])
        return info[-1][0]["subjectExercises"]

    def set_exercises(self):
        number_of_subjects = self.get_number_of_subjects()

        # Empty checkboxes.
        for checkbox in self.checkboxes:
            checkbox.grid_forget()

        self.checkboxes = []

        #rows = number_of_subjects // self.columns + 1 # Number of subjects divided by column length rounded up
        self.checkvalues = [IntVar() for i in range(number_of_subjects)] # Default value is 0.

        for i in range(number_of_subjects):
            self.checkboxes.append(Checkbutton(self, variable=self.checkvalues[i], text=str(i + 1), command=self.on_check_box))
            row_number = i // self.columns + self.start_row
            column_number = i % self.columns + self.start_column
            self.checkboxes[i].grid(row=row_number, column=column_number)

    def get_selected_exercises(self):
        return [str(index + 1) for index, checkvalue in enumerate(self.checkvalues) if checkvalue.get() == 1]

    def on_check_box(self):
        exercises = self.get_selected_exercises()
        text = "Exercises chosen: ({})".format(", ".join(self.get_selected_exercises())) if len(exercises) != 0 else "Exercises chosen: (None)"
        self.exercises_var.set(text)


def main():
    # qs = QS()
    # info = qs.get_subject_info("meth")
    # print(info[-1][0]["subjectExercises"])

    root = Tk()
    root.geometry("800x600")
    app = QSApp()
    root.mainloop()


if __name__ == '__main__':
    main()

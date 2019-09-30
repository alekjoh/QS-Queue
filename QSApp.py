# Tkinter imports.
from tkinter import Tk, Text, BOTH, OptionMenu, StringVar, Listbox, Checkbutton, IntVar
from tkinter.ttk import Frame, Button, Label, Style, Combobox

from QSFokker import QS         # QS library which is needed for doing all the requests towards QS.
import random                   # Just for trolling. It is only used for choosing random students to put in the queue.
import time                     # Makes the thread sleep so we do not overload QS by accident.
from threading import Thread    # Needed for spamming requests since without this the program will stop responding because of infinite while loop

# Map because I have hardcoded these in QSFokker.... This needs to be fixed someday (#Refactor is not fun).
subjects = {
    "Machine Learning": "ml",
    "Math": "meth",
    "Security": "sik"
}


class QSApp(Frame):

    """
    Constructor. It is also very messy. Lots of variables needed in the app.
    """
    def __init__(self):
        super().__init__()

        self.qs = QS()
        self.queue = []

        # Stored variables needed for queueing up.
        self.current_subject = None
        self.current_selected_student = None
        self.current_room = None
        self.current_desk = None
        self.current_student_to_add = None

        self.students = []
        self.students_to_add = []

        # Checkbox variables
        self.columns = 5 # Number of checkboxes per row when selecting exercises.
        self.start_row = 2
        self.start_column = 2

        # List of checkboxes and their values.
        self.checkboxes = []
        self.checkvalues = []

        self.request_thread = None
        self.should_stop = False


        # Load stuff

        # Rooms
        result = self.qs.get_rooms()

        if result[0] == 200:  # Checks if we managed to get the rooms
            self.rooms = result[-1]  # Final element is the content
        else:
            raise Exception("Could not load rooms. #RIP")  # Why not throw a good ol' error if we cannot find rooms?


        self.initUI()


    """
    An absolute pile of messy goo. It is very unstructured and bad, but at least it works. Method itself is used for
    placing all the visible aspects on the screen. It is basically the essence of the GUI. The only thing it does not
    display are the checkboxes over the different exercises since those are added via a method (set_exercises).
    """
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
        self.subject_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="we")

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


        self.exercises_var = StringVar(self)
        self.exercises_var.set("Exercises chosen: (None)")
        self.exercises_label = Label(self, textvariable=self.exercises_var)
        self.exercises_label.grid(row=1, column=2, columnspan=self.columns)


        self.room_label = Label(self, text="Room")
        self.room_label.grid(row=8, column=2, columnspan=self.columns)
        self.room_list = Combobox(self, values=["{} ({})".format(room["roomName"], room["roomNumber"]) for room in self.rooms], width=44)
        self.room_list.bind("<<ComboboxSelected>>", self.on_room_select)
        self.room_list.grid(row=9, column=2, columnspan=self.columns)

        self.desk_label = Label(self, text="Desk")
        self.desk_label.grid(row=10, column=2, columnspan=self.columns)
        self.desk_list = Combobox(self, values=["1"])
        self.desk_list.grid(row=11, column=2, columnspan=self.columns, sticky="N")

        self.add_to_queue_button = Button(self, text="Add to queue", command=self.add_to_queue)
        self.add_to_queue_button.grid(row=13, column=2, sticky="ew", pady=(20, 0), columnspan=self.columns)

        self.cancel_button = Button(self, text="Cancel", command=self.cancel_queue)
        self.cancel_button.grid(row=14, column=2, sticky="ew", pady=(5, 0), columnspan=self.columns)


        # Adding students list
        self.student_list = Listbox(self)
        self.student_list.bind("<<ListboxSelect>>", func=self.select_student_to_add)
        self.student_list.bind("<Double-Button-1>", func=self.add_student)
        self.student_list.config(width=40)
        self.student_list.grid(row=12, column=0, padx=(20, 0))

        self.update_students()


        self.student_add_list = Listbox(self)
        self.student_add_list.bind("<<ListboxSelect>>", func=self.select_student_to_remove)
        self.student_add_list.bind("<Double-Button-1>", func=self.remove_student)
        self.student_add_list.config(width=40)
        self.student_add_list.grid(row=12, column=1)


        self.add_student_button = Button(self, text="Add", command=self.add_student)
        self.add_student_button.grid(row=13, column=0, pady=(10, 0))

        self.remove_student_button = Button(self, text="Remove", command=self.remove_student)
        self.remove_student_button.grid(row=13, column=1, pady=(10, 0))


    """
    Method which runs every time you change the room you want to sign up with. The event passed in the method is not 
    used, but the combobox gives an event so the method needs to have it. This method updates the desk combobox with
    the correct desks, since different rooms have different amount of desks.
    """
    def on_room_select(self, useless_event):
        room = self.rooms[self.room_list.current()]

        desks = room["roomDesks"]
        self.desk_list.delete(0, "end")

        self.desk_list["values"] = [i for i in range(1, desks + 1)]

    """
    Method for adding students with you in the queue. It checks if the person exists or not in the list from before and
    if he/she/it does't, then the student is added in the list.
    """
    def add_student(self, event=None):
        if self.current_student_to_add != None:
            if self.current_student_to_add not in self.students_to_add:
                self.students_to_add.append(self.current_student_to_add)
                self.update_students_to_add()
        else:
            print("The student is none....")

    """
    Method for updating the listbox of students you want to add with you in the queue.
    """
    def update_students_to_add(self):
        self.student_add_list.delete(0, "end")
        for stud in self.students_to_add:
            self.student_add_list.insert("end", " ".join([stud["personFirstName"], stud["personLastName"]]))

    """
    Method for removing students from the list of students you want to add with you into a queue. Basically, if you 
    add someone by mistake, you need this method
    """
    def remove_student(self, event=None):
        if self.current_student_to_remove != None:
            if self.current_student_to_remove in self.students_to_add:
                self.students_to_add.remove(self.current_student_to_remove)
                self.update_students_to_add()

    """
    Does what it says it does. It makes a popup window with a message. Usage is for telling the user when input is 
    missing. Huge credit to Sentdex since that is where i "borrowed" this code.
    """
    def popup(self, message):
        popup = Tk()
        popup.wm_title("!")
        label = Label(popup, text=message)
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Okay", command=popup.destroy)
        B1.pack()
        popup.mainloop()

    """
    Method for adding yourself w/o others. It has checks for desk and exercises and sends popups if you miss any of these.
    """
    def add_to_queue(self):
        room = self.rooms[self.room_list.current()]
        room_id = room["roomID"]

        desk = self.desk_list.get()
        if desk.strip() == "":
            self.popup("You must enter a desk!")
            return

        exercises = self.get_selected_exercises()
        if len(exercises) <  1:
            self.popup("You must deliver at least 1 exercise!")
            return

        exercises = [int(ex) for ex in exercises] # Because shit needs to be int (can be float too actually)
        subject = subjects[self.current_subject]

        students = self.students_to_add
        if len(students) == 0:
            students = None
        else:
            students = [" ".join([stud["personFirstName"], stud["personLastName"]]) for stud in students]



        self.should_stop = False  # Needed so the thread knows that it needs to keep going or until we manually stop it.
        self.request_thread = Thread(target=self.spam_add, args=(room_id, desk, exercises, subject, students))
        self.request_thread.start()

        self.update_queue()
        self.exercises_var.set("Exercises chosen: (None)")

    """
    Method for canceling the spam_add method which is run by a thread.
    """
    def cancel_queue(self):
        if self.request_thread != None:
            self.should_stop = True


    """
    Thread method. This is the method which continuously sends requests for joining the queue. A thread is created and
    is told to run this method async so that the program does not suddenly "stops responding". It will continue to send
    requests until it either gets into the queue or the user presses the cancel button. After every request the thread
    will sleep a set of milliseconds before proceeding with the next attempt.
    """
    def spam_add(self, room_id, desk, exercises, subject, students):
        status_code, reason, content = self.qs.add_to_queue(subject=subject, roomID=room_id, desk=desk, exercises=exercises, persons=students)

        while status_code != 200 and not self.should_stop:
            status_code, reason, content = self.qs.add_to_queue(subject=subject, roomID=room_id, desk=desk,
                                                                exercises=exercises, persons=students)
            print(status_code)
            time.sleep(0.2)

        self.update_queue()

    """
    Method for setting the current_student_to_add variable. This is needed so that the add button knows which student 
    to add. The last student selected will be added.
    """
    def select_student_to_add(self, event):
        w = event.widget

        try:
            index = int(w.curselection()[0])
            self.current_student_to_add = self.students[index]
        except:
            pass

    """
    Method for setting the current_student_to_remove variable. This is needed so that the remove button knows which
    student to remove. The last student which was selected will be removed.
    """
    def select_student_to_remove(self, event):
        w = event.widget

        try:
            index = int(w.curselection()[0])
            self.current_student_to_remove = self.students_to_add[index]
        except:
            pass


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

        self.students_to_add = []
        self.current_student_to_add = None
        self.current_student_to_remove = None
        self.update_queue()
        self.update_students()
        self.update_students_to_add()

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

    """
    Method for getting the number of total exercises in the current subject
    """
    def get_number_of_subjects(self):
        info = self.qs.get_subject_info(subject=subjects[self.current_subject])
        return info[-1][0]["subjectExercises"]

    """
    Method for creating a list of checkboxes and a list with their boolean values (int is used here, but it is only 0 or 1).
    It creates as many checkboxes as needed and puts them in an array. Then they are shown on screen. Btw i'm pretty 
    sure the grid of checkboxes will look messed up if we get more than 25 exercises, since then there are more than 
    5x5 = 25 exercises and they will start on a row not expected which will create huge gaps.
    """
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

    """
    Method for getting a list of the exercises which are chosen
    """
    def get_selected_exercises(self):
        return [str(index + 1) for index, checkvalue in enumerate(self.checkvalues) if checkvalue.get() == 1]

    """
    Method which is called every time an exercise checkbox is ticked/unticked. The logic for updating the checkboxes are
    handled elsewhere, this method only updates the label which states the exercises chosen.
    """
    def on_check_box(self):
        exercises = self.get_selected_exercises()
        text = "Exercises chosen: ({})".format(", ".join(self.get_selected_exercises())) if len(exercises) != 0 else "Exercises chosen: (None)"
        self.exercises_var.set(text)

    """
    Method for updating the listbox containing the students you want to add with you in the queue.
    """
    def update_students(self):
        result = self.qs.get_people(subjects[self.current_subject])
        if result[0] == 200:
            self.students = result[-1]
            self.set_students_to_add([" ".join([stud["personFirstName"], stud["personLastName"]]) for stud in self.students])
        else:
            raise Exception("Could not get students because: {} ({})\nContent: {}".format(result[0], result[1], result[2]))

    """
    Method for setting the values in students_to_add listbox
    """
    def set_students_to_add(self, student_names):
        self.student_list.delete(0, "end")
        for name in student_names:
            self.student_list.insert("end", name)


def main():
    root = Tk()
    root.geometry("800x650")
    app = QSApp()
    root.mainloop()

if __name__ == '__main__':
    main()
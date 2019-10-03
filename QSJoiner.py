import argparse
from QSFokker import QS
import time
import config

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-m", "--mode", type=str, help="Specifies the mode (e.g join, remove, delay etc)", required=True)
parser.add_argument("-s", "--subject", type=str, help="Subject name. E.g. meth, ml, sik etc")
parser.add_argument("-e", "--exercises", type=int, nargs="+", help="Exercise numbers to add to the queue. For example assignment 1 and 2 would look like: -e 1 2")
parser.add_argument("-add", "--students", type=str, nargs="+", help="Students. This will be a list of names who will be added to the queue with you")
parser.add_argument("-d", "--desk", type=int, help="Number of the desk")
parser.add_argument("-r", "--room", type=str, help="Room number (e.g 404, 403, lab etc)")
parser.add_argument("-mes", "--message", type=str, help="Message for the teacher/assistant")
parser.add_argument("-help", "--enable_help", type=bool, help="Set to true if help is needed", default=False)

args = parser.parse_args()

subject = args.subject
exercises = args.exercises
students = args.students
mode = args.mode
room = args.room
desk = args.desk
message = args.message
help = args.enable_help

# Map of all the rooms. Room nickname is the key and the value is the room number it has in the qs system
rooms = config.rooms

subject_codes = config.subject_names_shortened

my_token = config.token
qs = QS(token=my_token)

if mode == "add":
    if subject == None or exercises == None or room == None or desk == None:
        print("To add people you need to fill in subject exercises, room and desk")
        exit(1)

    subject_id = subject_codes[subject]
    if subject_id == None:
        print("Input a valid subject. (You either spelled it wrong or you have not added the subject code to your config")
        exit(1)

    room = rooms[room]

    code = 401
    while code != 200:
        code, reason, content = qs.add_to_queue(subject_id=subject_id, room_id=room, desk=desk, message=message, help=help, exercises=exercises, persons=students)
        print(code, reason, content)
        time.sleep(0)

elif mode == "rem":
    if subject == None:
        print("To remove yourself from a queue, you must specify the subject!")
        exit(1)

    subject_id = subject_codes[subject]

    if subject_id == None:
        print("Input a valid subject. (You either spelled it wrong or you have not added the subject code to your config")
        exit(1)

    qs.remove_from_queue(subject_id=subject_id)
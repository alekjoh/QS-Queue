import requests
import json

"""
ABOUT:
A simple class for quickly adding yourself (and potential others) to a QS queue.... That's really it. I mean, it can
remove you from the queue too, but it is pretty useless to have a script do this for you. It can also "troll" someone
by constantly removing someone from the queue so that they can't join, or you can add lots of people into the queue
with invalid exercises for fun.
Oh yeah, you can also get info about students in different subjects and the ones that are already queued up.
"""

# Pure copy paste from Postman because I am too lazy to manually type in these headers.
text = """Sec-Fetch-Mode:cors
    Sec-Fetch-Site:same-origin
    Origin:https://qs.stud.iie.ntnu.no
    Accept-Encoding:gzip, deflate, br
    Accept-Language:nb-NO,nb;q=0.9,no;q=0.8,nn;q=0.7,en-US;q=0.6,en;q=0.5,da;q=0.4
    User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36
    Content-Type:application/json
    Accept:application/json, text/plain, */*
    Referer:https://qs.stud.iie.ntnu.no/student
    Cookie:_ga=GA1.2.1703069537.1547622772; token={}; io=AXI5RkliUpKJQFwiADBK
    Connection:keep-alive
    dnt:1
    """


class QS:
    def __init__(self, token):
        # This is the token that is needed for doing requests (authentication).
        self.token = token

        # URLS
        self.addURL = "https://qs.stud.iie.ntnu.no/res/addQueueElement"
        self.removeURL = "https://qs.stud.iie.ntnu.no/res/deleteQueueElement"
        self.getQueueURL = "https://qs.stud.iie.ntnu.no/res/getQueue"
        self.add_personURL = "https://qs.stud.iie.ntnu.no/res/addPersonToQueueElement"
        self.roomURL = "https://qs.stud.iie.ntnu.no/res/room"
        self.subjectURL = "https://qs.stud.iie.ntnu.no/res/subject"
        self.buildingURL = "https://qs.stud.iie.ntnu.no/res/building"  # Most useless link, it is never used anywhere (Only used for frontend).
        self.studentsURL = "https://qs.stud.iie.ntnu.no/res/studentsInSubject"
        self.postponeURL = "https://qs.stud.iie.ntnu.no/res/studentPostponeQueueElement"
        self.subject_specificURL = "https://qs.stud.iie.ntnu.no/res/regSubjectSpecific"

        # self.subjectIDs = {
        #     "meth": 128,
        #     "ml": 131,
        #     "sik": 130
        # }

        # Id which is needed for removing yourself from the queue....
        self.person_id = 6352

        """
        If you want to ban someone for lyf so that they cannot enter the queue, just set self.personID to the personID
        of your target and then run remove_from_queue(subject) in a while true loop. For example if I wanted to ban
        Sindre for lyf I would just uncomment the id below me and run remove_from_queue for ever! Yes, QS is such
        a nice and secure system that it lets you remove other people for them in case they don't know how to do it 
        themselves...??? Don't question it, it is perfectly balanced as all things should be!
        """

        # Inserts token into headers and makes a dict to feed the request library
        header_lines = text.format(token).split("\n")
        self.headers = {s.split(":")[0].strip(): s.split(":")[1].strip() for s in header_lines if s.strip() != ""}

    """
    Method for adding yourself (and evt other students). It takes in the subject name, which is the name of the subject.
    This name is then checked in the dictionary up in the class attributes. This means the user is responsible for 
    adding the correct subjects to the dictionary for this to work. By default I have added my own subjects.

    The roomID is the id of the id of the room you're in (duh). To find these id's you can do a post towards the 
    room url provided in the URL section above (self.roomURL). By doing this you can get a list of all the rooms and
    their corresponding ids. For my usage I only need 3 of them (404 = 43, 403 = 42 and the lab = 6).

    The desk is just the desk number. For small classrooms it is typically just the number 1, but in bigger rooms 
    (like the lab) there are several desks, so this argument is just a number between 1-n where n is the number of 
    desks in the room

    The message is just a string with a message to the teacher/assistent for additional information

    The help is just a boolean value which tells the teacher/assistant whether you need help or not

    The exercises is a list of the assignments you want to have reviewed. Must be numbers as anything else will be 
    displayed as NaN (Not a Number) in the QS queue system.

    Finally the persons argument is just a list of names. This would be the names of the students you want to join your
    queue. Example would be add_to_queue(persons=["Bob Bobsen", "Boy Boysen"]). This would then add yourself to the
    queue and then later add these 2. If any of these students do not exist or are already in the queue, the program will
    notify you and print the ones that was not added to the queue.
    
    This method returns some information about the reuquest sent like the status code, status code meaning and content of
    response.
    """

    def add_to_queue(self, subject_id, room_id, desk, message=None, help=False, exercises=[8], persons=None):

        # Need to check like this since isinstance() method cannot differentiate between int and bool.
        if not type(subject_id) == int:
            return 999, "Invalid subject type, must be int", "yeet"

        payload = {
            "subjectID": subject_id,
            "roomID": room_id,
            "desk": desk,
            "message": message,
            "help": help,
            "exercises": exercises
        }

        req = requests.post(self.addURL, data=json.dumps(payload), headers=self.headers)
        self.queue_id = req.text.split(":")[-1][:-1]

        status_code = req.status_code

        if req.status_code == 200:
            print("Added to queue for assignment(s) {}".format(", ".join(str(s) for s in exercises)))
        else:
            return status_code, req.reason, req.content

        if persons == None: return status_code, req.reason, req.content

        failed_to_add = []

        for person in persons:
            result = self.find_person_by_name(person.split(" ")[0], person.split(" ")[-1], subject_id=subject_id)


            # If it is none the person never existed or the person is already in the queue so we should just skip this person
            if result == None:
                failed_to_add.append(person)
                continue

            person_id = result["subjectPersonID"]

            add_person_payload = {
                "exercises": exercises,
                "queueElementID": self.queue_id,
                "subjectPersonID": person_id
            }

            req = requests.post(url=self.add_personURL, data=json.dumps(add_person_payload), headers=self.headers)
            if req.status_code != 200:
                print("Rip. Got some error")
                print("{}: {}".format(req.status_code, req.reason))
                print(req.content)

        if len(failed_to_add):
            print("We failed to add: {}".format(", ".join(failed_to_add)))
        else:
            print("Successfully added all students to queue")

        return status_code, req.reason, req.content

    """
    NOTE:
    This method is kind of useless since there really is no need for having a script for removing yourself from the queue.
    Also this method requires a queueElementPosition and QueueID which is RIP to find if you have not run add_to_queue()
    before this method since the program wont know what that ID would be and you'd have to find out manually which
    would take longer than to just remove yourself manually. Just made it to see if it worked and it does, but tbh
    it is a pretty useless method
    """

    def remove_from_queue(self, subject_id, person_id=None):
        if person_id == None:
            person_id = self.person_id

        queue_id = self.get_queueID(subject_id=subject_id, person_subject_id=person_id)

        if queue_id == None:
            print("You are already out of the queue!")
            return

        if subject_id == None:
            print("Cannot remove from invalid subject!")
            return

        payload = {
            "queueElementID": queue_id,
            "subjectID": subject_id
        }

        req = requests.post(url=self.removeURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code != 200:
            print("Rip. Could not remove from queue")
            print("{}: {}".format(req.status_code, req.reason))
            print(req.content)

        return req.status_code

    """
    Same as removing from queue, but this one removes based on queueID instead of personID.
    """
    def remove_from_queue_by_id(self, subject_id, queue_id):
        if not type(subject_id) == int:
            print("Cannot remove from invalid subject!")
            return

        payload = {
            "queueElementID": queue_id,
            "subjectID": subject_id
        }

        req = requests.post(url=self.removeURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code != 200:
            print("Could not remove from queue, rip...")
            print("{}: {}".format(req.status_code, req.reason))
            print(req.content)

        return req.status_code

    """
    Method for getting all the students from a certain subject. It accepts either a subject name or subjectID
    (must be at least one). If both are provided the subjectID will take priority. This will return a list of 
    all students from that subject which are NOT currently in the queue. Which means that if all students are in the
    queue simultaneously this method will give you an empty list.
    """

    def get_people(self, subject_id):
        if not type(subject_id) == int:
            return 999, "Subject ID needs to be an int", "Yeet"

        payload = {
            "subjectID": subject_id
        }

        req = requests.post(url=self.studentsURL, data=json.dumps(payload), headers=self.headers)
        if req.status_code == 200:
            return req.status_code, req.reason, req.json()

        # If we did not get 200 as status code, meaning something went wrong
        return req.status_code, req.reason, req.content

    """
    Method for finding a specific person from a specific subject. It calls upon the get_people() method which gets
    all students currently not in a queue (for that subject) and finds the first person with matching firstname and
    lastname. Note that this method will also check if the student's name starts with the input given.
    Example: Aleksander Johansen would be found with the given input: find_person_by_name("Aleks", "Joh", 128)
    If the person you are searching for does not exist or is already in the queue, this method will return None.
    """

    def find_person_by_name(self, firstname, lastname, subject_id):
        for p in self.get_people(subject_id=subject_id)[-1]:
            if p["personFirstName"] == firstname and p["personLastName"] == lastname or p["personFirstName"].startswith(firstname) and p["personLastName"].startswith(lastname):
                return p

    """
    Method for getting the subjectPersonID based on a firstname, lastname and a subject.
    """

    def get_person_ID(self, firstname, lastname, subject_id):
        return self.find_person_by_name(firstname, lastname, subject_id=subject_id)["subjectPersonID"]

    """
    Method for adding a person to the queue alone. It basically exploits the fact that if you add yourself to the queue
    with somebody, then add yourself to the queue alone, it will create two entries in the queue. 1 with the group you
    added all alone and 1 with just yourself. So if you remove yourself after adding yourself twice, the group will be 
    left behind in the queue, effectively adding only them to the queue.
    """

    def add_person(self, firstname, lastname, subject_id, room_id=6, desk=1, exercises=[3.141592653589793]):
        self.add_to_queue(subject_id=subject_id, room_id=room_id, desk=desk, exercises=exercises,
                          persons=[" ".join([firstname, lastname])])
        self.add_to_queue(subject_id=subject_id, room_id=room_id, desk=desk, exercises=exercises)
        self.remove_from_queue(subject_id=subject_id)

    """
    Same as add person but it uses a personID instead of a name
    """

    def add_person_id(self, subject_id, person_id, room_id=6, desk=1, exercises=[3.141592653589793], help=False,
                      message=None, boost=False):
        self.add_to_queue_with_id(subject_id=subject_id, person_id=person_id, room_id=room_id, desk=desk, exercises=exercises,
                                  help=help, message=message)

        # If you want the person to boost to top (almost, it's 1 posision before first)
        if boost:
            self.boost(subject_id=subject_id, person_id=person_id)

        self.add_to_queue(subject_id=subject_id, room_id=room_id, desk=desk, exercises=exercises)
        self.remove_from_queue(subject_id=subject_id)

    """
    Method for adding every single student in a subject that are not currently in the queue. This is not broken at all
    and should actually be a feature on their website.
    """

    def add_all(self, subject_id, room_id=6, desk=1, exercices=[3.141592653589793]):
        people_not_in_queue = self.get_people(subject_id=subject_id)

        for people in people_not_in_queue:
            self.add_person_id(subject_id=subject_id, person_id=people["subjectPersonID"], room_id=room_id, desk=desk,
                               exercises=exercices)

    """
    Same as add_to_queue just that it adds people based on their id instead of their names. Useful for trying to add
    lots of random people.
    """

    def add_to_queue_with_id(self, subject_id, person_id, room_id, desk, exercises, message=None, help=False):
        payload = {
            "subjectID": subject_id,
            "roomID": room_id,
            "desk": desk,
            "message": message,
            "help": help,
            "exercises": exercises
        }

        req = requests.post(self.addURL, data=json.dumps(payload), headers=self.headers)
        self.queue_id = req.text.split(":")[-1][:-1]

        if req.status_code == 200:
            print("Added to queue for assignment(s) {}".format(", ".join(str(s) for s in exercises)))
        else:
            print("Error. We got status code: {}".format(req.status_code))
            print("Content: {}".format(req.content))

        add_person_payload = {
            "exercises": exercises,
            "queueElementID": self.queue_id,
            "subjectPersonID": person_id
        }

        req = requests.post(url=self.add_personURL, data=json.dumps(add_person_payload), headers=self.headers)

        if req.status_code != 200:
            print("We got")
            print(req.status_code)
            print(req.reason)
            print(req.content)

        return req.status_code, req.reason, req.content

    """
    Method for getting the current queue for a specific subject. It's only argument is the subject name. It will request
    the queue for that subject and return a list of all the students in that queue. If the queue is not open it will 
    return None
    """

    def get_queue(self, subject_id):
        payload = {
            "subjectID": subject_id
        }

        req = requests.post(url=self.getQueueURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code == 200:
            return req.status_code, req.reason, req.json()

        return req.status_code, req.reason, req.content

    """
    Method for getting the queueID of a person in a subject. This method is basically a helper method for the 
    remove_from_queue method. To remove someone you need to know the queueID, so this method finds that id based on
    the subject and the personSubjectID.
    """

    def get_queueID(self, subject_id, person_subject_id):
        status_code, reason, content = self.get_queue(subject_id=subject_id)

        # If we could not get the queue, then return -1 for queueID.
        if status_code != 200:
            return -1

        queue = content

        if isinstance(person_subject_id, int):
            person_subject_id = str(person_subject_id)

        for people in queue:
            if person_subject_id in people["groupmembers"]:
                return people["queueElementID"]

    """
    Method for boosting to the "top". It sends you to the posision before first.
    """

    def boost_self(self, subject_id, person_id):
        queue_id = self.get_queueID(subject_id=subject_id, person_subject_id=person_id)

        payload = {
            "queueElementPosition": 999,
            "queueElementPositionNext": 1,
            "queueElementID": queue_id,
            "subjectID": subject_id
        }

        req = requests.post(url=self.postponeURL, data=json.dumps(payload), headers=self.headers)

        return req.status_code, req.reason, req.content

    """
    Same as boost_self, but it can boost anyone in the queue.
    """
    def boost(self, subject_id, queue_id, queue_position, steps=1):
        payload = {
            "queueElementPosition": queue_position,
            "queueElementPositionNext": queue_position - steps,
            "queueElementID": queue_id,
            "subjectID": subject_id
        }

        req = requests.post(url=self.postponeURL, data=json.dumps(payload), headers=self.headers)

        return req.status_code, req.reason, req.content

    """
    Method for getting information about a specific subject. Used for the QSApp
    """
    def get_subject_info(self, subject_id):
        if not type(subject_id) == int:
            print("Invalid subject")
            return

        payload = {
            "subjectID": subject_id
        }

        req = requests.post(url=self.subject_specificURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code != 200:
            return req.status_code, req.reason, req.content

        return req.status_code, req.reason, req.json()

    """
    Method for getting information about the different rooms.
    """
    def get_rooms(self):
        req = requests.get(url=self.roomURL, headers=self.headers)

        if req.status_code != 200:
            return req.status_code, req.reason, req.content
        else:
            return req.status_code, req.reason, req.json()
import requests
import json

"""
ABOUT:

A simple class for quickly adding yourself (and potential others) to a QS queue.... That's really it. I mean, it can 
you from the queue too, but it is pretty useless to have a script do this for you. Besides the program would then have
to run constantly so that the queueID is saved in the instance of the class otherwise it will not know what your queueID
is and it won't be able to remove you from the queue... so yeah. It is pretty good at adding you to the queue, then 
immediately removing you if you just want to see a use flash in and out of QS' existence. 

Oh yeah, you can also get info about students in different subjects and the ones that are already queued up.
"""

#Pure copy paste from Postman because I am too lazy to manually type in these headers.
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
    def __init__(self, token="%7B%22personID%22%3A6352%2C%22roleID%22%3A8%2C%22personFirstName%22%3A%22Aleksander%22%2C%22personLastName%22%3A%22Johansen%22%2C%22personEmail%22%3A%22aleksjoh%40stud.ntnu.no%22%2C%22personOtherMail%22%3Anull%2C%22roleName%22%3A%22Student%22%2C%22roleLink%22%3A%22%2Fstudent%23%2FstudentMainView%22%2C%22roleDescription%22%3A%22Student%22%2C%22roleShort%22%3A%22Student%22%2C%22personResetToken%22%3A%22d874128356b105838926f8a98230310f%22%2C%22personResetTime%22%3A%222019-02-06T12%3A10%3A27.000Z%22%2C%22sign%22%3A%22b51f85869886e4faba043fc2b4afac015bc47a94664292ab68d0e8527ea59832e6d879d040327793ddefb91854fde6ac51e783b6df7f70c10e9daad525e699dd%22%7D"):
        # This is the token that is needed for doing requests (authentication). By default it is my own cause I don't care if my cookies are on the interwebz, mkay?
        self.token = token

        #URLS
        self.addURL = "https://qs.stud.iie.ntnu.no/res/addQueueElement"
        self.removeURL = "https://qs.stud.iie.ntnu.no/res/deleteQueueElement"
        self.getQueueURL = "https://qs.stud.iie.ntnu.no/res/getQueue"
        self.add_personURL = "https://qs.stud.iie.ntnu.no/res/addPersonToQueueElement"
        self.roomURL = "https://qs.stud.iie.ntnu.no/res/room"
        self.subjectURL = "https://qs.stud.iie.ntnu.no/res/subject"
        self.buildingURL = "https://qs.stud.iie.ntnu.no/res/building"           # Most useless link, it is never used anywhere.
        self.studentsURL = "https://qs.stud.iie.ntnu.no/res/studentsInSubject"

        self.subjectIDs = {
            "meth": 128,
            "ml": 131,
            "sik": 130
        }

        # Id which is needed for removing yourself from the queue....
        self.personID = 6352

        """
        If you want to ban someone for lyf so that they cannot enter the queue, just set self.personID to the personID
        of your target and then run remove_from_queue(subject) in a while true loop. For example if I wanted to ban
        Sindre for lyf I would just uncomment the id below me and run remove_from_queue for ever! Yes, QS is such
        a nice and secure system that it lets you remove other people for them in case they don't know how to do it 
        themselves...??? Don't question it, it is perfectly balanced as all things should be!
        """

        #self.personID = 6395

        # Inserts token into headers and makes a dict to feed the request library
        header_lines = text.format(token).split("\n")
        self.headers = {s.split(":")[0].strip() : s.split(":")[1].strip() for s in header_lines if s.strip() != ""}


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
    """
    def add_to_queue(self, subject, roomID, desk, message=None, help=False, exercises=[8], persons=None):
        payload = {
           "subjectID": self.subjectIDs[subject],
           "roomID": roomID,
           "desk": desk,
           "message": message,
           "help": help,
           "exercises":exercises
        }

        req = requests.post(self.addURL, data=json.dumps(payload), headers=self.headers)
        self.queueID = req.text.split(":")[-1][:-1]
        print(self.queueID)

        if req.status_code == 200:
            print("Added to queue for assignment(s) {}".format(", ".join(str(s) for s in exercises)))
        else:
            print("Error. We got status code: {}".format(req.status_code))
            print("Content: {}".format(req.content))
            exit(1)

        if persons == None: return

        failed_to_add = []

        for person in persons:
            result = self.find_person(person.split(" ")[0], person.split(" ")[-1], "meth")

            # If it is none the person never existed or the person is already in the queue so we should just skip this person
            if result == None:
                failed_to_add.append(person)
                continue

            personID = result["subjectPersonID"]

            add_person_payload = {
                "exercises": exercises,
                "queueElementID": self.queueID,
                "subjectPersonID": personID
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


    """
    NOTE:
    
    This method is kind of useless since there really is no need for having a script for removing yourself from the queue.
    Also this method requires a queueElementPosition and QueueID which is RIP to find if you have not run add_to_queue()
    before this method since the program wont know what that ID would be and you'd have to find out manually which
    would take longer than to just remove yourself manually. Just made it to see if it worked and it does, but tbh
    it is a pretty useless method
    """
    def remove_from_queue(self, subject, personID=None):
        if personID == None:
            personID = self.personID

        queueID = self.get_queueID(subject=subject, personSubjectID=personID)

        if queueID == None:
            print("You are already out of the queue!")
            return

        subjectID = self.subjectIDs[subject]

        if subjectID == None:
            print("Cannot remove from invalid subject!")
            return

        payload = {
            "queueElementID": queueID,
            "subjectID": subjectID
        }

        req = requests.post(url=self.removeURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code != 200:
            print("Rip. Could not remove from queue")
            print("{}: {}".format(req.status_code, req.reason))
            print(req.content)

    """
    Method for getting all the students from a certain subject. It accepts either a subject name or subjectID
    (must be at least one). If both are provided the subjectID will take priority. This will return a list of 
    all students from that subject which are NOT currently in the queue. Which means that if all students are in the
    queue simultaneously this method will give you an empty list.
    """
    def get_people(self, subject=None, subjectID=None):
        # If you don't give anything then pls gtfo.
        if subjectID == None and subject == None:
            return None

        payload = {"subjectID": subjectID} if subjectID != None else {"subjectID": self.subjectIDs[subject]}

        req = requests.post(url=self.studentsURL, data=json.dumps(payload), headers=self.headers)
        if req.status_code == 200:
            return req.json()

        return []

    """
    Method for finding a specific person from a specific subject. It calls upon the get_people() method which gets
    all students currently not in a queue (for that subject) and finds the first person with matching firstname and
    lastname. Note that this method will also check if the student's name starts with the input given.
    Example: Aleksander Johansen would be found with the given input: find_person("Aleks", "Joh", "meth")
    If the person you are searching for does not exist or is already in the queue, this method will return None.
    """
    def find_person(self, firstname, lastname, subject):
        for p in self.get_people(subject=subject):
            if p["personFirstName"] == firstname and p["personLastName"] == lastname or p["personFirstName"].startswith(firstname) and p["personLastName"].startswith(lastname):
                return p

    # Probably useless method... Indeed
    def get_person_ID(self, firstname, lastname, subject):
        return self.find_person(firstname, lastname, subject=subject)["subjectPersonID"]

    """
    Method for getting the current queue for a specific subject. It's only argument is the subject name. It will request
    the queue for that subject and return a list of all the students in that queue. If the queue is not open it will 
    return None
    """
    def get_queue(self, subject):
        payload = {
            "subjectID": self.subjectIDs[subject]
        }

        req = requests.post(url=self.getQueueURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code == 200:
            return req.json()

    def get_queueID(self, subject, personSubjectID):
        queue = self.get_queue(subject=subject)

        if isinstance(personSubjectID, int):
            personSubjectID = str(personSubjectID)

        for people in queue:
            if personSubjectID in people["groupmembers"]:
                return people["queueElementID"]

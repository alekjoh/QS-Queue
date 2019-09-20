import requests
import json

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
        self.token = token

        #URLS
        self.addURL = "https://qs.stud.iie.ntnu.no/res/addQueueElement"
        self.removeURL = "https://qs.stud.iie.ntnu.no/res/deleteQueueElement"
        self.getQueueURL = "https://qs.stud.iie.ntnu.no/res/getQueue"
        self.add_personURL = "https://qs.stud.iie.ntnu.no/res/addPersonToQueueElement"
        self.roomURL = "https://qs.stud.iie.ntnu.no/res/room"
        self.subjectURL = "https://qs.stud.iie.ntnu.no/res/subject"
        self.buildingURL = "https://qs.stud.iie.ntnu.no/res/building"
        self.studentsURL = "https://qs.stud.iie.ntnu.no/res/studentsInSubject"

        self.subjectIDs = {
            "meth": 128,
            "ml": 131,
            "sik": 130
        }

        # Inserts token into headers and makes a dict to feed the request library
        header_lines = text.format(token).split("\n")
        self.headers = {s.split(":")[0].strip() : s.split(":")[1].strip() for s in header_lines if s.strip() != ""}
        self.queueID = 1000


    def add_to_queue(self, subject, roomID=4, desk=1, message=None, help=False, exercises=[8], persons=None):
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

        if req.status_code == 200:
            print("Added to queue for assignment(s) {}".format(", ".join(str(s) for s in exercises)))
        else:
            print("Error. We got status code: {}".format(req.status_code))
            print("Content: {}".format(req.content))
            exit(1)

        if persons == None: return


        for person in persons:
            result = self.find_person(person.split(" ")[0], person.split(" ")[-1], "meth")

            # If it is none the person never existed or the person is already in the queue so we should just skip this person
            if result == None:
                print("Rip. Could not add {} to queue".format(person))
                continue

            personID = result["subjectPersonID"]

            add_person_payload = {
                "exercises": exercises,
                "queueElementID": self.queueID,
                "subjectPersonID": personID
            }

            req = requests.post(url=self.add_personURL, data=json.dumps(add_person_payload), headers=self.headers)

            print(req)
            print(req.content)
            if req.status_code != 200:
                print("Rip. Got some error")
                print("{}: {}".format(req.status_code, req.reason))
                print(req.content)



    def remove_from_queue(self, subject, queueElementPosision, queueID=None):
        if queueID == None:
            queueID = self.queueID

        subjectID = self.subjectIDs[subject]

        if subjectID == None:
            print("Cannot remove from invalid subject!")
            return

        payload = {
            "queueElementID": queueID,
            "subjectID": subjectID,
            "queueElementPosition": queueElementPosision
        }

        req = requests.post(url=self.removeURL, data=json.dumps(payload), headers=self.headers)

        if req.status_code != 200:
            print("Rip. Could not remove from queue")
            print("{}: {}".format(req.status_code, req.reason))
            print(req.content)

    def get_people(self, subject=None, subjectID=None):
        # If you don't give anything then pls gtfo.
        if subjectID == None and subject == None:
            return None

        payload = {"subjectID": subjectID} if subjectID != None else {"subjectID": self.subjectIDs[subject]}

        req = requests.post(url=self.studentsURL, data=json.dumps(payload), headers=self.headers)
        if req.status_code == 200:
            return req.json()

        return []

    def find_person(self, firstname, lastname, subject):
        for p in self.get_people(subject=subject):
            if p["personFirstName"] == firstname and p["personLastName"] == lastname or p["personFirstName"].startswith(firstname) and p["personLastName"].startswith(lastname):
                return p

    # Probably useless method...
    def get_person_ID(self, firstname, lastname, subject):
        return self.find_person(firstname, lastname, subject=subject)["subjectPersonID"]
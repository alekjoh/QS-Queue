from QSFokker import QS

anders_personID = 9407

qs = QS()

#qs.add_person(subject="meth", firstname="Sindre", lastname="Thomassen", exercises=[3.141592653589793])

queue = qs.get_queue("meth")

sindre_id = queue[-1]["groupmembers"]

people = qs.get_people(subject="meth")
for p in queue:
    print(p)


#qs.remove_from_queue(subject="meth", personID=31)
#qs.add_person_id(subject="meth", personID=9387)
#qs.boost(subject="meth", personID=6352)
# for p in people:
#     print(p)

#Removes Rivertz
#qs.remove_from_queue(subject="meth", personID=31)

# Adds Rivertz
qs.add_person_id(subject="meth", personID=9387, help=True, message="Jeg skjønner ikke oppgaven!")
#qs.boost(subject="meth", personID=6352)


#qs.add_to_queue(subject="meth", roomID=6, desk=1, exercises=[3.1415926535], persons=["Anders Iversen"])
# QS-Queue

## About
Program for joining QS queues

Simple class made in Python for joining and leaving QS queues. 


## Some functionalities
-Join a queue given name/id\
-Adding several exercises and/or students\
-Leave a queue given a subject\
-Find info about people in different subjects (names, emails, subjectPersonID, exercises completed etc.)


## Prerequisites
Python (Prob with version >= 3)\
Requests library (pip install requests)\
Something that can run Python code.

## QSJoiner
Command Line Interface for joining the QS queue. Has currently only 2 modes, namely adding and removing to/from queue. Has functionality for sending lots of requests to QS so that the user has good chances of getting first into the queue.

## QSApp
Simple GUI made in Tkinter for easy interaction with QS. It has the most important functionalities from QSFokker. It's badly made (huge messy code), but it works and does the job pretty nicely. Makes it very easy to show the queue and add/remove students to/from the queue.
This program is not finished yet and needs to be polished. It works, but it has some flaws when it comes to updating data like the queue, people you wanted to add etc.

## Config
For this program to work, you must add in data in the config files. This would include your token and other data. Example is shown in the image below.
![alt text](https://i.ibb.co/zRYR3mV/Delete-This.jpg)

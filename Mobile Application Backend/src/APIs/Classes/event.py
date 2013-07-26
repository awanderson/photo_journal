'''
Created on Jul 21, 2013

@author: jacobforster
'''

class Event():
    
    def __init__(self):
        
         #takes the event key and the user key as input parameters and then adds an event reference object as a desendant of the user class that is defined
        #using the user reference key
        #if the date of the event is not transferred in the message then look up event date and add that to the event reference object, or just add date transmitted
        #returns a boolean value if added successfully or not
        
         #basically copies the event message containing all the information and creates a new event object with it
        #check what number the tags are in the user or add the new tags to the user property in the database
        #returns a boolean value if created successfully or not
        
        #removes an event from a users collection and possibly from the database if the event is personal or if it is public and no one has subscribed to it
        
        #DOES IT DELETE THE PICTURES AND EVERYTHING ASSOCIATED WITH IT?????
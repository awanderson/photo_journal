#development api explorer located at localhost:8080/_ah/api/explorer - uses googles own server and passes your localhost as the base so basically accessing your locahost from google's server.. nice
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import endpoints
#from webapp2_extras.appengine.auth import models
from Classes import user
from Classes import notification

"""
Error Messages

10 => User Has No Friends
11 => Could Not Find Friend
12 => User Is Already Registered
13 => Invalid Username/Email And Password
"""


#this is the actual object (message) that we will be transferring
class userMessage(messages.Message):
    userName = messages.StringField(1, required=False)
    password = messages.StringField(2, required=False)
    email = messages.StringField(3, required=False)
    authToken = messages.StringField(5, required=False)
    errorMessage = messages.StringField(6, required=False)
    errorNumber = messages.IntegerField(7, required=False)
    

class authTokenMessage(messages.Message):
    authToken = messages.StringField(1, required=False)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)

class checkFriendsMessage(messages.Message):
    authToken = messages.StringField(1, required=False)
    

class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required=True)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)

#for adding and removing friends, based on key
class friendMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    friendKey = messages.StringField(3, required=True)

#for adding friends based on username instead of key
class friendUserNameMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    friendUserName = messages.StringField(3, required=True)
    
class fullFriendObject(messages.Message):
    #object with all of the friend attributes
    userName = messages.StringField(1, required=True)
    key = messages.StringField(2, required=True)
    email = messages.StringField(3, required=True)
    name = messages.StringField(4, required=True)
    errorMessage = messages.StringField(5, required=False)
    errorNumber = messages.IntegerField(6, required=False)


class returnFriendObjects(messages.Message):
    #creates a list of friend message objects to be returned
    friends = messages.MessageField(fullFriendObject, 1, repeated=True)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)

class fullNotificationObject(messages.Message):
    eventKey = messages.StringField(1)
    creatorKey = messages.StringField(2)
    eventName = messages.StringField(3)
    creatorName = messages.StringField(4)
    created = message_types.DateTimeField(5)
    notificationKey = messages.StringField(6)
    

class returnNotificationObjects(messages.Message):
    
    notifications = messages.MessageField(fullNotificationObject, 1, repeated=True)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)
    
    
    
#used on get methods when only need to validate user
class validateUserMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)  

    
    #need a name for service, version number? and human readable description
@endpoints.api(name='userService', version='v0.202', description='API for User methods', hostname='engaged-context-254.appspot.com')  
class UserApi(remote.Service):
    
    
    """
    Creates user with encrypted password, returning auth token for validation
    """
    @endpoints.method(userMessage, authTokenMessage, name='User.signup', path='signup', http_method='POST')
    def signupUser(self, request):
        
        #makes sure required fields aren't blank
        if (request.userName == "") or (request.password == "") or (request.email == ""):
        
            return authTokenMessage(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #calls backend function, returns token of user
        userData = user.User.signUpUser(request.userName, request.email, request.password)
        
        if not userData[0]:
            return authTokenMessage(errorMessage = userData[1], errorNumber = userData[2])
        
        #get auth token message
        return authTokenMessage(authToken = userData[1])
    
    """
    login method using password and email/username (store in userName field), returns auth token
    """
    @endpoints.method(userMessage, authTokenMessage, name='User.login', path='login', http_method='POST')
    def loginUser(self, request):
        
        #makes sure required fields aren't blank (can put either userName or email in userName field because frontend doesn't know which one user submitted
        if (request.password == "") or (request.userName == ""):
            return authTokenMessage(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #calls user backend function, returns token of user
        userData = user.User.loginUser(request.userName, request.password)
        
        if not userData[0]:
            return authTokenMessage(errorMessage = userData[1], errorNumber = userData[2])
        
        #get auth token
        return authTokenMessage(authToken = userData[1])
        
        
    """
    logout method, simply deletes authtoken from backend
    """
    @endpoints.method(userMessage, callResult, name='User.logout', path='logout', http_method='POST')    
    def logoutUser(self,request):
        
        if (request.userName == "") or (request.authToken == ""):
            return authTokenMessage(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #calls method in user class, returns boolean if token was deleted
        userData = user.User.logoutUser(request.userName, request.authToken)
        
        return callResult(booleanValue=userData)
        
        
        
    def getSettings(self, request):
        pass
        #returns an object with all user settings
        
    def setSettings(self, request):
        pass
    
    
    """
    adds a friend to user given friend key
    """
    @endpoints.method(friendMessage, callResult, name='User.addFriend', path='addFriend', http_method='POST')
    def addFriend(self, request):
        
        #checks for blank fields
        if (request.friendKey == "") or (request.userName == "") or (request.authToken == ""):
            return callResult(booleanValue = False, errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorMessage = "User Validation Failed", errorNumber = 1)
        
        #calls function from user class
        friendExists = user.User.addFriend(userKey, request.friendKey)
        
        #friend doesn't exists, alert frontend
        if not friendExists:
            return callResult(booleanValue = False, errorMessage = "Could Not Find Friend", errorNumber = 11)
        
        #returns true if added
        return callResult(booleanValue = True)
        
        
    """
    adds a friend to user given friend's username
    """
    @endpoints.method(friendUserNameMessage, callResult, name="User.addFriendFromUserName", path='addFriendFromUserName', http_method='POST')
    def addFriendFromUserName(self, request):
        
        #checks for blank fields
        if (request.friendUserName == "") or (request.userName == "") or (request.authToken == ""):
            return callResult(booleanValue = False, errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorMessage = "User Validation Failed", errorNumber = 1)
        
        #calls function from user class
        friendExists = user.User.addFriendFromUserName(userKey, request.friendUserName)
            
    
        if not friendExists:
            return callResult(booleanValue = False, errorMessage = "Could Not Find Friend", errorNumber = 11)
        
        #returns true
        return callResult(booleanValue = True)
    
    
    """
    removes friend from user
    """
    @endpoints.method(friendMessage, callResult, name='User.removeFriend', path='removeFriend', http_method='POST')
    def removeFriend(self, request):
        
        #checks for blank fields
        if (request.friendKey == "") or (request.userName == "") or (request.authToken == ""):
            return callResult(booleanValue = False, errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorMessage = "User Validation Failed", errorNumber = 1)
        
        #calls function from user class
        ndb.transaction(user.User.removeFriend(userKey, request.friendKey))
        
        #returns true
        return callResult(booleanValue = True)
        
    """
    Gets a list of all of users friends
    """
    @endpoints.method(validateUserMessage, returnFriendObjects, name='User.getFriends', path='getFriends', http_method='POST')
    def getFriends(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken==""):
            return returnFriendObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnFriendObjects(errorMessage = "User Validation Failed", errorNumber = 1)
        
        #calls function to get list of friends object
        friendKeyList = user.User.getFriendKeys(userKey)
        
        #defines list variable to hold friends info
        friendInfoList = []
        
        #make sure user has friends to return, if not return error
        if not friendKeyList:
            return returnFriendObjects(errorMessage="User Has No Friends", errorNumber = 10)
        
        #goes through friend list, gets info from class, and puts into list
        for friendKey in friendKeyList:
            
            friendInfo = user.User.getFriendInfo(friendKey)
            userName = friendInfo[0]
            email = friendInfo[1]
            name = friendInfo[2]
            userKey = friendInfo[3]
            fullFriend = fullFriendObject(userName = userName, email = email, name = name, key = userKey)
            friendInfoList.append(fullFriend)
        
        return returnFriendObjects(friends = friendInfoList)
    
    
    @endpoints.method(validateUserMessage, returnNotificationObjects, name='User.getNotifications', path='getNotifications', http_method='POST')    
    def getNotifications(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken==""):
            return returnFriendObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnFriendObjects(errorMessage = "User Validation Failed", errorNumber = 1)
        
        #get all notifications
        notificationObList = notification.Notification.getUserNotifications(userKey)
        
        notificationInfoList = []
        
        #iterates through notification objects
        for notificationOb in notificationObList:
        
            eventKey = notificationOb.eventKey.urlsafe()
            eventName = notificationOb.eventName
            creatorKey = notificationOb.creatorKey.urlsafe()
            notificationKey = notificationOb.key.urlsafe()
            
            #gets the user object to get the name
            creatorInfo = user.User.getFriendInfo(notificationOb.creatorKey)
            creatorName = creatorInfo[2]
            
            created = notificationOb.created
            fullNotification = fullNotificationObject(eventKey = eventKey, eventName=eventName,
                                                      creatorKey = creatorKey, creatorName = creatorName,
                                                      created = created, notificationKey = notificationKey)
            notificationInfoList.append(fullNotification)
            
        return returnNotificationObjects(notifications = notificationInfoList)
    
    def checkUserExist(self):
        pass
        #helper function to check each user - actually in the class
    def checkUsersExist(self):
        pass
        #use a repeated message field... i think
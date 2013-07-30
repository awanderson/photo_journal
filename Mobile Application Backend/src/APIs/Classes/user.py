from google.appengine.ext import ndb
from webapp2_extras import security
from webapp2_extras.appengine.auth import models
import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import tag


class User(ndb.Model):
    
    
    """
    creates user and returns authToken
    """
    @classmethod
    @ndb.transactional(xg=True)
    def signUpUser(cls, userName, email, rawPassword, phone = None):
        
        
        #inserts into db
        unique_properties = ['email_address']
        user_data = models.User.create_user(userName, unique_properties, password_raw = rawPassword, email_address = email, userName = userName)
        
        #this means email/username is already registered, send back error message
        if not user_data[0]:
            error = [False,"User already exists in Database. Please use a different email and/or username", 10]
            return error
        
        #gets user id to use in other api calls
        userId = user_data[1].get_id()
        
        #gets actual user object to be used later
        userOb = models.User.get_by_id(userId)
        
        #creates default tags
        tag.Tag.createDefaultTags(userOb.key)
        
        #adds email as an auth id, needed later to login
        userOb.add_auth_id(email)
        
        #creates auth token
        authToken = models.User.create_auth_token(userId)
        #creates user token
        returnData = [True, authToken]
        
        #returns id of user
        return returnData
    
    
    """
    logins user given username and password, returns authToken to validate user in future
    """
    @classmethod
    @ndb.transactional(xg=True)
    def loginUser(cls,userName, rawPassword):
        
        try:
            #logs in user, returns user object
            userOb = models.User.get_by_auth_password(userName, rawPassword)
            
            #generates new auth token
            authToken = userOb.create_auth_token(userOb.key.id())
            
            returnData = [True, authToken]
            return returnData
            
        except (InvalidAuthIdError, InvalidPasswordError):
            error = [False, "Issue Logging in. Please try again",12]
            return error
    
    """ 
    Logouts user by deleting authToken from database 
    """ 
    @classmethod
    @ndb.transactional(xg=True)
    def logoutUser(cls, userName, authToken):
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        #actually deletes token
        userOb.delete_auth_token(userOb.key.id(), authToken)
        
        return True
    
    """
    adds a friend to user object given a friend key
    """
    @classmethod
    @ndb.transactional(xg=True)
    def addFriend(cls, userKey, friendKey):
        
        userKeyOb = ndb.Key(urlsafe=userKey)
        userOb = userKeyOb.get()
        
        #gets friend key object, makes sure it exists
        try:
            friendKeyOb = ndb.Key(urlsafe=friendKey)
            
        except:
            return False
        
        #tests if user has any friends
        try:
            userOb.friends
            #tests if user is already friend
            if friendKeyOb in userOb.friends:
                return True
        
        except AttributeError:
            pass
        
        #tries appending to existing friend list
        try:
            userOb.friends.append(friendKeyOb)
        
        #no current friends, create new field
        except AttributeError:
            #adds to userKeyOb to trick db into repeating the property
            userOb.friends = [friendKeyOb, userKeyOb]
            #removes userKeyOb from friends
            cls.removeFriend(userKey, userKey)
            
        userOb.put()
        return True
    
    """
    adds a friend to user object given a friend userName
    """
    @classmethod
    @ndb.transactional(xg=True)
    def addFriendFromUserName(cls, userKey, friendUserName):
        userKeyOb = ndb.Key(urlsafe=userKey)
        userOb = userKeyOb.get()
        
        #gets friend object, if exists
        try:
            friendOb = models.User.get_by_auth_id(friendUserName)
            friendKeyOb = friendOb.key
            
        #no such friend by that username, return false
        except:
            return False
        
        #tests if user has any friends
        try:
            userOb.friends
            #tests if user is already friend
            if friendKeyOb in userOb.friends:
                return True
        
        except AttributeError:
            pass
        
        #tries appending to existing friend list
        try:
            userOb.friends.append(friendKeyOb)
        
        #no current friends, create new field
        except AttributeError:
            #adds to userKeyOb to trick db into repeating the property
            userOb.friends = [friendKeyOb, userKeyOb]
            #removes userKeyOb from friends
            cls.removeFriend(userKey, userKey)
            
        userOb.put()
        return True
        
    """
    removes friend from users friend list
    """
    @classmethod
    def removeFriend(cls, userKey, friendKey):
        userKeyOb = ndb.Key(urlsafe=userKey)
        userOb = userKeyOb.get()
        
        #gets friend key object
        friendKeyOb = ndb.Key(urlsafe=friendKey)
        
        #tests if user has any friends
        try:
            userOb.friends = cls.remove_values_from_list(userOb.friends, friendKeyOb)
            userOb.put()
            #queries is 
            
        #user has no friends, so can't remove friend
        except:
            return True
    
    """
    returns a list of all the friends
    """
    @classmethod
    def getFriendKeys(cls,userKey):
        
        userKeyOb = ndb.Key(urlsafe=userKey)
        userOb = userKeyOb.get()
        try:
            return userOb.friends
        except:
            return False
    
    """
    returns array with user data for a given friend
    """
    @classmethod
    def getFriendInfo(cls,friendKeyOb):
        
        userOb = friendKeyOb.get()
        
        userName = userOb.userName
        email = userOb.email_address
        name = "Name goes here"
        
        return [userName, email, name, str(friendKeyOb)]
    
    """
    returns boolean to determine if user exists in DB and is logged in with token
    """
    @classmethod     
    def validateUser(cls, userName, authToken):    
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        
        #no user with that userName
        if not userOb:
            return False
        
        #validates token, returns object if true, false if not
        userTokenOb = userOb.validate_token(userOb.key.id(), 'auth', authToken)
        
        if userTokenOb is not None:
            return userOb.key.urlsafe()
        else:
            return False
    
    """
    helper method to remove item from list, used primarily to remove friend from friend list
    """
    @classmethod 
    def remove_values_from_list(cls, the_list, val):
        return [value for value in the_list if value != val]

from google.appengine.api import search
import logging
import utilities

"""
manages the documents, which are merely events. Dynamically updates with calls from api
"""
class DocumentManager():
    
    index = search.Index(name='events')
    
    """
    Adds event to doc with eventKey as doc id and name and description text fields to be searched
    """
    @classmethod
    def addEventDoc(cls, eventKey, name, description, privacySetting, userKey, startDate, endDate):
        
        
        event = search.Document(
                doc_id = eventKey,
                fields=[search.TextField(name='name', value = name),
                        search.TextField(name='description', value = description),
                        search.NumberField(name='privacySetting', value=privacySetting),
                        search.TextField(name='userKey', value=userKey),
                        search.DateField(name='startDate', value=startDate),
                        search.DateField(name='endDate', value=endDate)])
        
        # Index the document.
        try:
            cls.index.put(event)
            logging.info("event put into document into index")
        except search.PutError, e:
            result = e.results[0]
            if result.code == search.OperationResult.TRANSIENT_ERROR:
                # possibly retry indexing result.object_id
                pass
                
            pass
        except search.Error, e:
            # possibly log the failure
            pass
        
    
    """
    Removes event by eventKey (doc id)
    """ 
    @classmethod
    def removeEventDoc(cls, eventKey):
        
        cls.index.delete(eventKey)
        return True
    
        
    """
    Edits given event by eventKey
    """
    @classmethod
    def editEventDoc(cls, eventKey, name, description, privacySetting, startDate, endDate):
        
        event = cls.index.get(eventKey)
        
        if (name != ""):
            event.name = name
        if (description != ""):
            event.description = description
        if (privacySetting != ""):
            event.privacySetting = privacySetting
            
        #saves edited event
        try:
            cls.index.put(event)
            logging.info("event put into document into index")
        except search.PutError, e:
            result = e.results[0]
            if result.code == search.OperationResult.TRANSIENT_ERROR:
                # possibly retry indexing result.object_id
                pass
                
            pass
        except search.Error, e:
            # possibly log the failure
            pass
        
        return True

"""
actually parses queries
"""

class Search():
    
    index = search.Index(name='events')
            
    @classmethod
    def queryEvents(cls, string, date):
        
        
        """
        Need to add functionality to only search public events/your invited and private events
        """
        eventKeyList = []
        
        date = utilities.convertStringToSearchDate(date)
        
        #builds query string to search name and description
        queryString = "(name:\""+string+"\" OR description:\""+string+"\") AND (endDate >= "+date+" AND startDate <= "+date+")"
        
        #creates sort options
        sort_opts = search.SortOptions(match_scorer=search.MatchScorer())
        
        #creates query options based on sort options
        query_opts = search.QueryOptions(sort_options=sort_opts,returned_fields='doc_id')
        
        queryOb = search.Query(query_string = queryString, options=query_opts)
        
        try:
            results = cls.index.search(query=queryOb)
            
            for scored_events in results:
                logging.info(scored_events)
                eventKeyList.append(scored_events.doc_id)
                
        except search.Error, e:
            pass
        
        return eventKeyList
        
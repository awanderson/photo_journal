"""
This file contains helper functions that are used by multiple classes, mostly involving strings and dates
"""

from datetime import datetime

"""
Converts a string of the form "MONTH DATE, YEAR" to a Python DateTime object.
@param inputDate: an input string of the format MONTH DATE, YEAR
@return: a python DATETIME object corresponding to the input string
"""
def convertStringToDate(inputDate):
      
    newDateObject = datetime.strptime(inputDate, '%B %d, %Y')
    return newDateObject


"""
Converts a date back to a string for get methods, returns format MONTH DATE, YEAR
"""
def convertDateToString(inputDate):
    return inputDate.strftime('%B %d, %Y')


"""
Converts a string to another string that's properly formated for search in format YEAR-MONTH-DATE all in decimals
"""
def convertStringToSearchDate(inputDate):
    newDateObject = datetime.strptime(inputDate, '%B %d, %Y')
    return newDateObject.strftime('%Y-%m-%d')
    
    
"""
helper method that gets string and cleans it (capitalizes first letter of every word), reduces whitespace to a single space
"""
def cleanString(string):
    return ' '.join(word[0].upper() + word[1:] for word in string.split())

"""
helper method to remove item from list, used primarily to remove friend from friend list and pinned photos from pinned photos list
"""
def removeValuesFromList(the_list, val):
    return [value for value in the_list if value != val]
import json
import traceback

#def print_full_stack():
#    print('Traceback (most recent call last):')
#    for item in reversed(inspect.stack()[2:]):
#        print(' File "{1}", line {2}, in {3}\n'.format(*item),)
#    for line in item[4]:
#        print(' ' + line.lstrip(),)
#    for item in inspect.trace():
#        print(' File "{1}", line {2}, in {3}\n'.format(*item),)
#    for line in item[4]:
#        print(' ' + line.lstrip())

class AppException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg  = msg


        super(AppException, self).__init__()
        #print_full_stack()

    def errDict(self):
        return {'success': False,
                'error': {'code': self.code, 'message': self.msg}}

    def errDictWithEmptyData(self):
        return {'success': False, 'data':[],
                'error': {'code': self.code, 'message': self.msg}}

    def __repr__(self): return "[AppException %s] %s" \
                                % (self.code, self.msg)
    def __str__(self):  return self.__repr__()


class BadActivation(AppException):
    def __init__(self):
        super(BadActivation, self).__init__(400, 'Your account has already been activated.')

class BadActivationKey(AppException):
    def __init__(self):
        super(BadActivationKey, self).__init__(400, 'Invalid Set Password request. Please verify that the link you clicked is correct.')

class BadCookies(AppException):
    def __init__(self):
        super(BadCookies, self).__init__(403, "Access denied. Please clear your cookies and try again.")

class BadDemographicNum(Exception):
    def __init__(self):
        self.message = "The person requested does not exist."
        super(BadDemographicNum, self).__init__(self.message)

class BadEmail(AppException):
    def __init__(self):
        super(BadEmail, self).__init__(401, "The email and password combination you have provided is invalid.")

class BadEmailResetPassword(AppException):
    def __init__(self):
        super(BadEmailResetPassword, self).__init__(400, "That email address does not exist.")

class EmailUnauthorized(AppException):
    def __init__(self):
        super(EmailUnauthorized, self).__init__(401, "Your account has not yet been authorized by ClickMD. <br>You will receive an email when you are authorized and can begin using the system.")

class BadForm(AppException):
    def __init__(self):
        super(BadForm, self).__init__(400, "The form submitted is missing information.")

class BadPassword(AppException):
    def __init__(self):
        super(BadPassword, self).__init__(401, "The email and password combination you have provided is invalid.")

class BadProviderID(AppException):
    def __init__(self):
        super(BadProviderID, self).__init__(400, "The user requested does not exist.")

class DatabaseError(AppException):
    def __init__(self):
        super(DatabaseError, self).__init__(500, "There was an error connecting to the database.")

class EmailAlreadyExists(AppException):
    def __init__(self):
        super(EmailAlreadyExists, self).__init__(400, "That email already exists in our database!")

class ExpiredActivationKey(AppException):
    def __init__(self):
        super(ExpiredActivationKey, self).__init__(400, "Your activation key has expired.")

class InsertProviderRecordFailed(AppException):
    def __init__(self):
        super(InsertProviderRecordFailed, self).__init__(500, "The new user could not be created.")

class NotLoggedIn(AppException):
    def __init__(self):
        super(NotLoggedIn, self).__init__(401, "You are not logged in, access denied.")

class NotActive(AppException):
    def __init__(self):
        super(NotActive, self).__init__(400, "Your account email has not been verified. Please check your email for our activation link.")

class SetPasswordFailed(AppException):
    def __init__(self):
        super(SetPasswordFailed, self).__init__(500, "We were unable to set that password.")

class AccessDenied(AppException):
    def __init__(self):
        super(AccessDenied, self).__init__(403, "Access Denied.")



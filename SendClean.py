import logging
import os.path
import requests
import sys
import time
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

class Error(Exception):
    pass
class ValidationError(Error):
    pass
class InvalidKeyError(Error):
    pass

ERROR_MAP = {
    'ValidationError': ValidationError,
    'Invalid_Key': InvalidKeyError
}

logger = logging.getLogger('SendClean')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stderr))

class SendClean(object):
    def __init__(self, owner_id=None, apikey=None, appDomain=None, debug=False):

        self.session = requests.session()
        if debug:
            self.level = logging.INFO
        else:
            self.level = logging.DEBUG
        self.last_request = None

        if owner_id is None: raise Error('You must provide a SendClean Owner id')
        if apikey is None: raise Error('You must provide a SendClean Token')
        if appDomain is None: raise Error('You must provide a You must provide a SendClean TES DOMAIN')
        self.owner_id = owner_id
        self.apikey = apikey
        self.root='http://api.'+appDomain+'/v1.0/'

        self.messages = Messages(self)
        self.account = Account(self)
        self.settings = Settings(self)

    def call(self, url, params=None):
        '''Actually make the API call with the given params - this should only be called by the namespace methods - use the helpers in regular usage like m.tags.list()'''
        if params is None: params = {}
        params['owner_id'] = self.owner_id
        params['token'] = self.apikey
        params = json.dumps(params)
        self.log('POST to %s%s: %s' % (self.root, url, params))
        start = time.time()
        r = self.session.post('%s%s' % (self.root, url), data=params, headers={'content-type': 'application/json', 'user-agent': 'SendClean-Python/1.0.57'})
        try:
            remote_addr = r.raw._original_response.fp._sock.getpeername() # grab the remote_addr before grabbing the text since the socket will go away
        except:
            remote_addr = (None, None) #we use two private fields when getting the remote_addr, so be a little robust against errors

        response_body = r.text
        complete_time = time.time() - start
        self.log('Received %s in %.2fms: %s' % (r.status_code, complete_time * 1000, r.text))
        self.last_request = {'url': url, 'request_body': params, 'response_body': r.text, 'remote_addr': remote_addr, 'response': r, 'time': complete_time}

        result = json.loads(response_body)

        if r.status_code != requests.codes.ok:
            raise self.cast_error(result)
        return result

    def cast_error(self, result):
        '''Take a result representing an error and cast it to a specific exception if possible (use a generic SendClean.Error exception for unknown cases)'''
        if not 'status' in result or result['status'] != 'error' or not 'name' in result:
            raise Error('We received an unexpected error: %r' % result)

        if result['name'] in ERROR_MAP:
            return ERROR_MAP[result['name']](result['message'])
        return Error(result['message'])


    def log(self, * args, ** kwargs):
        '''Proxy access to the SendClean logger, changing the level based on the debug setting'''
        logger.log(self.level, * args, ** kwargs)

    def __repr__(self):
        return '<SendClean %s>' % self.apikey

class Messages(object):
    def __init__(self, master):
        self.master = master

    def sendMail(self, smtp_user_name=None, message=None):
        _params = {}
        if not smtp_user_name is None:
            _params['smtp_user_name'] = smtp_user_name

        if not message is None:
            _params['message'] = message

        return self.master.call('messages/sendMail', _params)
    def sendTemplate(self, smtp_user_name=None, message=None):
        _params = {}
        if not smtp_user_name is None:
            _params['smtp_user_name'] = smtp_user_name

        if not message is None:
            _params['message'] = message

        return self.master.call('messages/sendTemplate', _params) 

    def senRaw(self, smtp_user_name=None, raw_message=None):
        _params = {}
        if not smtp_user_name is None:
            _params['smtp_user_name'] = smtp_user_name

        if not raw_message is None:
            _params['raw_message'] = raw_message

        return self.master.call('messages/senRaw', _params)
    
    def getMessageInfo(self, x_unique_id=None, skip_page=None):
        _params = {}
        if not x_unique_id is None:
            _params['x_unique_id'] = x_unique_id

        if not skip_page is None:
            _params['skip_page'] = skip_page

        return self.master.call('messages/getMessageInfo', _params)




class Account(object):
    def __init__(self, master):
        self.master = master

    def viewUserDetail(self):
        _params = {}
        return self.master.call('account/viewUserDetail', _params)


class Settings(object):
    def __init__(self, master):
        self.master = master

    def listSmtp(self):
        _params = {}
        return self.master.call('settings/listSmtp', _params)


    def addSmtpUser(self, total_limit=None, hourly_limit=None):
        _params = {}
        if not total_limit is None:
            _params['total_limit'] = total_limit

        if not hourly_limit is None:
            _params['hourly_limit'] = hourly_limit

        return self.master.call('settings/listSmtp', _params)


    def editSmtp(self, smtp_user_name=None, total_limit=None, hourly_limit=None, status=None):
        _params = {}
        if not smtp_user_name is None:
            _params['smtp_user_name'] = smtp_user_name

        if not total_limit is None:
            _params['total_limit'] = total_limit

        if not hourly_limit is None:
            _params['hourly_limit'] = hourly_limit

        if not status is None:
            _params['status'] = status

        return self.master.call('settings/editSmtp', _params)

    def resetSmtpPassword(self, smtp_user_name=None):
        _params = {}
        if not smtp_user_name is None:
            _params['smtp_user_name'] = smtp_user_name

        return self.master.call('settings/resetSmtpPassword', _params)


    def addSendingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/addSendingDomain', _params)

    def deleteSendingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/deleteSendingDomain', _params)


    def checkSendingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/checkSendingDomain', _params)

    def verifySendingDomain(self, domain=None, mailbox=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        if not mailbox is None:
            _params['mailbox'] = mailbox

        return self.master.call('settings/verifySendingDomain', _params)


    def listSendingDomain(self):
        _params = {}
        return self.master.call('settings/listSendingDomain', _params)


    def addTrackingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/addTrackingDomain', _params)

    def deleteTrackingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/deleteTrackingDomain', _params)


    def checkTrackingDomain(self, domain=None):
        _params = {}
        if not domain is None:
            _params['domain'] = domain

        return self.master.call('settings/checkTrackingDomain', _params)

    def listTrackingDomain(self):
        _params = {}
        return self.master.call('settings/listTrackingDomain', _params)

    def addWebhook(self, url=None, event=None, description=None, store_log=None):
        _params = {}
        if not url is None:
            _params['url'] = url

        if not event is None:
            _params['event'] = event

        if not description is None:
            _params['description'] = description

        if not store_log is None:
            _params['store_log'] = store_log

        return self.master.call('settings/addWebhook', _params)


    def editWebhook(self, webhook_id=None, url=None, event=None, description=None, store_log=None):
        _params = {}

        if not webhook_id is None:
            _params['webhook_id'] = webhook_id

        if not url is None:
            _params['url'] = url

        if not event is None:
            _params['event'] = event

        if not description is None:
            _params['description'] = description

        if not store_log is None:
            _params['store_log'] = store_log

        return self.master.call('settings/editWebhook', _params)

    def deleteWebhook(self, webhook_id=None):
        _params = {}

        if not webhook_id is None:
            _params['webhook_id'] = webhook_id

        return self.master.call('settings/deleteWebhook', _params)

    def keyResetWebhook(self, webhook_id=None):
        _params = {}

        if not webhook_id is None:
            _params['webhook_id'] = webhook_id

        return self.master.call('settings/keyResetWebhook', _params)

    def listWebhook(self):
        _params = {}

        return self.master.call('settings/listWebhook', _params)
    
    def getWebhookInfo(self, webhook_id=None):
        _params = {}

        if not webhook_id is None:
            _params['webhook_id'] = webhook_id

        return self.master.call('settings/getWebhookInfo', _params)

from ckan.lib.navl.dictization_functions import Missing, StopOnError, Invalid

from ckan.common import _

import sys

import logging

log = logging.getLogger(__name__)
missing = Missing()

def identity_converter(key, data, errors, context):
    return

def keep_extras(key, data, errors, context):

    extras = data.pop(key, {})
    for extras_key, value in extras.iteritems():
        data[key[:-1] + (extras_key,)] = value

def not_missing(key, data, errors, context):

    value = data.get(key)
    if isinstance(value, Missing):
        errors[key].append(_('Missing value'))
        raise StopOnError

def not_empty(key, data, errors, context):

    value = data.get(key)
    if not value or isinstance(value, Missing):
        errors[key].append(_('Missing value'))
        raise StopOnError

def if_empty_same_as(other_key):

    def callable(key, data, errors, context):
        value = data.get(key)
        if not value or isinstance(value, Missing):
            data[key] = data[key[:-1] + (other_key,)]

    return callable


def both_not_empty(other_key):

    def callable(key, data, errors, context):
        value = data.get(key)
        other_value = data.get(key[:-1] + (other_key,))
        if (not value or isinstance(value, Missing) and
            not other_value or other_value is missing):
            errors[key].append(_('Missing value'))
            raise StopOnError

    return callable

def empty(key, data, errors, context):

    value = data.pop(key, None)
    
    if value and value is not missing:
        errors[key].append(_(
            'The input field %(name)s was not expected.') % {"name": key[-1]})

def ignore(key, data, errors, context):
    #TODO remove debug statement
    log.debug("ignore for key: {0}".format(key))
    data.pop(key, None)
    errors.pop(key, None)
    raise StopOnError

def default(defalult_value):

    def callable(key, data, errors, context):

        value = data.get(key)
        if not value or isinstance(value, Missing):
            data[key] = defalult_value

    return callable

def ignore_missing(key, data, errors, context):
    #TODO remove debug statement
    log.debug("ignore_missing before")
    value = data.get(key)

    if isinstance(value, Missing) or value is None:
        #TODO remove debug statement
        log.debug("ignore_missing detected key to ignore: {0}".format(key))
        data.pop(key, None)
        errors.pop(key, None)
        raise StopOnError

def ignore_empty(key, data, errors, context):
    #TODO remove debug statement
    log.debug("ignore_empty called")

    value = data.get(key)

    if isinstance(value, Missing) or not value:
        #TODO remove debug statement
        log.debug("ignore_empty detected key to ignore: {0}".format(key))
        data.pop(key, None)
        errors.pop(key, None)
        raise StopOnError

def convert_int(value, context):

    try:
        return int(value)
    except ValueError:
        raise Invalid(_('Please enter an integer value'))


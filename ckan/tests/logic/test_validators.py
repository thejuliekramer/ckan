import ckan.model as model
import ckan.logic.validators as v
import ckan.lib.navl.dictization_functions as df
import unittest

import logging

log = logging.getLogger(__name__)

class TestValidators(unittest.TestCase):
    def testTagStringConvert(self):
        def convert(tag_string):
            key = 'tag_string'
            data = {key: tag_string}
            errors = []
            context = {'model': model, 'session': model.Session}
            v.tag_string_convert(key, data, errors, context)
            tags = []
            i = 0
            while True:
                tag = data.get(('tags', i, 'name'))
                if not tag:
                    break
                tags.append(tag)
                i += 1
            return tags

        self.assertEqual(convert('big, good'), ['big', 'good'])
        self.assertEqual(convert('one, several word tag, with-hyphen'),
                     ['one', 'several word tag', 'with-hyphen'])
        self.assertEqual(convert(''),
                     [])
        self.assertEqual(convert('trailing comma,'),
                     ['trailing comma'])
        self.assertEqual(convert('trailing comma space, '),
                     ['trailing comma space'])

class TestPasswordValidators(unittest.TestCase):
    def testUserBothPasswordsEnteredPassesValidEntry(self):
        data = {
            'password1':'notempty',
            'password2':'alsonotempty'
        }

        schema = {
            'password1':[v.user_both_passwords_entered],
            #note, test will fail if no validator assigned to password2, as consequently the augment_data function
            #in dictization_functions.py will move said field into '__extras' or '__junk'
            'password2':[v.user_both_passwords_entered]
        }

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})
        self.assertEqual(converted_data, data)

    def testUserBothPasswordsEnteredForOrderIndependence(self):
        #Verify that validator works, even if it's declared on one, the other or both password fields
        data = {
            'password1':'',
            'password2':'notempty'
        }

        schema = {
            'password1':[v.user_both_passwords_entered]
        }

        converted_data, errors = df.validate(data, schema)

        self.assertEqual(errors, {'password1':[u'Please enter both passwords']})

        schema = {
            'password2':[v.user_both_passwords_entered]
        }

        converted_data, errors = df.validate(data, schema)

        self.assertEqual(errors, {'password2':[u'Please enter both passwords']})

        schema = {
            'password2':[v.user_both_passwords_entered],
            'password1':[v.user_both_passwords_entered]
        }

        converted_data, errors = df.validate(data, schema)

        self.assertEqual(errors, {'password1':[u'Please enter both passwords'],
                          'password2':[u'Please enter both passwords']})
        self.assertEqual(data, converted_data)

    def testUserPasswordNotEmptyIgnoresWhenPassword1Password2Present(self):
        """
        The function is kind of tricky here, but essentially, it says if password1 or password2 are present in
        the data dictionary, then don't check the 'password' field. This is because the function assumes that
        user_both_passwords_entered is assigned as a validator and will do the checking against password1 and password2
        """
        data = {
            'password1':'',
            'password2':'notempty',
            'password':'' #will not be checked
        }

        schema = {
            'password1':[v.user_password_not_empty]
        }

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})
        self.assertEqual(data, converted_data)

    def testUserPasswordNotEmpty(self):
        data = {
            'password':''
        }

        schema = {
            'password':[v.user_password_not_empty]
        }

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'password':[u'Missing value']})

        data['password']='notempty'

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})
        self.assertEqual(data, converted_data)
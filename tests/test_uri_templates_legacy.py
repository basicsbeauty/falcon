import ddt

import falcon
from falcon import routing
import falcon.testing as testing


@ddt.ddt
class TestUriTemplates(testing.TestBase):

    def test_string_type_required(self):
        self.assertRaises(TypeError, routing.compile_uri_template, 42)
        self.assertRaises(TypeError, routing.compile_uri_template, falcon.API)

    def test_template_must_start_with_slash(self):
        self.assertRaises(ValueError, routing.compile_uri_template, 'this')
        self.assertRaises(ValueError, routing.compile_uri_template, 'this/that')

    def test_template_may_not_contain_double_slash(self):
        self.assertRaises(ValueError, routing.compile_uri_template, '//')
        self.assertRaises(ValueError, routing.compile_uri_template, 'a//')
        self.assertRaises(ValueError, routing.compile_uri_template, '//b')
        self.assertRaises(ValueError, routing.compile_uri_template, 'a//b')
        self.assertRaises(ValueError, routing.compile_uri_template, 'a/b//')
        self.assertRaises(ValueError, routing.compile_uri_template, 'a/b//c')

    def test_root(self):
        fields, pattern = routing.compile_uri_template('/')
        self.assertFalse(fields)
        self.assertFalse(pattern.match('/x'))

        result = pattern.match('/')
        self.assertTrue(result)
        self.assertFalse(result.groupdict())

    @ddt.data('/hello', '/hello/world', '/hi/there/how/are/you')
    def test_no_fields(self, path):
        fields, pattern = routing.compile_uri_template(path)
        self.assertFalse(fields)
        self.assertFalse(pattern.match(path[:-1]))

        result = pattern.match(path)
        self.assertTrue(result)
        self.assertFalse(result.groupdict())

    def test_one_field(self):
        fields, pattern = routing.compile_uri_template('/{name}')
        self.assertEqual(fields, set(['name']))

        result = pattern.match('/Kelsier')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'name': 'Kelsier'})

        fields, pattern = routing.compile_uri_template('/character/{name}')
        self.assertEqual(fields, set(['name']))

        result = pattern.match('/character/Kelsier')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'name': 'Kelsier'})

        fields, pattern = routing.compile_uri_template('/character/{name}/profile')
        self.assertEqual(fields, set(['name']))

        self.assertFalse(pattern.match('/character'))
        self.assertFalse(pattern.match('/character/Kelsier'))
        self.assertFalse(pattern.match('/character/Kelsier/'))

        result = pattern.match('/character/Kelsier/profile')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'name': 'Kelsier'})

    @ddt.data('', '/')
    def test_two_fields(self, postfix):
        path = '/book/{id}/characters/{name}' + postfix
        fields, pattern = routing.compile_uri_template(path)
        self.assertEqual(fields, set(['name', 'id']))

        result = pattern.match('/book/0765350386/characters/Vin')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'name': 'Vin', 'id': '0765350386'})

    def test_three_fields(self):
        fields, pattern = routing.compile_uri_template('/{a}/{b}/x/{c}')
        self.assertEqual(fields, set('abc'))

        result = pattern.match('/one/2/x/3')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'a': 'one', 'b': '2', 'c': '3'})

    def test_malformed_field(self):
        fields, pattern = routing.compile_uri_template('/{a}/{1b}/x/{c}')
        self.assertEqual(fields, set('ac'))

        result = pattern.match('/one/{1b}/x/3')
        self.assertTrue(result)
        self.assertEqual(result.groupdict(), {'a': 'one', 'c': '3'})

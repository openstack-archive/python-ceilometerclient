import cStringIO
import sys
import unittest2

from ceilometerclient.common import utils


class UtilsTest(unittest2.TestCase):

    def test_prettytable(self):
        class Struct:
            def __init__(self, **entries):
                self.__dict__.update(entries)

        # test that the prettytable output is wellformatted (left-aligned)
        columns = ['ID', 'Name']
        val = ['Name1', 'another', 'veeeery long']
        images = [Struct(**{'id': i ** 16, 'name': val[i]})
                  for i in range(len(val))]

        saved_stdout = sys.stdout
        try:
            sys.stdout = output_dict = cStringIO.StringIO()
            utils.print_dict({'K': 'k', 'Key': 'Value'})

        finally:
            sys.stdout = saved_stdout

        self.assertEqual(output_dict.getvalue(), '''\
+----------+-------+
| Property | Value |
+----------+-------+
| K        | k     |
| Key      | Value |
+----------+-------+
''')

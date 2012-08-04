import os
import shutil
import subprocess
import tempfile
import unittest


class SimpleTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        count_1_upto_4_py = os.path.realpath(os.path.join(os.path.dirname(__file__), 'count_1_upto_4.py'))
        shutil.copy(count_1_upto_4_py, self.temp_dir)
        self.orig_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.orig_dir)
        shutil.rmtree(self.temp_dir)

    def test_check_ok(self):
        with open('Procfile', 'w') as procfile:
            procfile.write("count_1_upto_4: python count_1_upto_4.py")
            procfile.close()
            output = subprocess.check_output('honcho check', stderr=subprocess.STDOUT, shell=True)
            self.assertIn('Valid procfile detected', output)

    def test_check_empty(self):
        with open('Procfile', 'w') as procfile:
            # Empty Procfile
            procfile.close()

            try:
                output = subprocess.check_output('honcho check', stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                self.assertEquals(e.returncode, 1)
                self.assertIn('ERROR: No processes defined in Procfile', e.output)

    def test_check_invalid(self):
        with open('Procfile', 'w') as procfile:
            procfile.write("""foo bar dog""")
            procfile.close()

            try:
                output = subprocess.check_output('honcho check', stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                self.assertEquals(e.returncode, 1)
                self.assertIn('ERROR: No processes defined in Procfile', e.output)

    def test_start_simple_1(self):
        with open('Procfile', 'w') as procfile:
            procfile.write("count_1_upto_4: python count_1_upto_4.py")
            procfile.close()
            output = subprocess.check_output('honcho start', shell=True)
            self.assertIn('started with pid', output)
            self.assertIn('hello: 2', output)
            self.assertIn('hello: 2', output)
            self.assertIn('hello: 3', output)
            self.assertIn('hello: 4', output)


if __name__ == '__main__':
    unittest.main()

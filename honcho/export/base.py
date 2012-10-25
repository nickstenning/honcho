import os
import pwd
from honcho.command import CommandError, PATH
from jinja2 import Template

class BaseExport(object):
    def __init__(self, procfile, options, environment, concurrency):
        self.procfile = procfile
        self.options = options
        self.environment = environment
        self.concurrency = concurrency

        try:
            self.uid = pwd.getpwnam(options.user).pw_uid
        except KeyError:
            raise CommandError("No such user available: {}".format(
                    options.user))


    def _mkdir(self, directory):
        if os.path.exists(directory):
            return 
        try:
            os.makedirs(directory)
        except OSError, e:
            print e
            raise CommandError("Can not create {}".format(
                    directory))


    def _chown(self, filename):
        try:
            os.chown(filename, self.uid, self.uid)
        except OSError:
            raise CommandError("Can not chown {} to {}".format(
                    self.options.log,
                    self.options.user))


    def _write(self, filename, content):
        path = os.path.join(self.options.location, filename)
        
        try:
            open(path, 'w').write(content)
        except IOError:
            raise CommandError("Can not write to file {}".format(
                    path))

    def get_template(self, name):
        path = os.path.join(
            PATH,
            'data/export/',
            self.options.format,
            name)

        try:
            return Template(open(path).read())
        except IOError:
            raise CommandError("Can not find template with name {}".format(
                    name))
                     

    def export(self):
        self._mkdir(self.options.location)
        self._mkdir(self.options.log)
        self._chown(self.options.log)

        files = self.render(self.procfile, self.options, self.environment, self.concurrency)
        
        for name, content in files:
            self._write(name, content)

        return files

    def render(self, procfile, options, environment, concurrency):
        raise NotImplementedError("You must write a render method.")
            
            
            

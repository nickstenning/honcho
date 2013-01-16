import honcho
from honcho.export.base import BaseExport

class Export(BaseExport):
    def render(self, procfile, options, environment, concurrency):
        files = []

        context = {
            'app'         : options.app,
            'app_root'    : options.app_root,
            'environment' : environment,
            'log'         : options.log,
            'port'        : options.port,
            'user'        : options.user,
            'shell'        : options.shell}

        for name, cmd in procfile.commands.iteritems():
            ctx = context.copy()
            ctx.update({
                    'command' : cmd,
                    'name'    : name,})

            master  = "{}-{}.conf".format(options.app, name)
            files.append((master,  self.get_template("process_master.conf").render(ctx)))

            for num in xrange(1, concurrency[name]+1):
                ctx.update(num = num)
                process = "{}-{}-{}.conf".format(options.app, name, num)
                files.append((process, self.get_template("process.conf").render(ctx)))

        app = "{}.conf".format(options.app)

        files.append((app, self.get_template("master.conf").render(context)))

        return files

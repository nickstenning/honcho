from honcho import compat
from honcho.export.base import BaseExport


class Export(BaseExport):
    def render(self, procfile, options, environment, concurrency):
        files = []

        context = {
            'app':         options.app,
            'app_root':    options.app_root,
            'environment': environment,
            'log':         options.log,
            'port':        options.port,
            'user':        options.user,
            'shell':       options.shell
        }

        master_template = self.get_template('upstart/process_master.conf')
        process_template = self.get_template('upstart/process.conf')
        app_template = self.get_template('upstart/master.conf')

        for name, cmd in compat.iteritems(procfile.processes):
            ctx = context.copy()
            ctx.update({'command': cmd,
                        'name':    name})

            master = "{0}-{1}.conf".format(options.app, name)
            master_content = master_template.render(ctx)
            files.append((master, master_content))

            for num in compat.xrange(1, concurrency[name] + 1):
                ctx.update({'num': num})
                process = "{0}-{1}-{2}.conf".format(options.app, name, num)
                process_content = process_template.render(ctx)
                files.append((process, process_content))

        app = "{0}.conf".format(options.app)
        app_content = app_template.render(context)

        files.append((app, app_content))

        return files

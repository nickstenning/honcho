import pipes
from honcho import compat
from honcho.export.base import BaseExport


class Export(BaseExport):
    def render(self, procfile, options, environment, concurrency):
        commands = []
        port = options.port
        for name, cmd in procfile.commands.items():
            for num in compat.xrange(1, concurrency[name]+1):
                full_name_parts = [options.app, name]
                env = environment.copy()
                if concurrency[name] > 1:
                    env['PORT'] = str(port + num)
                    full_name_parts.append(str(num))
                else:
                    env['PORT'] = str(port)
                commands.append((
                    name,
                    cmd,
                    '-'.join(full_name_parts),
                    num,
                    [(key, '"%s"' % pipes.quote(value)) for key,value in env.items()] # quote env values
                ))
            port += 100

        context = {
            'app':         options.app,
            'app_root':    options.app_root,
            'log':         options.log,
            'port':        options.port,
            'user':        options.user,
            'shell':       options.shell,
            'commands':    commands,
            'concurrency': concurrency
        }
        filename = "{0}.conf".format(options.app)
        content = self.get_template("supervisord.conf").render(context)
        return [(filename, content)]

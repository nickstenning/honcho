import pipes
from honcho import compat
from honcho.export.base import BaseExport


class Export(BaseExport):
    def render(self, procfile, options, environment, concurrency):
        processes = []
        port = options.port
        for name, cmd in procfile.processes.items():
            for num in compat.xrange(0, concurrency[name]):
                full_name_parts = [options.app, name]
                env = environment.copy()
                if concurrency[name] > 1:
                    env['PORT'] = str(port + num)
                    full_name_parts.append(str(num))
                else:
                    env['PORT'] = str(port)
                processes.append((
                    name,
                    cmd,
                    '-'.join(full_name_parts),
                    num,
                    [(key, '"%s"' % pipes.quote(value)) for key, value in sorted(env.items())]  # quote env values
                ))
            port += 100

        context = {
            'app':         options.app,
            'app_root':    options.app_root,
            'log':         options.log,
            'port':        options.port,
            'user':        options.user,
            'shell':       options.shell,
            'processes':   processes,
            'concurrency': concurrency
        }
        filename = "{0}.conf".format(options.app)
        template = self.get_template('supervisord.conf', package='honcho')
        content = template.render(context)
        return [(filename, content)]

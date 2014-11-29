from itertools import groupby

from honcho.export.base import BaseExport
from honcho.export.base import dashrepl


class Export(BaseExport):
    def render(self, processes, context):
        master_tpl = self.get_template('upstart/master.conf')
        process_master_tpl = self.get_template('upstart/process_master.conf')
        process_tpl = self.get_template('upstart/process.conf')

        groups = groupby(processes, lambda p: p.name.split('.')[0])

        master = "{0}.conf".format(context['app'])
        yield master, master_tpl.render(context)

        for name, procs in groups:
            group_name = "{0}-{1}".format(context['app'], name)

            ctx = context.copy()
            ctx.update({'group_name': group_name})

            process_master = "{0}.conf".format(group_name)
            yield process_master, process_master_tpl.render(ctx)

            for p in procs:
                ctx = context.copy()
                ctx.update({'group_name': group_name,
                            'process': p})
                process = "{0}-{1}.conf".format(context['app'],
                                                dashrepl(p.name))
                yield process, process_tpl.render(ctx)

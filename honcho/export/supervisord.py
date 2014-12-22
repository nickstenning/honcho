from honcho.export.base import BaseExport


class Export(BaseExport):
    def render(self, processes, context):
        context['processes'] = processes
        filename = "{0}.conf".format(context['app'])
        template = self.get_template('supervisord/supervisord.conf')
        return [(filename, template.render(context))]

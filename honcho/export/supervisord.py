from honcho.export.base import BaseExport


class Export(BaseExport):
    default_template_dir = 'supervisord'

    def render(self, processes, context):
        context['processes'] = processes
        filename = "{0}.conf".format(context['app'])
        jinja2_template = self.get_template('supervisord.conf')
        return [(filename, jinja2_template.render(context))]

from honcho.export.base import BaseExport


class Export(BaseExport):
    def render(self, processes, context):
        context['processes'] = processes
        filename = "{0}.conf".format(context['app'])
        template_name = context.get('template') or 'supervisord/supervisord.conf'
        jinja2_template = self.get_template(template_name)
        return [(filename, jinja2_template.render(context))]

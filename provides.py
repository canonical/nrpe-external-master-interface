import datetime

from charmhelpers.core import hookenv
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class NrpeExternalMasterProvides(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:nrpe-external-master}-relation-{joined,changed}')
    def changed_nrpe(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:nrpe-external-master}-relation-{broken,departed}')
    def broken_nrpe(self):
        self.remove_state('{relation_name}.available')

    def add_check(self, args, name=None, description=None, context=None, unit=None):
        check_tmpl = """
#---------------------------------------------------
# This file is Juju managed
#---------------------------------------------------
command[%(check_name)s]=%(check_args)s
"""
        service_tmpl = """
#---------------------------------------------------
# This file is Juju managed
#---------------------------------------------------
define service {               
    use                             active-service                  
    host_name                       juju-%(unit_name)s
    service_description             %(description)s
    check_command                   check_nrpe!%(check_name)s
    servicegroups                   %(context)s
}
"""
        check_filename = "/etc/nagios/nrpe.d/%s.cfg" % (name)
        with open(check_filename, "w") as fh:
            fh.write(check_tmpl % {
                'check_args': ' '.join(args),
                'check_name': name,
            })
        service_filename = "/var/lib/nagios/export/service__%s_%s.cfg" % (unit, name)
        with open(service_filename, "w") as fh:
            fh.write(service_tmpl % {
                'context': context,
                'description': description,
                'check_name': name,
                'unit_name': unit,
            })


    def updated(self):
        relation_info = {
            'timestamp': datetime.datetime.now().isoformat(),
        }
        self.set_remote(**relation_info)
        self.remove_state('{relation_name}.available')

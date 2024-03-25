from flask_babel import Domain
from .. import translations

class AdminDomain(Domain):
    def __init__(self):
        super().__init__(translations.__path__[0], domain="admin")


admin_domain = AdminDomain()

gettext = admin_domain.gettext
ngettext = admin_domain.ngettext
lazy_gettext = admin_domain.lazy_gettext


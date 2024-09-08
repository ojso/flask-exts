from flask_babel import Domain
from .. import translations

class AdminDomain(Domain):
    def __init__(self):
        super().__init__(translations.__path__[0], domain="admin")


domain = AdminDomain()

_gettext = domain.gettext
_ngettext = domain.ngettext
_lazy_gettext = domain.lazy_gettext


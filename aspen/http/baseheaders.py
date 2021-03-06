from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from aspen.backcompat import CookieError, SimpleCookie

from aspen.http.mapping import CaseInsensitiveMapping
from aspen.utils import typecheck


class BaseHeaders(CaseInsensitiveMapping):
    """Represent the headers in an HTTP Request or Response message.
       http://stackoverflow.com/questions/5423223/how-to-send-non-english-unicode-string-using-http-header
       has good notes on why we do everything as pure bytes here
    """

    def __init__(self, d):
        """Takes headers as a dict or str.
        """
        typecheck(d, (dict, str))
        if isinstance(d, str):
            def genheaders():
                for line in d.splitlines():
                    k, v = line.split(b':', 1)
                    yield k.strip(), v.strip()
        else:
            genheaders = d.iteritems
        CaseInsensitiveMapping.__init__(self, genheaders)


        # Cookie
        # ======

        self.cookie = SimpleCookie()
        try:
            self.cookie.load(self.get('Cookie', b''))
        except CookieError:
            pass # XXX really?


    def __setitem__(self, name, value):
        """Extend to protect against CRLF injection:

        http://www.acunetix.com/websitesecurity/crlf-injection/

        """
        if '\n' in value:
            from aspen.exceptions import CRLFInjection
            raise CRLFInjection()
        super(BaseHeaders, self).__setitem__(name, value)


    def raw(self):
        """Return the headers as a string, formatted for an HTTP message.
        """
        out = []
        for header, values in self.iteritems():
            for value in values:
                out.append('%s: %s' % (header, value))
        return '\r\n'.join(out)
    raw = property(raw)

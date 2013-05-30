import datetime
from requests.sessions import Session as _Session
from webtest.app import TestApp as _TestApp
from wsgiproxy import HostProxy
from wsgiproxy.requests_client import HttpClient

from loads.util import dns_resolve


class TestApp(_TestApp):
    """A subclass of webtest.TestApp which uses the requests backend per
    default.
    """
    def __init__(self, app, session, test_result, *args, **kwargs):
        self.session = session
        self.test_result = test_result

        client = HttpClient(session=self.session)
        app = HostProxy(app, client=client)

        super(TestApp, self).__init__(app, *args, **kwargs)

    # XXX redefine here the _do_request, check_status and check_errors methods.
    # so we can actually use them to send information to the test_result


class Session(_Session):
    """Extends Requests' Session object in order to send information to the
    test_result.
    """

    def __init__(self, test, test_result):
        _Session.__init__(self)
        self.test = test
        self.test_result = test_result
        self.loads_status = None

    def send(self, request, **kwargs):
        """Do the actual request from within the session, doing some
        measures at the same time about the request (duration, status, etc).
        """
        request.url, original, resolved = dns_resolve(request.url)
        request.headers['Host'] = original

        # attach some information to the request object for later use.
        start = datetime.datetime.utcnow()
        res = _Session.send(self, request, **kwargs)
        res.started = start
        res.method = request.method
        self._analyse_request(res)
        return res

    def _analyse_request(self, req):
        """Analyse some information about the request and send the information
        to the test_result.

        :param req: the request to analyse.
        """
        loads_status = self.loads_status or (None, None, None)
        if self.test_result is not None:
            self.test_result.add_hit(elapsed=req.elapsed,
                                     started=req.started,
                                     status=req.status_code,
                                     url=req.url,
                                     method=req.method,
                                     loads_status=list(loads_status))

from helper_functions import request_helper
from helper_functions import core_link_format_helper

from database import DB
from coapthon.resources.resource import Resource
import logging
logger = logging.getLogger("log")


class LookupResource(Resource):
    """
    Lookup resource, which is accessbile via:
     - /rd-lookup/ep for device discovery
     - /rd-lookup/res for service discovery
    """
    def __init__(self, lookup_table, name="LookupResource", coap_server=None):
        super(LookupResource, self).__init__(name, coap_server, visible=True,
                                             observable=True, allow_children=True)
        self.lookup_table = lookup_table

    def render_GET(self, request):
        if request.source[0] != "127.0.0.1":
            logger.info("CoAP RD: GET to /rd-lookup from {host}:{port}".format(host=request.source[0], port=request.source[1]))
        res = LookupResource(self.lookup_table)
        query_parameters = request_helper.get_query_parameter(request)
        if len(query_parameters) == 0:
            res.payload = DB.DB.lookup_all(self.lookup_table)
        else:
            res.payload = DB.DB.lookup_with_parameter(self.lookup_table, query_parameters)
        return res




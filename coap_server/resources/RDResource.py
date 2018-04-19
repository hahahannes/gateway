from coapthon.resources.resource import Resource
from helper_functions import core_link_format_helper, device_translator, request_helper
from database import DB
import logging
from connector_client.connector import client, device

logger = logging.getLogger("log")

class RDResource(Resource):
    """
    Main resource directory class for endpoint /rd.
    Registration, Updates and Removal requests are sent to this endpoint.
    """
    def __init__(self, name="RDResource", coap_server=None):
        super(RDResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.db = DB.DB()

    def render_POST(self, request):
        logger.info("RD: POST to /rd from {host}:{port}".format(host=request.source[0], port=request.source[1]))
        print(request.pretty_print())
        logger.info("RD: Payload: {payload}".format(payload=request.payload))
        res = RDResource()
        if request.payload:
            informations = {
                "host": request.source[0],
                "port": request.source[1],
                "query_parameters": request_helper.get_query_parameter(request),
                "links": core_link_format_helper.parse_links(request.payload),
            }
            ep = informations.get("query_parameters").get("ep")

            if not DB.DB.endpoint_exists(ep):  # todo check ip change
                DB.DB.create(informations)
                logger.info('RD: Endpoint not found -> created in local db and register on platform')
                id = DB.DB.get_endpoint_id(ep)
                device = DB.DB.get(id)
                res.location_path = "/rd/{id}".format(id=id) # todo nicht da in respone
                client.Client.add(device)
            else:
                logger.info("RD: Endpoint exists -> return found id")
                # todo reconnect by Client.add() ?
                res.location_path = "/rd/" + str(DB.DB.get_endpoint_id(ep))
            return res

    def render_DELETE(self, request):
        logger.info("RD: DELETE to /rd from {host}:{port}".format(host=request.source[0], port=request.source[1]))
        DB.DB.remove_endpoint()
        device = device_translator.convert_to_device_instance(informations)
        client.Client.delete(device)
        return True
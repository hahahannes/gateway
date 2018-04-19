from coapthon.server.coap import CoAP
from coap_server.resources import WKResource,RDResource,UpdateResource,LookupResource
import threading

class CoAPMulticastServer(CoAP,threading.Thread):
    """
    Server class, where the API endpoints gets appended
    Multicast:
    coap://224.0.1.187:5683/rd
    coap://224.0.1.187:5683/rd-lookup/ep
    Unicast:
    coap://127.0.0.1/5683
    """
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), multicast=True)
        threading.Thread.__init__(self)
        self.add_resource('.well-known/core/', WKResource.WKResource())
        self.add_resource('rd/', RDResource.RDResource())
        self.add_resource('rd-lookup/ep/', LookupResource.LookupResource("endpoints"))
        self.add_resource('rd-lookup/res/', LookupResource.LookupResource("resources"))

    def run(self):
        while True:
            self.listen(10)




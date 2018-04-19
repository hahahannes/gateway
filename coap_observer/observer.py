from coapthon.client.helperclient import HelperClient
import threading
import time
from helper_functions import core_link_format_helper, request_helper
from database import DB
from connector_client.connector import device, client
import logging
import datetime
import json

logger = logging.getLogger("log")


class CoAPDiscovery(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db = DB.DB()
        self.observed_devices = []

    def handle_observe_response(self, response, id=None):
        if id and response:
            device = DB.DB.get(id)
            service = ""
            payload = response
            client.Client.event(device, service, payload)

    def diff(self, known, unknown):
        new_devices = set(unknown) - set(known)
        deleted_devices = set(known) - set(unknown)
        return new_devices, deleted_devices

    def check_observations(self):
        localhost_client = HelperClient(("127.0.0.1", 5683))
        current_devices = localhost_client.get("lookup/ep?status=1")
        new_devices, deleted_devices = self.diff(self.observed_devices, current_devices)

        for device in new_devices:
            localhost_client.observe(device.get("path", callback=self.handle_observe_response(id=device.get("id"))))
            self.observed_devices.append(device)

        for device in deleted_devices:
            localhost_client.cancel_observing(device.get("path", self.handle_observe_response(id=device.get("id"))))
            self.observed_devices.remove(device)

    def run(self):
        # Get data via CoAP Observe request
        # self.check_observations()

        # Get data via frequently GET requests (maybe as fallback if observe is not supported)
        while True:
            time.sleep(30)
            localhost_client = HelperClient(("127.0.0.1", 5683))

            # Observe all sensor resources # todo id und status von endpoint bei join mitnehmen
            services_of_connected_devices = localhost_client.get("lookup/res?status=1&if=core.s")
            for device in services_of_connected_devices:
                id = device.get("id")
                url = request_helper.parse_url(device.get("path"))
                logger.info(
                    "OBSERVER: Perform GET to: {host}:{port} with id: {id}".format(host=url.hostname, port=url.port,
                                                                                   id=id))
                device_client = HelperClient((url.hostname, url.port))
                response = None

                try:
                    response = device_client.get(url.path)
                    device = DB.DB.get(id)
                except Exception as e:
                    logger.error("OBSERVER: GET was not successful")

                if response:
                    try:
                        # Data Type of platoform contain data and metadata 
                        # structure of data has to be defined in the service output parameter
                        client.Client.event(device, service=url.path, data=json.dumps(response.payload))
                    except Exception as e:
                        logger.error("OBSERVER: Send data to platform was not successful")

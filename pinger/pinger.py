import time
import sys
from socket import *
from coapthon.client.helperclient import HelperClient
import time
from helper_functions import core_link_format_helper,request_helper
from database import DB
import threading
from connector_client.connector import client
import logging
logger = logging.getLogger("log")

class Pinger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def ping(self, host, port=5683):
        client = HelperClient(server=(host, port))
        response = client.get("", timeout=3)
        return response # None if no response in timeout

    def run(self):
        while True:
            #todo die disconnected auf connected umstellen wenn wieder da,
            # allles auf connected stellen wenn nicht eh schon auf connected

            time.sleep(10)
            local_coap_client = HelperClient(server=("127.0.0.1", 5683))
            response = local_coap_client.get("/rd-lookup/ep")

            if response.payload:
                known_devices = core_link_format_helper.parse_links(response.payload)
                # ping unicast instead of multicast, dont know if the device listens on multicast

                missing_devices = []
                reconnected_devices = []
                for device in known_devices:
                    url = request_helper.parse_url(device.get("path"))
                    device_was_connected = None
                    print(device)

                    if device.get("status") == '1':
                        device_was_connected = True
                    elif device.get("status") == '0':
                        device_was_connected = False

                    is_online = self.ping(url.hostname,url.port)
                    if not is_online and device_was_connected:
                        missing_devices.append(device)

                    if is_online and not device_was_connected:
                        reconnected_devices.append(device)

                for device in missing_devices:
                    id = device.get("id")
                    logger.info("PINGER: device {id} is not online -> disconnect".format(id=id))
                    device = DB.DB.get(id)
                    try:
                        client.Client.disconnect(device)
                        logger.info("PINGER: device {id} was disconnected from RD and platform".format(id=id))
                    except Exception as e:
                        logger.error("PINGER: device {id} was not successful disconnected".format(id=id))
                        logger.error(e)

                for device in reconnected_devices:
                    id = device.get("id")
                    logger.info("PINGER: device {id} is online -> reconnect".format(id=id))
                    device = DB.DB.get(id)
                    try:
                        # For reconnect, use add() - maybe connect() better ?
                        client.Client.add(device)
                        logger.info("PINGER: device {id} was added to platform".format(id=id))
                    except Exception as e:
                        logger.error("PINGER: device {id} was not successful added to platform".format(id=id))

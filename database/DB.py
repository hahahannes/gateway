import sqlite3
from helper_functions import core_link_format_helper
import logging
logger = logging.getLogger("log")


class DB(singleton.SimpleSingleton):
    """
    Datbase class, for SQL execution on a SQLite file.
    """
    _db_path = 'devices.sqlite'
    _devices_table = 'endpoints'
    _services_table = 'services'

    def __init__(self):
        self._executeQuery("""CREATE TABLE IF NOT EXISTS endpoints(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ep VARCHAR(100),
              et VARCHAR(100),
              host VARCHAR(100),
              status INTEGER,
              port INTEGER
          )""")
        self._executeQuery("""CREATE TABLE IF NOT EXISTS resources(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title VARCHAR(100),
              path VARCHAR(100),
              d VARCHAR(100),
              rt VARCHAR(100),
              gp VARCHAR(100),
              belongs_to_endpoint INTEGER,
              FOREIGN KEY(belongs_to_endpoint) REFERENCES endpoint(id) ON DELETE CASCADE
          )""")

    @staticmethod
    def _executeQuery(query):
        try:
            db_conn = sqlite3.connect(__class__._db_path)
            cursor = db_conn.cursor()
            cursor.execute(query)
            if any(statement in query for statement in ('CREATE', 'INSERT', 'DELETE', 'UPDATE')):
                db_conn.commit()
                result = True
            else:
                result = cursor.fetchall()
            db_conn.close()
            return result
        except Exception as ex:
            logger.error(ex)
            return False

    @staticmethod
    def endpoint_exists(endpoint_name):
        query = """
                SELECT * FROM endpoints
                WHERE ep = '{endpoint_name}'
                """

        results = DB._executeQuery(query.format(endpoint_name=endpoint_name))
        return len(results) != 0

    @staticmethod
    def get_endpoint_id(endpoint_name):
        logger.info("Database Module: get endpoint id")

        query = """
                SELECT * FROM endpoints
                WHERE ep = '{endpoint_name}'
                """

        results = DB._executeQuery(query.format(endpoint_name=endpoint_name))
        if results:
            return str(results[0][0])
        else:
            return False

    def update(self, informations):
        pass

    @staticmethod
    def create(device):
        logger.info("DB: add device to RD")

        # todo get from dict wenn nicht vorhanden
        query_parameters = device.get('query_parameters')
        links = device.get('links')
        host = device.get('host')
        port = device.get('port')
        endpoint_name = query_parameters.get('ep')

        if endpoint_name:
            # Insert into endpoints db
            query = """INSERT INTO endpoints (ep, et, host, port, status) VALUES(
                                '{ep}', '{et}', '{host}', '{port}', 1
                                )
                            """
            DB._executeQuery(query.format(ep=endpoint_name, et=query_parameters['et'], host=host,
                                      port="5683"))
            logger.info("Database Module: endpoint added")

            endpoint_id = DB.get_endpoint_id(endpoint_name)
            # Insert into resource db
            for resource in links:
                query = """INSERT INTO resources (path, title, rt, gp, d, belongs_to_endpoint) VALUES(
                                    '{path}', '{title}', '{rt}', '{gp}', '{d}', '{belongs_to_endpoint}'
                                )"""
                DB._executeQuery(query.format(path=resource.get("path", ""), title=resource.get('title', ""),
                                                rt=resource.get('rt', ""), gp=resource.get('gp', ""),
                                                d=resource.get('d', ""), belongs_to_endpoint=endpoint_id))

            return True
        else:
            return False
            logger.info("Database Module: Endpoint name is missing")

    @staticmethod
    def add(device):
        # for reconnect client.add calls this method
        DB.update_status(device.id, 1)


    def delete_from_db(self,id):
        logger.info("DB: remove device to RD")

        query = """
                DELETE FROM endpoints 
                WHERE id = {id}
                """
        DB._executeQuery(query.format(id=id))
        return ""

    @staticmethod
    def get(id):
        query = """
                SELECT * FROM endpoints
                WHERE id = {id}
                """.format(id=id)
        result = DB._executeQuery(query)
        if result:
            result = result[0]
            new_device = device.Device(str(result[0]), result[2], result[1])
            return new_device
        else:
            return None

    def lookup_with_parameter(self, table, parameters):
        query = "SELECT * FROM resources WHERE"

        for parameter in parameters:
            query += " " + parameter + " LIKE '%" + parameters[parameter] + "%'"
        result = self._executeQuery(query)

        for r in result:
            resource_informations = {}
            resource_informations["parameters"] = {}
            resource_informations["parameters"]["title"] = r["title"]
            resource_informations["parameters"]["rt"] = r["rt"]
            resource_informations["parameters"]["d"] = r["d"]
            resource_informations["parameters"]["gp"] = r["gp"]
            belongs_to_endpoint = r["belongs_to_endpoint"]
            result_endpoint = self.execute(
                """SELECT * FROM endpoints WHERE id = {id}""".format(id=belongs_to_endpoint))

            resource_informations["path"] = "coap://" + result_endpoint[0]["host"] + ":" + str(
                result_endpoint[0]["port"]) + r["path"]

    def lookup_all(table):
        resources = []

        if table == "resources":
            result = DB._executeQuery("""SELECT * FROM resources""")
            for r in result:
                resource_informations = {}
                resource_informations["parameters"] = {}
                resource_informations["parameters"]["title"] = r["title"]
                resource_informations["parameters"]["rt"] = r["rt"]
                resource_informations["parameters"]["d"] = r["d"]
                belongs_to_endpoint = r["belongs_to_endpoint"]
                result_endpoint = DB._executeQuery(
                    """SELECT * FROM endpoints WHERE id = {id}""".format(id=belongs_to_endpoint))
                resource_informations["path"] = "coap://" + result_endpoint[0]["host"] + ":" + str(
                    result_endpoint[0]["port"]) + r["path"]
                resources.append(resource_informations)

        elif table == "endpoints":
            result = DB._executeQuery("""SELECT * FROM endpoints""")
            for r in result:
                resource_informations = {}
                resource_informations["parameters"] = {}
                resource_informations["parameters"]["title"] = r[2]
                resource_informations["parameters"]["et"] = r[1]
                resource_informations["parameters"]["id"] = str(r[0])
                resource_informations["path"] = "coap://" + r[3] + ":" + str(r[5])
                resource_informations["parameters"]["status"] = r[4]
                resources.append(resource_informations)

        return core_link_format_helper.generate_link(resources)

    @staticmethod
    def remove(device_id):
        logger.info("DB: disconnect device to RD")
        DB.update_status(device_id, 0)

    def update_status(id, status):
        logger.info("DB: update device status")
        query = 'UPDATE {table} SET status = {status} WHERE id == {id}'.format(id=str(id),status=str(status),table=__class__._devices_table)
        print(query)
        DB._executeQuery(query)

    @staticmethod
    def devices() -> dict:
        query = 'SELECT * FROM {table}' \
                'WHERE status = 1'.format(
            table=__class__._devices_table
        )
        result = DB._executeQuery(query)
        devices = dict()
        if result:
            for r in result:
                device = device.Device(str([0]), r[2], r[1])
                devices[device.id] = device
        return devices

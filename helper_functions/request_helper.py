import urllib
def get_query_parameter(request):
    # use python shortcut to create list
    query_parameters = {}
    parsed_query = urllib.parse.parse_qs(request.uri_query)
    for parameter in parsed_query:
        query_parameters[parameter] = parsed_query[parameter][0]
    return query_parameters

def parse_url(url):
    return urllib.parse.urlparse(url)


def generate_uri(ip, paths, parameters={}):
    """
    Generates an URI based on the protocol, the ip/hostname, multiple paths and parameters
    """

    uri = 'coap://' + ip
    for path in paths:
        uri += path
    #todo if parameters set ? only
    return uri + '?' + urllib.urlencode(parameters)



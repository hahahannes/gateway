"""
CoRE Link Format (RFC6690) functions
"""


def generate_link(resources):
    """
    Generates a link in the CoRE Link Format (RFC6690).
    :param resources: Array of resources that should translated into links.
                      Resources are dict, containing a path property and a parameters property.
                      Path is a string and parameters is a dict, containing the parameters and their values.
    """

    links = ""
    for i, resource in enumerate(resources):
        link = "<" + resource["path"] + ">"
        if "parameters" in resource:
            for parameter in resource["parameters"]:
                link += ";" + str(parameter) + "=" + str(resource["parameters"][parameter])
        links += link
        if i != len(resources) - 1:
            links += ","
    return links


def parse_links(links):
    links = links.split(",")
    link_list = []
    for link in links:
        link_as_dict = {}
        values = link.split(";")
        for i, value in enumerate(values):
            if i == 0:
                value = value.replace("<", "")
                value = value.replace(">", "")
                link_as_dict['path'] = value
            else:
                parameter, value = value.split("=")
                link_as_dict[parameter] = value
        link_list.append(link_as_dict)
    return link_list
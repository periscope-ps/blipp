from utils import clean_mac

def mac_match(geni_port, local_port):
    try:
        geni_mac = clean_mac(geni_port['properties']['geni']['mac_address'])
    except KeyError:
        try:
            geni_mac = clean_mac(geni_port['properties']['mac']['address'])
        except KeyError:
            return False
    try:
        local_mac = clean_mac(local_port['properties']['mac']['address'])
    except KeyError:
        return False
    return local_mac == geni_mac

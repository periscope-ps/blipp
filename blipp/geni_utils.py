from utils import clean_mac

def mac_match(geni_port, local_port):
    geni_mac = clean_mac(geni_port['properties']['geni']['mac_address'])
    local_mac = clean_mac(local_port['properties']['mac']['address'])
    return local_mac == geni_mac

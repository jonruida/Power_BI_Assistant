from mitmproxy import io
from mitmproxy.exceptions import FlowReadException
import pprint
import sys

# Abre el archivo de salida en modo escritura
with open(sys.argv[2], "w", encoding="utf-8") as outfile:
    # Redirige stdout a outfile
    sys.stdout = outfile
    
    with open(sys.argv[1], "rb") as logfile:
        freader = io.FlowReader(logfile)
        pp = pprint.PrettyPrinter(indent=4)
        try:
            for f in freader.stream():
                print(f)
                print(f.request.host)
                pp.pprint(f.get_state())
                print("")
        except FlowReadException as e:
            print("Flow file corrupted: {}".format(e))

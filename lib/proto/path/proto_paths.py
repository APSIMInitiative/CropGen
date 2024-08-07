import sys
import os

# This is a convenience python file to setup the paths for the autogen directory so that we can
# easily include proto files. Without this, when proto files include other proto files it doesn't 
# find them.
proto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib', 'autogen'))
if proto_path not in sys.path:
    sys.path.append(proto_path)

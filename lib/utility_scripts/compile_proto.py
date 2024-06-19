import os
import shutil
import subprocess
import sys

# Check if the protoc compiler is available
if not shutil.which('protoc'):
    print("Error: protoc compiler not found. Please install it and ensure it's in your PATH.")
    sys.exit(1)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the source and destination directories relative to the script directory
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'cgm.messages', 'cgm.protobuf.messages', 'Proto'))
dst_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'autogen'))

# Ensure the destination directory exists, delete contents if it does, create if it doesn't
if os.path.exists(dst_dir):
    shutil.rmtree(dst_dir)
os.makedirs(dst_dir)

# Iterate over all .proto files in the source directory
for root, _, files in os.walk(src_dir):
    for file in files:
        if file.endswith('.proto'):
            proto_file = os.path.join(root, file)
            subprocess.run(['protoc', f'-I={src_dir}', f'--python_out={dst_dir}', proto_file])

print(f"All .proto files from {src_dir} have been compiled and copied to {dst_dir}")

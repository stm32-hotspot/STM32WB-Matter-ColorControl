# Copyright(c) 2024 STMicroelectronics International N.V.
# Copyright 2017 Linaro Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import struct
import json
import argparse
import subprocess
import tempfile
import os
import re
import ssl
from enum import Enum, auto

class dataType(Enum):
    INT8 = 1
    INT16 = auto()
    INT32 = auto()
    STRING = auto()
    ARRAY8 = auto()
    
class flashingType(Enum):
    DATAFACTORY = 1
    M4 = auto()
    M0 = auto()

class cryptoType(Enum):
    CERT = 1
    PUBLIC = auto()
    PRIVATE = auto()

# Dictionary to map names to types and IDs
name_map = {
    # DeviceAttestationCredentialsProvider 
    "CERTIFICATION_DECLARATION": {"type": dataType.ARRAY8, "id": 1},
    "FIRMWARE_INFORMATION": {"type": dataType.ARRAY8, "id": 2},
    "DEVICE_ATTESTATION_CERTIFICATE": {"type": dataType.ARRAY8, "id": 3},
    "PAI_CERTIFICATE": {"type": dataType.ARRAY8, "id": 4},
    "DEVICE_ATTESTATION_PRIV_KEY": {"type": dataType.ARRAY8, "id": 5},
    "DEVICE_ATTESTATION_PUB_KEY": {"type": dataType.ARRAY8, "id": 6},
    # CommissionableDataProvider
    "SETUP_DISCRIMINATOR": {"type": dataType.INT16, "id": 11},
    "SPAKE2_ITERATION_COUNT": {"type": dataType.INT32, "id": 12},
    "SPAKE2_SALT": {"type": dataType.ARRAY8, "id": 13},
    "SPAKE2_VERIFIER": {"type": dataType.ARRAY8, "id": 14},
    "SPAKE2_SETUP_PASSCODE": {"type": dataType.INT32, "id": 15},
    # DeviceInstanceInfoProvider
    "VENDOR_NAME": {"type": dataType.STRING, "id": 21},
    "VENDOR_ID": {"type": dataType.INT16, "id": 22},
    "PRODUCT_NAME": {"type": dataType.STRING, "id": 23},
    "PRODUCT_ID": {"type": dataType.INT16, "id": 24},
    "SERIAL_NUMBER": {"type": dataType.STRING, "id": 25},
    "MANUFACTURING_DATE": {"type": dataType.STRING, "id": 26},
    "HARDWARE_VERSION": {"type": dataType.INT16, "id": 27},
    "HARDWARE_VERSION_STRING": {"type": dataType.STRING, "id": 28},
    "ROTATING_DEVICE_ID": {"type": dataType.STRING, "id": 29},
    # Platform specific
    "TAG_ID_ENABLE_KEY": {"type": dataType.STRING, "id": 41}
}

paramToName = {key.lower().replace("_", ""): key for key, value in name_map.items()}

# Define ANSI escape codes for text formatting
RED = '\033[91m'       # Red text
GREEN = '\033[92m'     # Green text
YELLOW = "\033[1;33m"  # Yellow text
BLUE = '\033[94m'      # Blue text
MAGENTA = "\033[1;35m" # Magenta text
CYAN = "\033[1;36m"    # Cyan text
RESET = '\033[0m'      # Reset text color to default

# Function to convert value from decimal or hexadecimal format
def convert_value(value):
    # Check if the value starts with "0x"
    if value.startswith("0x"):
        # If it does, assume it's a hexadecimal number and convert it using base 16
        return int(value, 16)
    else:
        # If it doesn't start with "0x", assume it's a decimal number and convert it using base 10
        return int(value)

def bytes_to_hex_string(my_bytes, format_specifier):
    # Convert the bytes object to an integer
    my_int = int.from_bytes(my_bytes, byteorder='little')
    
    # Convert the integer to a hexadecimal string with the specified format specifier
    my_hex_string = format(my_int, format_specifier)
    
    return ("0x" + my_hex_string, my_int)


def displayChangedValue(data_dict, who, name, id, value, format=None):
    # Define a separator string to use in output messages
    sep = '  '
    
    # Check if the format parameter is 'string'
    if format == 'string':
        # Check if the id parameter is in the data_dict dictionary
        if id in data_dict:
            # Check if the value associated with the id key has changed
            if data_dict[id][0] != value:
                # Print a message indicating that the value has changed
                print(f"{sep}{who} changed {CYAN}{name}{RESET} from {data_dict[id][0]} to {value}")
            else:
                print(f"{sep}{who} set value for existing {CYAN}{name}{RESET} with no change : {value}")
        else:
            # Print a message indicating that a new value has been set
            print(f"{sep}{who} set value for {CYAN}{name}{RESET}: {value}")
    
    # Check if the format parameter is 'none'
    elif format == 'none':
        if id in data_dict:
            # Check if the value associated with the id key has changed
            if data_dict[id][0] != value:
                # Print a message indicating that the value has changed
                print(f"{sep}{who} changed {CYAN}{name}{RESET} from\n{data_dict[id][0]}\nto\n{value}")
            else:
                print(f"{sep}{who} set value for existing {CYAN}{name}{RESET} with no change :\n{value}")
        else:
            # Print a message indicating that a new value has been set
            print(f"{sep}{who} set value for {CYAN}{name}{RESET}:\n{value}")
    
    # If the format parameter is not 'string' or 'none'
    else:
        # Check if the id parameter is in the data_dict dictionary
        if id in data_dict:
            # Convert the old and new values to a hex string plus decimal string using the bytes_to_hex_string() function
            old, old_dec = bytes_to_hex_string(data_dict[id][0], format)
            new, new_dec = bytes_to_hex_string(value, format)
            # Check if the old and new values are different
            if old != new:
                # Print a message indicating how the value has changed
                print(f"{sep}{who} changed {CYAN}{name}{RESET} from {old} ({old_dec}) to {new} ({new_dec})")
            else:
                print(f"{sep}{who} set value for existing {CYAN}{name}{RESET} with no change : {new} ({new_dec})")
        else:
            # Convert the new value to a hex string using the bytes_to_hex_string() function
            new, new_dec = bytes_to_hex_string(value, format)
            # Print a message indicating that a new value has been set
            print(f"{sep}{who} set value for {CYAN}{name}{RESET} : {new} ({new_dec})")

def fillData(name, value, data_dict, who):
    try:
        id = name_map[name]["id"]
        type = name_map[name]["type"]
    except KeyError:
        print(f"{RED}  {who} can't set value for {name}: {value}.\n{name} is an unknown parameter{RESET}")
        return
    #print(f"  Name: {name}, ID: {id}, Type: {type}")
    # Convert value to appropriate type
    if type == dataType.INT8: 
        value = convert_value(value)
        value = struct.pack("B", value)
        displayChangedValue(data_dict, who, name, id, value, '02x')
    elif type == dataType.INT16:
        value = convert_value(value)
        value = struct.pack("<H", value)
        displayChangedValue(data_dict, who, name, id, value, '04x')
    elif type == dataType.INT32:
        value = convert_value(value)
        value = struct.pack("<I", value)
        displayChangedValue(data_dict, who, name, id, value, '08x')
    elif type == dataType.ARRAY8:
        value = bytes(int(x, 16) for x in value)
        displayChangedValue(data_dict, who, name, id, value, 'none')
    elif type == "float":
        value = float(value)
        value = struct.pack("<f", value)
    elif type == "bool":
        value = bool(value)
        value = struct.pack("<?", value)
    else:
        value = str(value).encode("utf-8")
        displayChangedValue(data_dict, who, name, id, value, 'string')
    # Add ID/value/type tuple to dictionary
    data_dict[id] = (value, type, name)
    #print(f"  Name: {name}, ID: {id}, Type: {type}, Value: {value}")

def removeData(name, data_dict, who):
    id = name_map[name]["id"]
    print(f"  {who} removed {CYAN}{name}{RESET}")
    data_dict.pop(id, None)
    return data_dict

# Function to read JSON file and fill data_dict
# Open JSON file for reading
# Each item in the data array represents a TLV
# The ID field is a unique identifier for the TLV
# The type field specifies the data type of the value
# Possible types are: int8, int16, int32, string
# The value field contains the value of the TLV
# The name field is an optional field that provides a human-readable name for the TLV

def read_json_file(file_path, data_dict):

    # Open JSON file for reading
    try:
        with open(file_path, "r") as f:
            # Load JSON data
            data = json.load(f)
    except FileNotFoundError:
        print(f"{RED}Error: JSON file {file_path} not found{RESET}")
        return None
    except json.JSONDecodeError:
        print(f"{RED}Error: JSON file {file_path} is not a valid JSON file{RESET}")
        return None
    
    # Loop through JSON data
    # for item in data["data"]:
    #     # Extract name, value, and optional ID from item
    #     name = item["name"]
    #     value = item["value"]
    for name, value in data.items():
        #print(name, ":", value)
        #print(f"  To be filled :  Name: {name}, Value: {value}")
        #print(f"  To be filled :  Name: {name}")
        fillData(name, value, data_dict, "Read Json")    
    return data_dict

def writeJson(data_dict, file_path):
    """
    Converts a dictionary of TLVs (Type-Length-Value) to JSON format and writes it to a file.

    Args:
        data_dict (dict): A dictionary of TLVs where the keys are IDs and the values are tuples of (value, type, name).
        file_path (str): The path to the output JSON file.

    Returns:
        None
    """
    # List to store TLVs
    tlv_list = []
    
    # Loop through TLVs in data_dict
    #print (data_dict)
    for id, (value, type, name) in data_dict.items():
        # Convert value to appropriate format for JSON
        if type == dataType.INT8:
            value = struct.unpack('b', value)[0]
            value = str(value)
        elif type == dataType.INT16:
            value = int.from_bytes(value, byteorder='little')
            value = str(value)
        elif type == dataType.INT32:
            value = value = struct.unpack('<i', value)[0]
            value = str(value)
        elif type == "float":
            value = float(value)
        elif type == "bool":
            value = bool(value)
        elif type == dataType.STRING:
            value = value.decode('utf-8')
        elif type == dataType.ARRAY8:
            # Convert uint8_array to hex string format
            hex_strings = [f'0x{byte:02x}' for byte in value]
            # Combine hex strings into groups of 14
            #hex_groups = [hex_strings[i:i+14] for i in range(0, len(hex_strings), 14)]
            # Join hex strings in each group with a comma and space
            #value = [', '.join(group) for group in hex_groups]

            value = hex_strings
        else:
            value = str(value)
        
        # Add TLV to list
        tlv_list.append((id, name, value))
    
    # Sort TLV list by ID
    tlv_list = sorted(tlv_list, key=lambda x: x[0])
    
    # Create JSON dictionary without ID
    json_dict = {}
    for _, name, value in tlv_list:
        json_dict[name] = value
    
    # Write JSON data to file
    try:
        with open(file_path, "w") as f:
            json.dump(json_dict, f, indent=4)
        print(f"{GREEN}Write to Json file {file_path} successful{RESET}")
    except IOError as e:
        print(f"{RED}Write to Json file {file_path} return ERROR -->{RESET}")
        print(e)

# Function to write data_dict to binary file
def writeBinary(data_dict, file_path):
    # Sort data_dict by ID
    data_dict = dict(sorted(data_dict.items()))

    # Open binary file for writing
    try:
        with open(file_path, "wb") as f:
            # Loop through ID/value/type tuples
            for id, (value, _, _) in data_dict.items():
                # Verify that value does not exceed length
                length = len(value)
                # Convert ID to 32-bit binary format in native byte order
                id_bin = struct.pack("I", id)
                # Convert length to 32-bit binary format in little-endian byte order
                len_bin = struct.pack("<I", length)
                # Write TLV to binary file
                f.write(id_bin + len_bin + value)
            print(f"{GREEN}Write to binary file{file_path} successful{RESET}")
            return 0
    except IOError as e:
        print(f"{RED}Write to binary file {file_path} return ERROR -->{RESET}")
        print(e)
        return 1

# This function reads a binary file containing TLVs and returns a dictionary data_dict containing
# the TLVs and their values. The TLVs are identified by their unique IDs and contain values of
# different data types such as integers, floats, strings, and booleans. The function uses the struct
# module to unpack the binary data based on the data type specified in the name_map dictionary.
# The resulting dictionary can be used to access the TLVs and their values.
def readBinary(file_path, data_dict):
    # Open binary file for reading
    try:
        f = open(file_path, "rb")
    except FileNotFoundError:
        print(f"{RED}Error: binary file {file_path} not found{RESET}")
        return None

    # Loop through binary data
    while True:
        # Read ID (4 bytes)
        id_bin = f.read(4)
        if not id_bin:
            # End of file
            break
        # Convert ID from binary to integer
        id = struct.unpack("I", id_bin)[0]
        
        # Read length (4 bytes)
        len_bin = f.read(4)
        # Convert length from binary to integer
        length = struct.unpack("<I", len_bin)[0]
        
        # Read value (length bytes)
        value_bin = f.read(length)
        
        # Determine data type based on ID
        if id in [v["id"] for v in name_map.values()]:
            # Get name of TLV from name_map dictionary
            name = [k for k, v in name_map.items() if v["id"] == id][0]
            # Get data type from name_map dictionary
            type = name_map[name]["type"]
            # Unpack value based on data type
            if type == dataType.INT8:
                value = struct.unpack("b", value_bin)[0]
                displayChangedValue(data_dict, "Read binary", name, id, value_bin, '02x')
            elif type == dataType.INT16:
                value = struct.unpack("<h", value_bin)[0]
                displayChangedValue(data_dict, "Read binary", name, id, value_bin, '04x')
            elif type == dataType.INT32:
                value = struct.unpack("<i", value_bin)[0]
                displayChangedValue(data_dict, "Read binary", name, id, value_bin, '08x')
            elif type == "float":
                value = struct.unpack("<f", value_bin)[0]
            elif type == "bool":
                value = struct.unpack("<?", value_bin)[0]
            elif type == dataType.STRING:
                value = value_bin.decode("utf-8")
                displayChangedValue(data_dict, "Read binary", name, id, value_bin, 'string')
            else:
                value = value_bin
                displayChangedValue(data_dict, "Read binary", name, id, value_bin, 'none')
            # Add ID/value/type tuple to dictionary
            value = value_bin
            data_dict[id] = (value, type, name)
            #print(f"  Name: {name}, ID: {id}, Type: {type}, Value: {value}")
        else:
            print(f"{RED}  Read binary Type {id} incorrect, this value will be skipped{RESET}")
    f.close()
    return data_dict

def flashBinary(binaryFile, flashAddr, programmer_path, external_loader_path, external_loader, type):
            
    # Construct the command to flash the binary file to the specified address
    command = [
        programmer_path + "\\STM32_Programmer_CLI.exe", "-c", "port=SWD", "mode=UR", "-el", external_loader_path + "\\" + external_loader + ".stldr",
        "-d", binaryFile, flashAddr, "-V", "-rst"
    ]
    if type == flashingType.M4:
        displayStr = "M4 firmware"
    elif type == flashingType.M0:
        command = [
                programmer_path + "\\STM32_Programmer_CLI.exe", "-c", "port=SWD", "mode=UR",
                "-ob nSWboot0=0 nboot1=1 nboot0=1", "-startfus",
                "-fwupgrade", binaryFile, flashAddr, "-V"
            ]
        displayStr = "M0 firmware"
    else:
        displayStr = "data factory"

    # Run the command using check_output()
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        # Print a message indicating that the binary file was successfully flashed to the specified address
        print(f"{GREEN}Flash {displayStr} file {binaryFile} to address {flashAddr} successful{RESET}")
    except subprocess.CalledProcessError as e:
        # Print an error message if the flashing failed and print the output of the command
        print(f"{RED}Flash {displayStr} file {binaryFile} to address {flashAddr} returned ERROR -->{RESET}")
        print(e.output)
        
        # Reset the board
        if type == flashingType.M0:
            command = [programmer_path + "\\STM32_Programmer_CLI.exe", "-c",  "port=swd",  "mode=UR", "-ob nSWboot0=1 nboot1=1 nboot0=1", "-rst"]
        else:
            command = [programmer_path + "\\STM32_Programmer_CLI.exe", "-c", "port=SWD", "mode=UR", "-rst"]
        subprocess.run(command)

def readFlash(flashAddr, length, programmer_path, external_loader_path, external_loader, data_dict):
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp_file:
        # Use the temporary file
        # The temporary file will be automatically deleted when the 'with' block ends
        print("  Temporary file name:", tmp_file.name)

        binaryOut = tmp_file.name
        # Construct the command to read the binary file from the specified address
        command = [
            programmer_path + "\\STM32_Programmer_CLI.exe", "-c", "port=SWD", "mode=UR", "-el", external_loader_path + "\\" + external_loader + ".stldr",
            "-r " + flashAddr, str(length), "\"" + binaryOut + "\"", "-rst"
        ]
        # print (command)
        # Run the command using check_output()
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            # Print a message indicating that the binary file was successfully read frem the specified address
            print(f"{GREEN}Read flash from address {flashAddr} successful{RESET}")
            print(f"{BLUE}Read from temporary binary file {binaryOut}...{RESET}")
            retValue = readBinary(binaryOut, data_dict)
            
            if retValue is not None:
                print(f"{GREEN}Read from temporary binary file {binaryOut} successful{RESET}")
                toBeReturn = retValue
            else:
                toBeReturn = data_dict
        except subprocess.CalledProcessError as e:
            # Print an error message if the reading failed and print the output of the command
            print(f"{RED}Read flash from address {flashAddr} returned ERROR -->{RESET}")
            print(e.output.decode("utf-8"))
            
            # Reset the board
            command = [programmer_path + "\\STM32_Programmer_CLI.exe", "-c", "port=SWD", "mode=UR", "-rst"]
            subprocess.run(command)
            toBeReturn =  data_dict

    os.remove(binaryOut)
    return toBeReturn

def read_certificate(cert_file, type):
    """
    Reads a PEM-encoded SSL/TLS certificate file and returns its contents as a byte array.

    Args:
        cert_file (str): The path to the PEM-encoded certificate file.

    Returns:
        bytearray: A byte array containing the contents of the certificate file.
    """
    sep = '  '
    extension = os.path.splitext(cert_file)[1]
    try:
        if extension == ".pem":
            # Load the certificate file as plain text
            with open(cert_file, 'r') as f:
                cert_data = f.read()
            # Extract the certificate data using a regular expression
            if type == cryptoType.CERT:
                cert_match = re.search(r'(-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----)', cert_data, re.DOTALL)
                stringType = 'Certificate'
            elif type == cryptoType.PRIVATE :
                cert_match = re.search(r'(-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----)', cert_data, re.DOTALL)
                stringType = 'Private key'
            elif type == cryptoType.PUBLIC :
                cert_match = re.search(r'(-----BEGIN PUBLIC KEY-----.*-----END PUBLIC KEY-----)', cert_data, re.DOTALL)
                stringType = 'Public key'
            else:
                cert_match = False
                stringType = 'Unknown type'

            if cert_match:
                cert_data = cert_match.group(1).strip()
            else:
                raise ValueError(f'{stringType} data not found in file {cert_file}')
            # Convert the certificate to a byte array
            cert = ssl.PEM_cert_to_DER_cert(cert_data)
            byte_array = bytearray(cert)
        
        elif extension == ".der":
            with open(cert_file, 'rb') as f:
                byte_array = bytearray(f.read())
        
        else:
            raise ValueError(f'extension {extension} of {cert_file} is not known') 
        
        # Return the byte array
        return [f"0x{b:02x}" for b in byte_array]

    except FileNotFoundError:
        print(f"{sep}{RED}Error: File '{cert_file}' not found.{RESET}")
        return None

    except ssl.SSLError as e:
        print(f"{sep}{RED}Error: Failed to read certificate file '{cert_file}': {e}.{RESET}")
        return None

    except ValueError as e:
        print(f"{sep}{RED}Error: {e}.{RESET}")
        return None

    except Exception as e:
        print(f"{sep}{RED}Error: Failed to read certificate file '{cert_file}': {e}.{RESET}")
        return None
    
def display_help(parser):
    """
    Display the help message for the script.

    Args:
        parser: The argparse.ArgumentParser object.

    Returns:
        None
    """
    print(parser.format_help())
    exit()

# Main function
def main():
    programmer_path = "c:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin"
    programmer = "STM32_Programmer_CLI.exe"
    external_loader_path = programmer_path + "\\" + "ExternalLoader"
    external_loader = "S25FL128S_STM32WB5MM-DK"
    M4_address = "0x08000000"

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-jsonIn", "-ji",
                        help="JSON input file path")
    parser.add_argument("-jsonOut", "-jo",
                        help="JSON output file path",
                        type=str)
    parser.add_argument("-binaryIn", "-bi",
                        help="Binary input file path. If jsonIn and binaryIn are set, Json input file "+\
                        "will be read first, and then Binary input file will be read, eventualy overriding jsin input file values")
    parser.add_argument("-binaryOut", "-bo",
                        help="Binary output file path")
    parser.add_argument("-flashIn", "-fi",
                        help="Input data are read from flash from this address. Will override data read from "+\
                        "Json input file or binary input file")



    parser.add_argument("-certificationdeclaration", "-cd",
                        help=" set path for certification declaration pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-firmwareinformation", "-fw",
                        help=" set path for certification declaration pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-deviceattestationcertificate", "-dc",
                        help=" set path for device attestation certificate pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-paiCertificate", "-pc",
                        help=" set path for PAI certification pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-deviceattestationprivkey", "-dr",
                        help=" set path for device attestation private key pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-deviceattestationpubkey", "-dp",
                        help=" set path for device attestation public key pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)    



    parser.add_argument("-hardwareVersion", "-hv",
                        help=" set value for hardware version. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-hardwareVersionString", "-hs",
                        help=" set value for hardware version string. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-productName", "-pd",
                        help="set value for product name. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-productID", "-pi",
                        help="set value for product ID. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-setupDiscriminator", "-sd",
                        help="set value for setup discriminator. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-spake2IterationCount", "-si",
                        help="set value for spake2 iteration count. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-spake2salt", "-ss",
                        help=" set path for spake2 salt pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-spake2verifier", "-sv",
                        help=" set path for spake2 verifier pem or der file. Override value read from Json or binary file, or read from board's flash.",
                        type=str)    
    parser.add_argument("-spake2SetupPasscode", "-sp",
                        help="set value for spake2 setup passcode. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-vendorName", "-vn",
                        help="set value for vendor name. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-vendorId", "-vi",
                        help="set value for vendor ID. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-serialNumber", "-sn",
                        help="set value for serial number. Override value read from Json or binary file, or read from board's flash.",
                        type=str)
    parser.add_argument("-remove", "-rm",
                        help="name of parameter to be removed from any requested output. ex : -remove productID",
                        type=str,
                        action='append')
    parser.add_argument("-flashM4", "-m4",
                        help="Path to the M4 firmware to be flashed in the board at address " + M4_address + ". " +\
                            "Flashing the M4 firmware is the very first action done or just after M0 flashing." )
    parser.add_argument("-M4Addr", "-4a",
                        help="Address wher the M4 firmware is flashed. if not set, " + M4_address + " will be used")
    parser.add_argument("-flashM0", "-m0",
                        help="Path to the M0 firmware to be flashed in the board at address defined by -M0Addr option. " +\
                            "Flashing the M0 firmware is the very first action done." )
    parser.add_argument("-M0Addr", "-0a",
                        help="Address wher the M4 firmware is flashed. No default value. Mansatory if -flashM0 option is used.")
    parser.add_argument("-flashAddr", "-fa",
                        help="Flash the bin output file (if generated) to this address. If not set, binary output file won't be flashed")
    parser.add_argument("-programmerPath", "-pp",
                        help="Path to STM32CubeProgrammer. If not set, " + programmer_path + " will be used. Used if option flashIn or flashAddr is set.")
    parser.add_argument("-externalLoader", "-el",
                        help="External loader file to use. If not set, " + external_loader + " will be used. External loader is in this folder : " +\
                            external_loader_path +" . Used if option flashIn or flashAddr is set.")
    parser.add_argument("-showHelp", "-sh",
                        action="store_true",
                        help="Show this help message and exit")
    args = parser.parse_args()

    if args.showHelp:
        display_help(parser)

    # Dictionary to store TLVs
    data_dict = {}

    if args.M4Addr is not None:
        M4_address =  args.M4Addr

    if args.programmerPath is not None:
        programmer_path =  args.programmerPath

    if args.externalLoader is not None:
        external_loader =  args.externalLoader

    if args.flashM0 is not None:
        if args.M0Addr is not None:
            print(f"{BLUE}Flashing M0 firmware {args.flashM0} to address {args.M0Addr} ...{RESET}")
            flashBinary(args.flashM0, args.M0Addr, programmer_path, external_loader_path, external_loader, flashingType.M0)
        else:
            print(f"{RED}Flashing M0 firmware {args.flashM4} is missing M0 firmware flash address. use -M0Addr option to set address.{RESET}")

    if args.flashM4 is not None:
        print(f"{BLUE}Flashing M4 firmware {args.flashM4} to address {M4_address} ...{RESET}")
        flashBinary(args.flashM4, M4_address, programmer_path, external_loader_path, external_loader, flashingType.M4)

    if args.jsonIn is not None:
        print(f"{BLUE}Read from Json file {args.jsonIn}...{RESET}")
        # Read JSON file and fill data_dict
        retValue = read_json_file(args.jsonIn, data_dict)
        if retValue is not None:
            print(f"{GREEN}Read from Json file {args.jsonIn} successful{RESET}")
            data_dict = retValue
    
    if args.binaryIn is not None:
        print(f"{BLUE}Read from binary file {args.binaryIn}...{RESET}")
        retValue = readBinary(args.binaryIn, data_dict)
        if retValue is not None:
            print(f"{GREEN}Read from binary file {args.binaryIn} successful{RESET}")
            data_dict = retValue
        
    if args.flashIn is not None:
        print(f"{BLUE}Read from flash address {args.flashIn}...{RESET}")
        data_dict = readFlash(args.flashIn, 2048, programmer_path, external_loader_path, external_loader, data_dict)

    print(f"{BLUE}Analyze cli parameters (if any)...{RESET}")
    # Parse parameters corresponding to data factory data and add to data_dict
    for attr in dir(args):
        if (not attr.startswith('_')) and (getattr(args, attr) is not None) and (attr.lower() in paramToName):
            value = getattr(args, attr)
            if attr.lower() == "certificationdeclaration" or \
               attr.lower() == "firmwareinformation" or \
               attr.lower() == "deviceattestationcertificate" or \
               attr.lower() == "paicertificate" or \
               attr.lower() == "spake2salt" or \
               attr.lower() == "spake2verifier":
                value = read_certificate(getattr(args, attr), cryptoType.CERT)
            elif attr.lower() == "deviceattestationprivkey":
                value = read_certificate(getattr(args, attr), cryptoType.PRIVATE)
            elif attr.lower() == "deviceattestationpubkey":
                value = read_certificate(getattr(args, attr), cryptoType.PUBLIC)
            # print(f'{attr}: {getattr(args, attr)} --- {paramToName[attr.lower()]} -> {getattr(args, attr)}')
            if value is not None:
                fillData(paramToName[attr.lower()], value, data_dict, "Cli parameter")
            else:
                print(f"    {RED}ERROR on cli parameter {CYAN}-{attr}{RED}.{RESET}")

    if args.remove is not None:
        for remove_arg in args.remove:
            toRemove = remove_arg.lower()
            if(toRemove in paramToName):
                data_dict = removeData(paramToName[toRemove], data_dict, "Cli parameter")
            else:
                print(f"  Cli parameter can't remove {remove_arg}. {RED}Invalid value {remove_arg}{RESET}")

    print(f"{GREEN}Analyze cli parameters (if any) end{RESET}")

    # Sort data_dict by ID
    data_dict = dict(sorted(data_dict.items()))

    if args.jsonOut is not None:
        print(f"{BLUE}Write to Json file {args.jsonOut}...{RESET}")
        # Write data_dict to JSON file
        writeJson(data_dict, args.jsonOut)
    
    if args.binaryOut is not None:
        print(f"{BLUE}Write to binary file {args.binaryOut}...{RESET}")
        # Write data_dict to JSON file
        retValue = writeBinary(data_dict, args.binaryOut)
    
        # Check if the flash address is specified
        if args.flashAddr is not None:
            if retValue == 0:
                # Print a message indicating that the binary file is being flashed to the specified address
                print(f"{BLUE}Flashing data factory file {args.binaryOut} to address {args.flashAddr} ...{RESET}")
                flashBinary(args.binaryOut, args.flashAddr, programmer_path, external_loader_path, external_loader, flashingType.DATAFACTORY)
            else:
                print(f"{RED}Flashing data factory file {args.binaryOut} to address {args.flashAddr} Impossible "+\
                    f"as binary data factory file can't be written{RESET}")


if __name__ == "__main__":
    main()
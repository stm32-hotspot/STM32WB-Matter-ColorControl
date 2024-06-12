# -*- coding: utf-8 -*-

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

"""
    @file    CreateMatterBin.py
    @author  Matter Team
    @brief   Create Matter binary file by assembling header + M4 binary + M0 binary.

    Python 3 is required.

    How to use:
    Launch the scripts with 2 mandatory arguments : 
        -m4 followed by full path to M4 binary (mandatory)
        -m0 followed by full path to M0 binary (optional)
        -o followed by output bin (optional)

    You can use -h or --help to display help.

    Example:
    python.exe .\CreateMatterBin.py -m4 c:\MATTER\path_to_M4_bin\M4.bin -m0 c:\MATTER\path_to_M0_bin\M0.bin

    If successful, Matter binary file is created in script directory.

    note: 
    In the current version, the -m4 option is mandatory. If the M0 image is not updated, you must 
    provide an empty file (size = 0) for -m0
"""

import os
import struct
import argparse

CreateMatterBin_about_name = "CreateMatterBin"
CreateMatterBin_about_version = "v1.0"
CreateMatterBin_about_date = "2024-03-21"

DEFAULT_OUTPUT_MATTER_BIN = "MatterM4M0.bin"

# #################################################################
#  make_bin function
#  Create Matter binary files made of:
#   - Header
#   - M4 binary file
#   - M0 binary file (optional)
# Return code : 0 if success
# #################################################################
def make_bin(file_path_M4, file_path_M0, file_path_Matter):

    # Read M4 bin content
    try:
        M4BinarySize = os.path.getsize(file_path_M4)
        with open(file_path_M4,'rb') as f:
            dataM4 = f.read()
            f.close()
    except:
        print("Error opening M4 binary")
        return(1)    
     
    # Read M0 bin content  
    if file_path_M0:
        try:
            M0BinarySize = os.path.getsize(file_path_M0)                
            with open(file_path_M0,'rb') as f:
                dataM0 = f.read()
                f.close()
        except:
            print("Error opening M0 binary")
            return(1)     
    else:
        # if no M0 bin provided, uses an empty M0 bin 
        M0BinarySize = 0
        dataM0 = b''

    print("*** M4 binary ***")
    print(file_path_M4)    
    print("size: ", M4BinarySize)
    print("*** M0 binary ***")
    print(file_path_M0)    
    print("size: ", M0BinarySize)

    # Create the header
    print("*** MATTER binary ***")
    Header = struct.pack("II", M4BinarySize, M0BinarySize)
    print("Header = ", Header)

    # Write Matter bin content   
    try:        
        with open(file_path_Matter,'wb') as f:
            f.write(Header + dataM4 + dataM0)
            f.close()
            print("Output= ", file_path_Matter)
    except:
        print("Error during binary creation")
        return(1)      

    # success
    return(0) 

# #################################################################
#  parse_input_args function
#  This function parse input arguments
#  Returns: M4_path, M0_path
# #################################################################
def parse_input_args():
    # arguments parsing
    parser = argparse.ArgumentParser(description='Parmaters parsing')
    parser.add_argument('-m4', type=str,
                        help='full path to M4 bin file')
    parser.add_argument('-m0', type=str,
                        help='full path to M0 bin file', default=None)
    parser.add_argument('-o', type=str,
                        help='output bin file name')

    args = parser.parse_args()

    return args.m4, args.m0, args.o  

# #################################################################
#  main function
# #################################################################
def main():

    print("< create Matter bin started >")
    # parse input arguments
    M4_path, M0_path, output_bin = parse_input_args()

    if output_bin is None:
        output_bin = DEFAULT_OUTPUT_MATTER_BIN

    if M4_path:
        # all mandatory args are present, create the Matter bin
        ret = make_bin(M4_path, M0_path, output_bin)  
        if ret != 0:
            print("Matter binary creation failed.")
        else:
            print("Matter binary created.")  
    else:
        # missing mandatory args
        print("Error, argument -m4 is mandatory.")

# #################################################################
#  Entry point
# #################################################################
if __name__ == '__main__':

    """ Main starts here """
    main()
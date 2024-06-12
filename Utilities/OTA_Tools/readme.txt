
##################################
#  Tools ans scripts for Matter  #
##################################


==============================================================================
CreateMatterBin.py
==============================================================================
origin: STMicroelectronics

description: 
Create Matter binary file by assembling (header + M4 binary or sfb + M0 binary).

note: 
Only -m4 option is mandatory.
If the M0 image is not updated, do not specify -m0 option. The script will use an empty M0 binary in this case.
The output binary will use a default name if -o option is not used.

usage examples:
python ./CreateMatterBin.py --help
python ./CreateMatterBin.py -m4 myapp-SBSFU.sfb -m0 stm32wb5x_BLE_Thread_ForMatter_fw.bin -o myMatterM4M0-fw.bin
python ./CreateMatterBin.py -m4 myapp-SBSFU.sfb 


==============================================================================
ota_image_tool.py
==============================================================================
origin: Project chip
can be found in connectedhomeip\src\app\ota_image_tool.py

note: 
The version of the script corresponds to the version of Matter (formerly Project CHIP) used for the X-Cube Matter.
The version can be found in the top release note, in root directory, of the X-Cube Matter.

description: 
Matter OTA (Over-the-air update) image utility.
This script can be used to: Create OTA image, Show OTA image info, Remove the OTA header from an image file or 
Change the specified values in the header.
 
note:
To work outside of CHIP environment, this script requires to use functions from chip.tlv
The following tree is required by the script. It comes from connectedhomeip\src\controller\python\chip\tlv
   [chip]
        __init__
        [tlv]
            __init__

usage examples:
python ./ota_image_tool.py --help
python ./ota_image_tool.py create -v <VENDOR_ID> -p <PRODUCT_ID> -vn <VERSION> -vs <VERSION_STRING> -da sha256 my-firmware.bin my-firmware.ota
python ./ota_image_tool.py create -v 0xDEAD -p 0xBEEF -vn 1 -vs "1.0" -da sha256 my-firmware.bin my-firmware.ota


==============================================================================
ST_ota_image_tool.py
==============================================================================
origin: STMicroelectronics

description: 
This script is an overlay of the script ota_image_tool.py
The <VENDOR_ID>, <PRODUCT_ID>, <VERSION> and <VERSION_STRING> parameters are extracted from the specified CHIPProjectConfig.h file.

note:
The script ota_image_tool.py and the [chip] directory are required to execute this script.

usage examples:
python ./ST_ota_image_tool.py --help
python ./ST_ota_image_tool.py -cc <full_path>/CHIPProjectConfig.h my-firmware.bin my-firmware.ota


==============================================================================
ST_MFT.py
==============================================================================
origin: STMicroelectronics

description: 
This script launches a Graphic User Interface for CreateMatterBin.py and ota_image_tool.py

note:
The script ota_image_tool.py and the [chip] directory are required to execute this script.
The script ST_ota_image_tool.py is required to execute this script.
The PySimpleGui python library is required.

usage examples:
python ./ST_MFT.py




#pragma once

#define CHIP_FUZZING_ENABLED 0
#define CHIP_CONFIG_TEST 0


#define CHIP_CONFIG_SHORT_ERROR_STR 0
#define CHIP_CONFIG_ENABLE_ARG_PARSER 0
#define CHIP_TARGET_STYLE_UNIX 0
#define CHIP_TARGET_STYLE_EMBEDDED 1
#define HAVE_MALLOC 0
#define HAVE_FREE 0
#define HAVE_NEW 0
#define CHIP_CONFIG_MEMORY_MGMT_SIMPLE 0
#define CHIP_CONFIG_MEMORY_DEBUG_CHECKS 0
#define CHIP_CONFIG_MEMORY_DEBUG_DMALLOC 0
#define CHIP_CONFIG_PROVIDE_OBSOLESCENT_INTERFACES 0


#define CHIP_CONFIG_MAX_ACTIVE_CHANNELS 8  // default 16
#define CHIP_CONFIG_MAX_CHANNEL_HANDLES 16 // default 32
#define CHIP_CONFIG_MAX_EXCHANGE_CONTEXTS 8 // default 16
//#define CHIP_CONFIG_MAX_FABRICS 5
#define CHIP_CONFIG_MAX_INTERFACES 4 // value not defined
#define CHIP_CONFIG_MAX_PEER_NODES 16 // default 128
#define CHIP_CONFIG_MAX_UNSOLICITED_MESSAGE_HANDLERS 8 // default 8
#define CHIP_DEVICE_CONFIG_MAX_EVENT_QUEUE_SIZE 25 // default 100

#define CHIP_CONFIG_TRANSPORT_TRACE_ENABLED 0


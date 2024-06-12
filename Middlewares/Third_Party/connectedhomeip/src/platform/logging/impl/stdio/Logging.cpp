/* See Project CHIP LICENSE file for licensing information. */

#include <lib/support/EnforceFormat.h>
#include <lib/support/logging/Constants.h>
#include <platform/logging/LogV.h>

#include <stdio.h>

namespace chip {
namespace Logging {
namespace Platform {

extern "C" {
   uint32_t HAL_GetTick(void);
}

void ENFORCE_FORMAT(3, 0) LogV(const char * module, uint8_t category, const char * msg, va_list v)
{
    // Display current time

    uint32_t timeInMs = HAL_GetTick();

    uint32_t timeInS = timeInMs / 1000;

    uint32_t ms = timeInMs % 1000;

    uint32_t timeInMin = timeInS / 60;

    uint32_t sec = timeInS % 60;

    uint32_t hour = timeInMin / 60;

    uint32_t min = timeInMin % 60;

    printf("[%02d:%02d:%02d.%03d] ", hour, min, sec, ms);

    printf("CHIP:%s: ", module);
    vprintf(msg, v);
    printf("\n");
}

} // namespace Platform
} // namespace Logging
} // namespace chip

/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    app_led_bar_shield.h 
  * @author  MCD Application Team
  * @brief   Header for app_led_bar_shield.c module
  ******************************************************************************
* @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
  
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __APP_LED_BAR_SHIELD_H
#define __APP_LED_BAR_SHIELD_H

#ifdef __cplusplus
extern "C" {
#endif
/* Includes ------------------------------------------------------------------*/


#include "app_common.h"
/* Defines -------------------------------------------------------------------*/

#define LED_BAR_ON 1
#define LED_BAR_OFF 0

typedef enum {
  LED_SCENE_OFF= 0,
  LED_SCENE_RAINBOW,
  LED_SCENE_ROT_PINK,
  LED_SCENE_ROT_YELLOW,
  LED_SCENE_ROT_BLUE,
  LED_SCENE_ROT_WHITE,
  LED_SCENE_MAX
} LED_SCENE_t;
    
/* Exported functions ------------------------------------------------------- */
void Led_bar_shield_Init(void);
void Led_bar_shield_Start(void);
void Led_bar_shield_Stop(void);
void Led_bar_shield_On(void);
void Led_bar_shield_Off(void);
void Led_bar_set_scene(uint8_t sce);
void Led_bar_set_level(uint8_t level);
void Led_bar_get_status(uint8_t *status);
void Led_bar_set_Color(uint8_t Color_R,uint8_t Color_G,uint8_t Color_B);

#ifdef __cplusplus
}
#endif
#endif /* _APP_LED_BAR_SHIELD_H */

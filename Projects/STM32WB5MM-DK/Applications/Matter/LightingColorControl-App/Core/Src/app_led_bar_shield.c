/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file    app_led_bar_shield.c
 * @author  MCD Application Team
 * @brief   Led bar shield Application
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

/* Includes ------------------------------------------------------------------*/
#include "app_led_bar_shield.h"
#include "blinkt.h"
#include "cmsis_os.h"
#include "timers.h"


/* Private defines -----------------------------------------------------------*/
#define LED_BAR_SHIELD_UPDATE_PERIOD    (uint32_t)(0.005*1000*1000/CFG_TS_TICK_VAL) /*5ms*/

/* Private variables ---------------------------------------------------------*/
uint8_t Led_bar_shield_Timer_Id;
uint8_t mLedStatus = LED_BAR_OFF;
TimerHandle_t  LedTimeoutTimer;

osThreadId_t LedProcessId;
const osThreadAttr_t LedProcess_attr = { .name = LED_PROCESS_NAME, .attr_bits =
		LED_PROCESS_ATTR_BITS, .cb_mem = LED_PROCESS_CB_MEM, .cb_size =
		LED_PROCESS_CB_SIZE, .stack_mem = LED_PROCESS_STACK_MEM, .priority =
		LED_PROCESS_PRIORITY, .stack_size = LED_PROCESS_STACK_SIZE };



uint8_t Led_bar_scene, Led_bar_scene_next;

/* Private function prototypes -----------------------------------------------*/
static void Led_bar_shield_update(void);
static void LedUpdateProcess(void *argument);
static void LedTimeoutHandler(TimerHandle_t  xTimer);
/**
 * @brief  Led bar shield Initialization.
 */
void Led_bar_shield_Init(void) {

	BLINKT_Init(0, GPIOC, GPIO_PIN_1, GPIOC, GPIO_PIN_5);
	BLINKT_Init(1, GPIOB, GPIO_PIN_8, GPIOB, GPIO_PIN_4);
	BLINKT_Init(2, GPIOD, GPIO_PIN_14, GPIOD, GPIO_PIN_12);
	BLINKT_Init(3, GPIOB, GPIO_PIN_10, GPIOE, GPIO_PIN_0);

	LedProcessId = osThreadNew(LedUpdateProcess, NULL, &LedProcess_attr);

	LedTimeoutTimer = xTimerCreate("LedTimer", // Just a text name, not used by the RTOS kernel
			LED_BAR_SHIELD_UPDATE_PERIOD,        // == default timer period (mS)
			pdTRUE,               //  timer reload
			0,       // init timer
			LedTimeoutHandler // timer callback handler
			);

	Led_bar_scene = LED_SCENE_OFF;
	Led_bar_scene_next = LED_SCENE_OFF;

	return;
}

void Led_bar_shield_Start(void) {
	/* Start the timer used to update Led bar display */
	xTimerStart(LedTimeoutTimer, 0);
	mLedStatus = LED_BAR_ON;
}

void Led_bar_shield_Stop(void) {
	/* Stop the timer used to update Led bar display */
	xTimerStop(LedTimeoutTimer, 0);
	mLedStatus = LED_BAR_OFF;
}

void Led_bar_shield_On(void) {

	for(int i=0;i<4;i++){
		BLINKT_SetOn(i);
	}
}

void Led_bar_shield_Off(void) {

	for(int i=0;i<4;i++){
		BLINKT_SetOff(i);
	}
}
void Led_bar_get_status(uint8_t *status){
	*status = mLedStatus;
}
void Led_bar_set_scene(uint8_t sce) {
	Led_bar_scene_next = sce;

	return;
}

void Led_bar_set_level(uint8_t level){

	if(level > 0){
		for(int i=0;i<4;i++){
			BLINKT_SetLevel(i,0,0,level);
		}
	}
}
void Led_bar_set_Color(uint8_t Color_R,uint8_t Color_G,uint8_t Color_B){


		for(int i=0;i<4;i++){
			BLINKT_SetLevel(i,Color_R,Color_G,Color_B);
		}
}


volatile uint32_t led_val = 0;
volatile uint32_t led_val2 = 0;
volatile uint32_t led_val3 = 0;

static void LedTimeoutHandler(TimerHandle_t  xTimer) {
	  osThreadFlagsSet(LedProcessId, 1);
}

static void LedUpdateProcess(void *argument) {
	UNUSED(argument);

	for (;;) {
		osThreadFlagsWait(1, osFlagsWaitAny, osWaitForever);
		Led_bar_shield_update();
	}
}

static void Led_bar_shield_update(void) {
	uint32_t limit;

	if (Led_bar_scene != Led_bar_scene_next) {
		Led_bar_scene = Led_bar_scene_next;

		led_val = 0;
		led_val2 = 0;
		led_val3 = 0;

		switch (Led_bar_scene) {
		case LED_SCENE_OFF:
			break;
		case LED_SCENE_RAINBOW:
			BLINKT_SetAnimationMode(BLINKT_ANINATION_MODE_RAINBOW,
					360 / 16 / 2);
			break;
		case LED_SCENE_ROT_PINK:
			BLINKT_SetAnimationMode(BLINKT_ANINATION_MODE_ROT_PINK, led_val2);
			break;
		case LED_SCENE_ROT_YELLOW:
			BLINKT_SetAnimationMode(BLINKT_ANINATION_MODE_ROT_YELLOW, led_val2);
			break;
		case LED_SCENE_ROT_BLUE:
			BLINKT_SetAnimationMode(BLINKT_ANINATION_MODE_ROT_BLUE, led_val2);
			break;
		case LED_SCENE_ROT_WHITE:
			BLINKT_SetAnimationMode(BLINKT_ANINATION_MODE_ROT_WHITE, led_val2);
			break;
		default:
			break;
		}
	}

	switch (Led_bar_scene) {
	case LED_SCENE_RAINBOW:
		if (led_val >= 360) {
			led_val = 0;
		}

		BLINKT_AnimationStep(led_val);
		led_val++;
		break;
	case LED_SCENE_ROT_PINK:
	case LED_SCENE_ROT_YELLOW:
	case LED_SCENE_ROT_BLUE:
	case LED_SCENE_ROT_WHITE:
		limit = ((BAR_INSTANCE * LEDS_COUNT * 4) + (led_val3 * 3));
		if ((led_val / 8) >= limit) {
			led_val = 0;
			led_val2 = !led_val2;
			led_val3 = (uint32_t) (READ_BIT(RTC->SSR, RTC_SSR_SS))
					% (BAR_INSTANCE * LEDS_COUNT);
		}
		if ((led_val % 8) == 0) {
			BLINKT_AnimationStep(led_val2);
		}
		led_val++;
		break;
	default:
		break;
	}

	return;
}

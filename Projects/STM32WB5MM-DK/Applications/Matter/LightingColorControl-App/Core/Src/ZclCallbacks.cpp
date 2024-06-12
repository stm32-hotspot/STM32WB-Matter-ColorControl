/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * File Name          : ZclCallback.c
 * Description        : Cluster output source file for Matter.
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2019-2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */

#include "AppTask.h"
#include "LightingManager.h"
#include "ColorFormat.h"	


#include <app-common/zap-generated/ids/Attributes.h>
#include <app-common/zap-generated/ids/Clusters.h>
#include <app/ConcreteAttributePath.h>
#include <lib/support/logging/CHIPLogging.h>

using namespace chip;
using namespace chip::app::Clusters;

void MatterPostAttributeChangeCallback(const chip::app::ConcreteAttributePath &attributePath,
        uint8_t type, uint16_t size, uint8_t *value) {
    ClusterId clusterId = attributePath.mClusterId;
    AttributeId attributeId = attributePath.mAttributeId;
    static HsvColor_t hsv;	
    static CtColor_t ct;


    if (clusterId == OnOff::Id && attributeId == OnOff::Attributes::OnOff::Id) {
        LightingMgr().InitiateAction(
                *value ? LightingManager::ON_ACTION : LightingManager::OFF_ACTION, 0, size, value);
    } else if (clusterId == LevelControl::Id
            && attributeId == LevelControl::Attributes::CurrentLevel::Id) {
        LightingMgr().InitiateAction(LightingManager::LEVEL_ACTION, 0, size, value);
    }
    
    else if (clusterId == ColorControl::Id) {
    		/* XY color space */
    		        if (attributeId == ColorControl::Attributes::CurrentX::Id || attributeId == ColorControl::Attributes::CurrentY::Id)
    		        {
    		        	//APP_DBG("XY color space");
    		        	ChipLogProgress(NotSpecified, "XY color space")
    		        }
    		        /* HSV color space *    		         */

    		        else if (attributeId == ColorControl::Attributes::CurrentHue::Id ||
    		                 attributeId == ColorControl::Attributes::CurrentSaturation::Id ||
    		                attributeId == ColorControl::Attributes::EnhancedCurrentHue::Id)
    		        {
    		        	if (attributeId == ColorControl::Attributes::EnhancedCurrentHue::Id)
    		        	    {
    		        	       hsv.h = (uint8_t)(((*reinterpret_cast<uint16_t *>(value)) & 0xFF00) >> 8);
    		        	       hsv.s = (uint8_t)((*reinterpret_cast<uint16_t *>(value)) & 0xFF);
    		        	    }
    		        	else if (attributeId == ColorControl::Attributes::CurrentHue::Id)
    		        	    {
    		        	    	hsv.h = *value;
    		        	    }
    		        	 else if (attributeId == ColorControl::Attributes::CurrentSaturation::Id)
    		        	    {
    		        	        hsv.s = *value;
    		        	    }
    		        	LightingMgr().InitiateAction(LightingManager::COLOR_ACTION_HSV, 0, size,(uint8_t *) &hsv);
    		        }
    		        
    		        else if (attributeId == ColorControl::Attributes::ColorTemperatureMireds::Id)
    		        {
    		        	//ct.ctMireds = *reinterpret_cast<uint16_t *>(value);
    		        	ct.ctMireds =  (uint16_t)(*reinterpret_cast<uint16_t *>(value));
    		        	if (ct.ctMireds!=0)	
    		        	
    		           LightingMgr().InitiateAction(LightingManager::COLOR_ACTION_CT, 0,size,(uint8_t *) &ct.ctMireds);

    		        }
    		  }
}

void emberAfOnOffClusterInitCallback(EndpointId endpoint) {
}


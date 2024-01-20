/**
  ******************************************************************************
  * @file    py32f0xx_ll_lptim.c
  * @author  MCU Application Team
  * @brief   LPTIM LL module driver.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) Puya Semiconductor Co.
  * All rights reserved.</center></h2>
  *
  * <h2><center>&copy; Copyright (c) 2016 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
#if defined(USE_FULL_LL_DRIVER)

/* Includes ------------------------------------------------------------------*/
#include "py32f0xx_ll_lptim.h"
#include "py32f0xx_ll_bus.h"
#include "py32f0xx_ll_rcc.h"


#ifdef  USE_FULL_ASSERT
#include "py32_assert.h"
#else
#define assert_param(expr) ((void)0U)
#endif /* USE_FULL_ASSERT */

/** @addtogroup PY32F0XX_LL_Driver
  * @{
  */

#if defined (LPTIM) 

/** @addtogroup LPTIM_LL
  * @{
  */

/* Private types -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private constants ---------------------------------------------------------*/
/* Private macros ------------------------------------------------------------*/
/** @addtogroup LPTIM_LL_Private_Macros
  * @{
  */

#define IS_LL_LPTIM_CLOCK_PRESCALER(__VALUE__) (((__VALUE__) == LL_LPTIM_PRESCALER_DIV1)   \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV2)   \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV4)   \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV8)   \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV16)  \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV32)  \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV64)  \
                                                || ((__VALUE__) == LL_LPTIM_PRESCALER_DIV128))

#define IS_LL_LPTIM_UPDATA_MODE(__VALUE__) (((__VALUE__) == LL_LPTIM_UPDATE_MODE_IMMEDIATE)   \
                                            || ((__VALUE__) == LL_LPTIM_UPDATE_MODE_ENDOFPERIOD))   \
  

/**
  * @}
  */

/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/
/** @defgroup LPTIM_Private_Functions LPTIM Private Functions
  * @{
  */
/**
  * @}
  */
/* Exported functions --------------------------------------------------------*/
/** @addtogroup LPTIM_LL_Exported_Functions
  * @{
  */

/** @addtogroup LPTIM_LL_EF_Init
  * @{
  */

/**
  * @brief  Set LPTIMx registers to their reset values.
  * @param  LPTIMx LP Timer instance
  * @retval An ErrorStatus enumeration value:
  *          - SUCCESS: LPTIMx registers are de-initialized
  *          - ERROR: invalid LPTIMx instance
  */
ErrorStatus LL_LPTIM_DeInit(LPTIM_TypeDef *LPTIMx)
{
  ErrorStatus result = SUCCESS;

  /* Check the parameters */
  assert_param(IS_LPTIM_INSTANCE(LPTIMx));
  
  if (LPTIMx == LPTIM)
  {
    LL_APB1_GRP1_ForceReset(LL_APB1_GRP1_PERIPH_LPTIM1);
    LL_APB1_GRP1_ReleaseReset(LL_APB1_GRP1_PERIPH_LPTIM1);
  }
  else
  {
    result = ERROR;
  }

  return result;
}

/**
  * @brief  Set each fields of the LPTIM_InitStruct structure to its default
  *         value.
  * @param  LPTIM_InitStruct pointer to a @ref LL_LPTIM_InitTypeDef structure
  * @retval None
  */
void LL_LPTIM_StructInit(LL_LPTIM_InitTypeDef *LPTIM_InitStruct)
{
  /* Set the default configuration */
  LPTIM_InitStruct->Prescaler   = LL_LPTIM_PRESCALER_DIV1;
  LPTIM_InitStruct->UpdateMode  = LL_LPTIM_UPDATE_MODE_IMMEDIATE;
}

/**
  * @brief  Configure the LPTIMx peripheral according to the specified parameters.
  * @note LL_LPTIM_Init can only be called when the LPTIM instance is disabled.
  * @note LPTIMx can be disabled using unitary function @ref LL_LPTIM_Disable().
  * @param  LPTIMx LP Timer Instance
  * @param  LPTIM_InitStruct pointer to a @ref LL_LPTIM_InitTypeDef structure
  * @retval An ErrorStatus enumeration value:
  *          - SUCCESS: LPTIMx instance has been initialized
  *          - ERROR: LPTIMx instance hasn't been initialized
  */
ErrorStatus LL_LPTIM_Init(LPTIM_TypeDef *LPTIMx, LL_LPTIM_InitTypeDef *LPTIM_InitStruct)
{
  ErrorStatus result = SUCCESS;
  /* Check the parameters */
  assert_param(IS_LPTIM_INSTANCE(LPTIMx));
  assert_param(IS_LL_LPTIM_CLOCK_PRESCALER(LPTIM_InitStruct->Prescaler));
  assert_param(IS_LL_LPTIM_UPDATA_MODE(LPTIM_InitStruct->UpdateMode));
  /* The LPTIMx_CFGR register must only be modified when the LPTIM is disabled
     (ENABLE bit is reset to 0).
  */
  if (LL_LPTIM_IsEnabled(LPTIMx) == 1UL)
  {
    result = ERROR;
  }
  else
  {
    /* Set PRESC bitfield according to Prescaler value */
    MODIFY_REG(LPTIMx->CFGR,
                (LPTIM_CFGR_PRESC | LPTIM_CFGR_PRELOAD),
                 LPTIM_InitStruct->Prescaler |
                 LPTIM_InitStruct->UpdateMode);
  }
  return result;
}

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

#endif /* LPTIM */

/**
  * @}
  */

#endif /* USE_FULL_LL_DRIVER */

/************************ (C) COPYRIGHT Puya *****END OF FILE****/

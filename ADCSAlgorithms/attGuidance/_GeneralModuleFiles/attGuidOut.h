/*
Copyright (c) 2016, Autonomous Vehicle Systems Lab, Univeristy of Colorado at Boulder

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

*/

#ifndef _ATT_GUID_OUT_H_
#define _ATT_GUID_OUT_H_

#include <stdint.h>

#define MAX_RASTER_SET 36
/*! \addtogroup ADCSAlgGroup
 * @{
 */

/*! @brief Structure used to define the format of an attitude maneuver command */
typedef struct {
   double sigma_BR[3];      /*!< -- Commanded body wrt reference that we are tracking*/
   double omega_BR[3];      /*!< r/s Body rate of that commanded attitude vector*/
}attCmdOut;

/*! @brief Structure used to define the output definition for attitude guidance*/
typedef struct {
    double sigma_BR[3];         /*!<        Current attitude error estimate (MRPs) of B relative to R*/
    double omega_BR_B[3];       /*!< [r/s]  Current body error estimate of B relateive to R
                                            in B frame compoonents */
    double omega_RN_B[3];       /*!< [r/s]  Reference frame rate vector of the of R relative to N
                                            in B frame components */
    double domega_RN_B[3];      /*!< [r/s2] Reference frame inertial body acceleration of R relative
                                            to N in B frame components */
}attGuidOut;

/*! @brief Structure used to define the output definition for attitude reference generation */
typedef struct {
    double sigma_RN[3];         /*!<        Current attitude error estimate (MRPs) of B relative to R*/
    double omega_RN_N[3];       /*!< [r/s]  Reference frame rate vector of the of R relative to N
                                            in N frame components */
    double domega_RN_N[3];      /*!< [r/s2] Reference frame inertial acceleration of  R relative
                                            to N in N frame components */
}attRefOut;

/*! @brief Structure used to define the output euler set for attitude reference generation */
typedef struct {
    double set[3];
}eulerOut;

/*! @} */

#endif

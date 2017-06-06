#ifndef STH_STATUS_H
#define STH_STATUS_H

#include "sth/base.h"


typedef struct {
    SthRet status;
} SthStatus;


SthRet sth_status_new (SthStatus **st);
SthRet sth_status_free (SthStatus *st);


#endif /* STH_STATUS_H */

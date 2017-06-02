#ifndef STH_BUILTINS_INT_H
#define STH_BUILTINS_INT_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"


typedef struct {
    STH_OBJECT_MEMBERS
    long value;
} SthInt;


SthRet sth_int_new (SthStatus *st);
SthRet sth_int_free (SthStatus *st);


#endif /* STH_BUILTINS_INT_H */

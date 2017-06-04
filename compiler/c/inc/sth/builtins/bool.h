#ifndef STH_BUILTINS_BOOL_H
#define STH_BUILTINS_BOOL_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"


typedef struct {
    STH_OBJECT_MEMBERS
    int value;
} SthBool;


SthRet sth_bool_new (SthStatus *st);
SthRet sth_bool_free (SthStatus *st);


#endif /* STH_BUILTINS_BOOL_H */

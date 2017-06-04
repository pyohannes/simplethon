#ifndef STH_BUILTINS_INT_H
#define STH_BUILTINS_INT_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"


typedef struct {
    STH_OBJECT_MEMBERS
    SthRet (*__add__)(SthStatus *st);
    SthRet (*__sub__)(SthStatus *st);
    SthRet (*__mul__)(SthStatus *st);
    SthRet (*__div__)(SthStatus *st);
    SthRet (*__mod__)(SthStatus *st);
    SthRet (*__lt__)(SthStatus *st);
    SthRet (*__le__)(SthStatus *st);
    SthRet (*__eq__)(SthStatus *st);
    long value;
} SthInt;


SthRet sth_int_new (SthStatus *st);
SthRet sth_int_free (SthStatus *st);


#endif /* STH_BUILTINS_INT_H */

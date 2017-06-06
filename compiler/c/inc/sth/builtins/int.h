#ifndef STH_BUILTINS_INT_H
#define STH_BUILTINS_INT_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"
#include "sth/builtins/bool.h"

typedef struct SthInt_ SthInt;

struct SthInt_{
    STH_OBJECT_MEMBERS
    SthRet (*__add__)(SthStatus *st, SthInt **ret, SthInt *self, SthInt *other);
    SthRet (*__sub__)(SthStatus *st, SthInt **ret, SthInt *self, SthInt *other);
    SthRet (*__mul__)(SthStatus *st, SthInt **ret, SthInt *self, SthInt *other);
    SthRet (*__div__)(SthStatus *st, SthInt **ret, SthInt *self, SthInt *other);
    SthRet (*__mod__)(SthStatus *st, SthInt **ret, SthInt *self, SthInt *other);
    SthRet (*__lt__)(SthStatus *st, SthBool **ret, SthInt *self, SthInt *other);
    SthRet (*__le__)(SthStatus *st, SthBool **ret, SthInt *self, SthInt *other);
    SthRet (*__eq__)(SthStatus *st, SthBool **ret, SthInt *self, SthInt *other);
    long value;
};


SthRet sth_int_new (SthStatus *st, SthInt **ret, long value);


#endif /* STH_BUILTINS_INT_H */

#ifndef STH_BUILTINS_FREE_H
#define STH_BUILTINS_FREE_H

#include <stdio.h>
#include "sth/base.h"
#include "sth/builtins/int.h"


SthRet sth_free (SthStatus *st, SthCraw **ret, SthObject *obj)
{
    obj->free (obj);

    return st->status;
}


#endif /* STH_BUILTINS_FREE_H */

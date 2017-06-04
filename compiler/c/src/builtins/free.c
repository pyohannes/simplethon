#ifndef STH_BUILTINS_FREE_H
#define STH_BUILTINS_FREE_H

#include <stdio.h>
#include "sth/builtins/print.h"
#include "sth/builtins/int.h"


SthRet sth_free (SthStatus *st)
{
    SthObject *i = (SthObject *) sth_status_frame_argval_get (st, 0);

    i->free (i);

    return sth_status_status_get (st);
}


#endif /* STH_BUILTINS_FREE_H */

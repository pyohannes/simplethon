#ifndef STH_BUILTINS_PRINT_H
#define STH_BUILTINS_PRINT_H

#include <stdio.h>
#include "sth/builtins/print.h"
#include "sth/builtins/int.h"


SthRet sth_print (SthStatus *st)
{
    SthInt *i = sth_status_frame_argval_get (st, 0);

    int ret = printf ("%ld\n", i->value);

    if (ret <= 0) {
        sth_status_status_set (st, STH_ERR_IO);
    }

    return sth_status_status_get (st);
}


#endif /* STH_BUILTINS_PRINT_H */

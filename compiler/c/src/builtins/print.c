#ifndef STH_BUILTINS_PRINT_H
#define STH_BUILTINS_PRINT_H

#include <stdio.h>
#include "sth/base.h"
#include "sth/builtins/print.h"
#include "sth/builtins/int.h"


SthRet sth_print (SthStatus *st, SthCraw **ret, SthInt *i)
{
    int retcode = printf ("%ld\n", i->value);

    if (retcode <= 0) {
        st->status = STH_ERR_IO;
    }

    return st->status;
}


#endif /* STH_BUILTINS_PRINT_H */

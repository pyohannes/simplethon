#include <stdlib.h>
#include "sth/builtins/int.h"


static void sth_int_free_internal (void *obj)
{
    if (obj) {
        free (obj);
    }
}


SthRet sth_int_new (SthStatus *st)
{
    SthInt *i = malloc (sizeof (SthInt));
    if (!i) {
        sth_status_status_set (st, STH_ERR_MEM);
        goto sth_int_new_error;
    }
    i->free = sth_int_free_internal;
    sth_status_frame_retval_set (st, 0, i);

    return sth_status_status_get (st);

sth_int_new_error:
    return sth_status_status_get (st);
}


SthRet sth_int_free (SthStatus *st)
{
    void *i = sth_status_frame_argval_get (st, 0);
    sth_int_free_internal (i);

    return sth_status_status_get (st);
}

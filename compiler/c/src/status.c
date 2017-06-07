#include <stdlib.h>
#include "sth/status.h"


SthRet sth_status_new (SthStatus **st)
{
    if (!(*st = malloc (sizeof (SthStatus)))) {
        return STH_ERR_MEM;
    }

    (*st)->status = STH_OK;

    return STH_OK;
}


SthRet sth_status_free (SthStatus *st)
{
    if (st) {
        free (st);
    }

    return STH_OK;
}

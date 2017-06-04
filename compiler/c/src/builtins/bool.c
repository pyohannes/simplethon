#include <stdlib.h>
#include "sth/builtins/bool.h"
#include "sth/status.h"


static void sth_bool_free_internal (void *obj)
{
    if (obj) {
        free (obj);
    }
}


static SthRet sth_bool___craw___internal (SthStatus *st)
{
    SthBool *i = (SthBool *) sth_status_frame_argval_get (st, 0);
    sth_status_frame_retval_set (st, 0, i);
    return sth_status_status_get (st);
}

/*
static SthRet sth_bool___add___internal (SthStatus *st)
{
    SthBool *i1 = (SthBool *) sth_status_frame_argval_get (st, 0);
    SthBool *i2 = (SthBool *) sth_status_frame_argval_get (st, 1);
    SthBool *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_bool___add___error;
    }

    if (sth_bool_new(st) != STH_OK) {
        goto sth_bool___add___error;
    }
    
    result = (SthBool* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_bool___add___error;
    }
   
    result->value = i1->value + i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_bool___add___error:
    return sth_status_status_get (st);
}

*/


SthRet sth_bool_new (SthStatus *st)
{
    SthBool *i = malloc (sizeof (SthBool));
    if (!i) {
        sth_status_status_set (st, STH_ERR_MEM);
        goto sth_bool_new_error;
    }
    i->free = sth_bool_free_internal;
    i->__craw__= sth_bool___craw___internal;
    sth_status_frame_retval_set (st, 0, i);

    return sth_status_status_get (st);

sth_bool_new_error:
    return sth_status_status_get (st);
}


SthRet sth_bool_free (SthStatus *st)
{
    void *i = sth_status_frame_argval_get (st, 0);
    sth_bool_free_internal (i);

    return sth_status_status_get (st);
}

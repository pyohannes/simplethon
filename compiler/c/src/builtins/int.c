#include <stdlib.h>
#include "sth/builtins/int.h"
#include "sth/builtins/bool.h"
#include "sth/status.h"


static void sth_int_free_internal (void *obj)
{
    if (obj) {
        free (obj);
    }
}


static SthRet sth_int___craw___internal (SthStatus *st)
{
    SthInt *i = (SthInt *) sth_status_frame_argval_get (st, 0);
    sth_status_frame_retval_set (st, 0, i);
    return sth_status_status_get (st);
}


static SthRet sth_int___add___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthInt *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___add___error;
    }

    if (sth_int_new(st) != STH_OK) {
        goto sth_int___add___error;
    }
    
    result = (SthInt* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___add___error;
    }
   
    result->value = i1->value + i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___add___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___sub___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthInt *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___sub___error;
    }

    if (sth_int_new(st) != STH_OK) {
        goto sth_int___sub___error;
    }
    
    result = (SthInt* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___sub___error;
    }
   
    result->value = i1->value - i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___sub___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___mul___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthInt *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___mul___error;
    }

    if (sth_int_new(st) != STH_OK) {
        goto sth_int___mul___error;
    }
    
    result = (SthInt* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___mul___error;
    }
   
    result->value = i1->value * i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___mul___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___div___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthInt *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___div___error;
    }

    if (sth_int_new(st) != STH_OK) {
        goto sth_int___div___error;
    }
    
    result = (SthInt* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___div___error;
    }
   
    result->value = i1->value / i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___div___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___mod___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthInt *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___mod___error;
    }

    if (sth_int_new(st) != STH_OK) {
        goto sth_int___mod___error;
    }
    
    result = (SthInt* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___mod___error;
    }
   
    result->value = i1->value % i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___mod___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___lt___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthBool *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___lt___error;
    }

    if (sth_bool_new(st) != STH_OK) {
        goto sth_int___lt___error;
    }
    
    result = (SthBool* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___lt___error;
    }
   
    result->value = i1->value < i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___lt___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___eq___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthBool *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___eq___error;
    }

    if (sth_bool_new(st) != STH_OK) {
        goto sth_int___eq___error;
    }
    
    result = (SthBool* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___eq___error;
    }
   
    result->value = i1->value == i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___eq___error:
    return sth_status_status_get (st);
}


static SthRet sth_int___le___internal (SthStatus *st)
{
    SthInt *i1 = (SthInt *) sth_status_frame_argval_get (st, 0);
    SthInt *i2 = (SthInt *) sth_status_frame_argval_get (st, 1);
    SthBool *result;

    if (sth_status_frame_add(st, 0, 1) != STH_OK) {
        goto sth_int___le__error;
    }

    if (sth_bool_new(st) != STH_OK) {
        goto sth_int___le__error;
    }
    
    result = (SthBool* ) sth_status_frame_retval_get(st, 0);
    if (sth_status_frame_remove(st) != STH_OK) {
        goto sth_int___le__error;
    }
   
    result->value = i1->value <= i2->value;
    sth_status_frame_retval_set (st, 0, (void *)result);

sth_int___le__error:
    return sth_status_status_get (st);
}


SthRet sth_int_new (SthStatus *st)
{
    SthInt *i = malloc (sizeof (SthInt));
    if (!i) {
        sth_status_status_set (st, STH_ERR_MEM);
        goto sth_int_new_error;
    }
    i->free = sth_int_free_internal;
    i->__craw__= sth_int___craw___internal;
    i->__add__= sth_int___add___internal;
    i->__sub__= sth_int___sub___internal;
    i->__mul__= sth_int___mul___internal;
    i->__div__= sth_int___div___internal;
    i->__mod__= sth_int___mod___internal;
    i->__lt__= sth_int___lt___internal;
    i->__le__= sth_int___le___internal;
    i->__eq__= sth_int___eq___internal;
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

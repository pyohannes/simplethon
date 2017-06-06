#include "sth/builtins/bool.h"
#include "sth/status.h"


static SthRet sth_bool_free_internal (void *obj)
{
    return STH_OK;
}


static SthRet sth_bool___craw___internal (SthStatus *st, SthCraw **ret, 
        SthObject *b)
{
    *ret = (SthCraw *)b;
    return st->status;
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


static SthBool Sth_True_ = { 
    sth_bool_free_internal,
    sth_bool___craw___internal,
    1
};


static SthBool Sth_False_ = { 
    sth_bool_free_internal,
    sth_bool___craw___internal,
    0
};


SthBool *Sth_True = &Sth_True_;
SthBool *Sth_False = &Sth_False_;

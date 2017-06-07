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

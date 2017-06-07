#ifndef STH_BUILTINS_INT_H
#define STH_BUILTINS_INT_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"
#include "sth/builtins/bool.h"


typedef struct SthInt_ SthInt;


typedef SthRet (*SthFP_IntInt_Int)(SthStatus *, SthInt **, SthInt*, SthInt*);
typedef SthRet (*SthFP_IntInt_Bool)(SthStatus *, SthBool **, SthInt*, 
        SthInt*);


struct SthInt_{
    STH_OBJECT_MEMBERS
    SthFP_IntInt_Int __add__;
    SthFP_IntInt_Int __sub__;
    SthFP_IntInt_Int __mul__;
    SthFP_IntInt_Int __div__;
    SthFP_IntInt_Int __mod__;
    SthFP_IntInt_Bool __lt__;
    SthFP_IntInt_Bool __le__;
    SthFP_IntInt_Bool __eq__;
    long value;
};


SthRet sth_int_new (SthStatus *st, SthInt **ret, long value);


#endif /* STH_BUILTINS_INT_H */

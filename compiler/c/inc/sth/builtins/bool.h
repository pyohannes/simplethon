#ifndef STH_BUILTINS_BOOL_H
#define STH_BUILTINS_BOOL_H

#include "sth/base.h"
#include "sth/status.h"
#include "sth/object.h"


typedef struct {
    STH_OBJECT_MEMBERS
    int value;
} SthBool;


extern SthBool *Sth_True;
extern SthBool *Sth_False;


#endif /* STH_BUILTINS_BOOL_H */

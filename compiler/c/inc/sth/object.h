#ifndef STH_OBJECT_H
#define STH_OBJECT_H

#include "sth/base.h"
#include "sth/status.h"



#define STH_OBJECT_MEMBERS \
    SthRet (*free)(void *); \
    SthRet (*__craw__)(SthStatus *, SthCraw **, SthObject *);


typedef struct SthObject_ SthObject;


struct SthObject_ {
    STH_OBJECT_MEMBERS
};


#endif /* STH_OBJECT_H */

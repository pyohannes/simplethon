#ifndef STH_OBJECT_H
#define STH_OBJECT_H

#include "sth/base.h"
#include "sth/status.h"


#define STH_OBJECT_MEMBERS \
    void (*free)(void *); \
    SthRet (*__craw__)(SthStatus *);


typedef struct {
    STH_OBJECT_MEMBERS
} SthObject;


#endif /* STH_OBJECT_H */

#ifndef STH_OBJECT_H
#define STH_OBJECT_H


#define STH_OBJECT_MEMBERS \
    void (*free)(void *);


typedef struct {
    STH_OBJECT_MEMBERS
} SthObject;


#endif /* STH_OBJECT_H */

#ifndef STH_STATUS_H
#define STH_STATUS_H

#include "sth/base.h"


typedef struct _SthStatus SthStatus;


SthRet sth_status_new (SthStatus **st);
SthRet sth_status_free (SthStatus *st);

SthRet sth_status_status_get (const SthStatus *st);
SthRet sth_status_status_set (SthStatus *st, SthRet status);

SthRet sth_status_frame_add (SthStatus *st, unsigned argc, unsigned retc);
SthRet sth_status_frame_remove (SthStatus *st);
void sth_status_frame_retval_set (SthStatus *st, unsigned pos, void *val);
void *sth_status_frame_retval_get (SthStatus *st, unsigned pos);
void sth_status_frame_argval_set (SthStatus *st, unsigned pos, void *val);
void *sth_status_frame_argval_get (SthStatus *st, unsigned pos);


#endif /* STH_STATUS_H */

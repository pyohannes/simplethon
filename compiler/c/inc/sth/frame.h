#ifndef STH_FRAME_H
#define STH_FRAME_H

#include "sth/base.h"


typedef struct _SthFrame SthFrame;


SthFrame *sth_frame_new (unsigned argc, unsigned retc);
void sth_frame_free (SthFrame *frame);

void *sth_frame_retval_get (SthFrame *frame, unsigned pos);
void sth_frame_retval_set (SthFrame *frame, unsigned pos, void *val);
void *sth_frame_argval_get (SthFrame *frame, unsigned pos);
void sth_frame_argval_set (SthFrame *frame, unsigned pos, void *val);


#endif /* STH_FRAME_H */

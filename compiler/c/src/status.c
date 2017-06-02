#include <stdlib.h>
#include "sth/status.h"
#include "sth/frame.h"
#include "sth/list.h"


struct _SthStatus {
    SthRet status;
    SthPtrList *frames;
};


SthRet sth_status_new (SthStatus **st)
{
    *st = malloc (sizeof (SthStatus));
    if (!*st) {
        return STH_ERR_MEM;
    }

    if (!((*st)->frames = sth_ptrlist_new ())) {
        free (*st);
        return STH_ERR_MEM;
    }

    (*st)->status = STH_OK;

    return STH_OK;
}


SthRet sth_status_status_get (const SthStatus *st)
{
    return st->status;
}


SthRet sth_status_status_set (SthStatus *st, SthRet status)
{
    st->status = status;

    return status;
}


SthRet sth_status_free (SthStatus *st)
{
    if (st) {
        /* it is assumed that st->frames is always empty when status
         * is freed. */
        sth_ptrlist_free (st->frames, 0);
        free (st);
    }

    return STH_OK;
}


SthRet sth_status_frame_add (SthStatus *st, unsigned argc, unsigned retc)
{
    SthFrame *frame = sth_frame_new (argc, retc);

    if (!frame) {
        st->status = STH_ERR_MEM;
        goto sth_status_frame_add_error;
    }

    if (!sth_ptrlist_prepend (st->frames, frame)) {
        st->status = STH_ERR_MEM;
        goto sth_status_frame_add_error;
    }

    return st->status;
        
sth_status_frame_add_error:
    return st->status;
}


SthRet sth_status_frame_remove (SthStatus *st)
{
    SthFrame *frame;

    sth_ptrlist_at (st->frames, 0, (void **)&frame);
    sth_frame_free (frame);
    sth_ptrlist_remove (st->frames, 0, 0);

    return st->status;
}


void sth_status_frame_retval_set (SthStatus *st, unsigned pos, void *val)
{
    SthFrame *frame;
    sth_ptrlist_at (st->frames, 0, (void **)&frame);
    sth_frame_retval_set (frame, pos, val);
}


void *sth_status_frame_retval_get (SthStatus *st, unsigned pos)
{
    SthFrame *frame;
    sth_ptrlist_at (st->frames, 0, (void **)&frame);
    return sth_frame_retval_get (frame, pos);
}


void sth_status_frame_argval_set (SthStatus *st, unsigned pos, void *val)
{
    SthFrame *frame;
    sth_ptrlist_at (st->frames, 0, (void **)&frame);
    sth_frame_argval_set (frame, pos, val);
}


void *sth_status_frame_argval_get (SthStatus *st, unsigned pos)
{
    SthFrame *frame;
    sth_ptrlist_at (st->frames, 0, (void **)&frame);
    return sth_frame_argval_get (frame, pos);
}

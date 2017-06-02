#include <stdlib.h>
#include "sth/frame.h"


struct _SthFrame {
    void **arg_values;
    void **return_values;
};


SthFrame *sth_frame_new (unsigned argc, unsigned retc)
{
    SthFrame *frame = malloc (sizeof (SthFrame));

    if (!frame) {
        return 0;
    }

    if (argc > 0) {
        frame->arg_values = malloc (sizeof (void *) * argc);
        if (!frame->arg_values) {
            free (frame);
            return 0;
        }
    } else {
        frame->arg_values = 0;
    }

    if (retc > 0) {
        frame->return_values = malloc (sizeof (void *) * retc);
        if (!frame->return_values) {
            free (frame);
            return 0;
        }
    } else {
        frame->return_values = 0;
    }
    
    return frame;
}


void sth_frame_free (SthFrame *frame)
{
    if (frame) {
        if (frame->arg_values) {
           free (frame->arg_values);
        } 
        if (frame->return_values) {
           free (frame->return_values);
        } 
        free (frame);
    }
}


void *sth_frame_retval_get (SthFrame *frame, unsigned pos)
{
    return frame->return_values[pos];
}


void sth_frame_retval_set (SthFrame *frame, unsigned pos, void *val)
{
    frame->return_values[pos] = val;
}


void *sth_frame_argval_get (SthFrame *frame, unsigned pos)
{
    return frame->arg_values[pos];
}


void sth_frame_argval_set (SthFrame *frame, unsigned pos, void *val)
{
    frame->arg_values[pos] = val;
}


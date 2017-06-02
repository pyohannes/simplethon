#include <stdlib.h>
#include "sth/list.h"
#include "sth/object.h"


typedef struct _SthPtrListItem SthPtrListItem;
struct _SthPtrListItem {
    void *item;
    SthPtrListItem *next;
};


struct _SthPtrList {
    SthPtrListItem *first;
};


SthPtrList *sth_ptrlist_new ()
{
    SthPtrList *list = malloc (sizeof (SthPtrList));
    if (!list) {
        return 0;
    }

    list->first = 0;

    return list;
}


void sth_ptrlist_free (SthPtrList *list, int objfree)
{
    SthPtrListItem *litem = list->first;

    while (litem) {
        SthPtrListItem *curr = litem;
        if (objfree) {
            ((SthObject *)(curr->item))->free (curr->item);
        }
        litem = litem->next;
        free (curr->item);
    }
    free (list);
}


int sth_ptrlist_prepend (SthPtrList *list, void *item)
{
    SthPtrListItem *litem = malloc (sizeof (SthPtrListItem));

    if (!litem) {
        return 0;
    }

    litem->item = item;
    litem->next = list->first;
    list->first = litem;

    return 1;
}


int sth_ptrlist_at (const SthPtrList *list, unsigned pos, void **item)
{
    SthPtrListItem *litem = list->first;

    while (pos) {
        litem = litem->next;
        pos--;
    }

    *item = litem->item;

    return 1;
}


int sth_ptrlist_remove (SthPtrList *list, unsigned pos, int freeobj)
{
    SthPtrListItem *litem = list->first;
    SthPtrListItem *old, *prev;

    if (pos == 0) {
        if (litem) {
            old = list->first;
            list->first = old->next;
        }
    } else {
        while (pos) {
            prev = litem;
            litem = litem->next;
            pos--;
        }
        old = litem;
        prev->next = old->next;
    }

    if (freeobj) {
        ((SthObject *)(old->item))->free (old->item);
    }
    free (old);

    return 1;
}

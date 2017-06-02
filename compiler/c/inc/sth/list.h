#ifndef STH_LIST_H
#define STH_LIST_H


typedef struct _SthPtrList SthPtrList;


SthPtrList *sth_ptrlist_new ();
void sth_ptrlist_free (SthPtrList *list, int objfree);
int sth_ptrlist_prepend (SthPtrList *list, void *item);
int sth_ptrlist_at (const SthPtrList *list, unsigned pos, void **item);
int sth_ptrlist_remove (SthPtrList *list, unsigned pos, int objfree);


#endif /* STH_LIST_H */

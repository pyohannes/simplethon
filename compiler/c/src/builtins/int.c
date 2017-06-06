#include <stdlib.h>
#include "sth/builtins/int.h"
#include "sth/builtins/bool.h"
#include "sth/status.h"


#define STH_MAKE_INT(val) \
    {  sth_int_free_internal, \
       sth_int___craw___internal, \
       sth_int___add___internal, \
       sth_int___sub___internal, \
       sth_int___mul___internal, \
       sth_int___div___internal, \
       sth_int___mod___internal, \
       sth_int___lt___internal, \
       sth_int___le___internal, \
       sth_int___eq___internal, \
       val }


static SthRet sth_int_free_internal (void *obj)
{
    SthInt *i = (SthInt *)obj;

    if (i && (i->value < 0 || i->value > 100)) {
        free (obj);
    }

    return STH_OK;
}


static SthRet sth_int___craw___internal (SthStatus *st, SthCraw **ret, 
        SthObject *i)
{
    *ret = (SthCraw *) i;
    return st->status;
}


static SthRet sth_int___add___internal (SthStatus *st, SthInt **ret, 
        SthInt *self, SthInt *other)
{
    sth_int_new(st, ret, self->value + other->value);
    return st->status;
}


static SthRet sth_int___sub___internal (SthStatus *st, SthInt **ret, 
        SthInt *self, SthInt *other)
{
    sth_int_new(st, ret, self->value - other->value);
    return st->status;
}


static SthRet sth_int___mul___internal (SthStatus *st, SthInt **ret, 
        SthInt *self, SthInt *other)
{
    sth_int_new(st, ret, self->value * other->value);
    return st->status;
}


static SthRet sth_int___div___internal (SthStatus *st, SthInt **ret, 
        SthInt *self, SthInt *other)
{
    sth_int_new(st, ret, self->value / other->value);
    return st->status;
}


static SthRet sth_int___mod___internal (SthStatus *st, SthInt **ret, 
        SthInt *self, SthInt *other)
{
    sth_int_new(st, ret, self->value % other->value);
    return st->status;
}


static SthRet sth_int___lt___internal (SthStatus *st, SthBool **ret, 
        SthInt *self, SthInt *other)
{
    *ret = (self->value < other->value) ? Sth_True : Sth_False;
    return st->status;
}


static SthRet sth_int___eq___internal (SthStatus *st, SthBool **ret, 
        SthInt *self, SthInt *other)
{
    *ret = (self->value == other->value) ? Sth_True : Sth_False;
    return st->status;
}


static SthRet sth_int___le___internal (SthStatus *st, SthBool **ret, 
        SthInt *self, SthInt *other)
{
    *ret = (self->value <= other->value) ? Sth_True : Sth_False;
    return st->status;
}


static SthInt int_cache_table[] = {
    STH_MAKE_INT(0),
    STH_MAKE_INT(1),
    STH_MAKE_INT(2),
    STH_MAKE_INT(3),
    STH_MAKE_INT(4),
    STH_MAKE_INT(5),
    STH_MAKE_INT(6),
    STH_MAKE_INT(7),
    STH_MAKE_INT(8),
    STH_MAKE_INT(9),
    STH_MAKE_INT(10),
    STH_MAKE_INT(11),
    STH_MAKE_INT(12),
    STH_MAKE_INT(13),
    STH_MAKE_INT(14),
    STH_MAKE_INT(15),
    STH_MAKE_INT(16),
    STH_MAKE_INT(17),
    STH_MAKE_INT(18),
    STH_MAKE_INT(19),
    STH_MAKE_INT(20),
    STH_MAKE_INT(21),
    STH_MAKE_INT(22),
    STH_MAKE_INT(23),
    STH_MAKE_INT(24),
    STH_MAKE_INT(25),
    STH_MAKE_INT(26),
    STH_MAKE_INT(27),
    STH_MAKE_INT(28),
    STH_MAKE_INT(29),
    STH_MAKE_INT(30),
    STH_MAKE_INT(31),
    STH_MAKE_INT(32),
    STH_MAKE_INT(33),
    STH_MAKE_INT(34),
    STH_MAKE_INT(35),
    STH_MAKE_INT(36),
    STH_MAKE_INT(37),
    STH_MAKE_INT(38),
    STH_MAKE_INT(39),
    STH_MAKE_INT(40),
    STH_MAKE_INT(41),
    STH_MAKE_INT(42),
    STH_MAKE_INT(43),
    STH_MAKE_INT(44),
    STH_MAKE_INT(45),
    STH_MAKE_INT(46),
    STH_MAKE_INT(47),
    STH_MAKE_INT(48),
    STH_MAKE_INT(49),
    STH_MAKE_INT(50),
    STH_MAKE_INT(51),
    STH_MAKE_INT(52),
    STH_MAKE_INT(53),
    STH_MAKE_INT(54),
    STH_MAKE_INT(55),
    STH_MAKE_INT(56),
    STH_MAKE_INT(57),
    STH_MAKE_INT(58),
    STH_MAKE_INT(59),
    STH_MAKE_INT(60),
    STH_MAKE_INT(61),
    STH_MAKE_INT(62),
    STH_MAKE_INT(63),
    STH_MAKE_INT(64),
    STH_MAKE_INT(65),
    STH_MAKE_INT(66),
    STH_MAKE_INT(67),
    STH_MAKE_INT(68),
    STH_MAKE_INT(69),
    STH_MAKE_INT(70),
    STH_MAKE_INT(71),
    STH_MAKE_INT(72),
    STH_MAKE_INT(73),
    STH_MAKE_INT(74),
    STH_MAKE_INT(75),
    STH_MAKE_INT(76),
    STH_MAKE_INT(77),
    STH_MAKE_INT(78),
    STH_MAKE_INT(79),
    STH_MAKE_INT(80),
    STH_MAKE_INT(81),
    STH_MAKE_INT(82),
    STH_MAKE_INT(83),
    STH_MAKE_INT(84),
    STH_MAKE_INT(85),
    STH_MAKE_INT(86),
    STH_MAKE_INT(87),
    STH_MAKE_INT(88),
    STH_MAKE_INT(89),
    STH_MAKE_INT(90),
    STH_MAKE_INT(91),
    STH_MAKE_INT(92),
    STH_MAKE_INT(93),
    STH_MAKE_INT(94),
    STH_MAKE_INT(95),
    STH_MAKE_INT(96),
    STH_MAKE_INT(97),
    STH_MAKE_INT(98),
    STH_MAKE_INT(99)
};


SthRet sth_int_new (SthStatus *st, SthInt **ret, long value)
{
    if (0 <= value && value < 100) {
        *ret = &(int_cache_table[value]);
    } else if ((*ret = malloc (sizeof (SthInt)))) {
        (*ret)->free = sth_int_free_internal;
        (*ret)->__craw__= sth_int___craw___internal;
        (*ret)->__add__= sth_int___add___internal;
        (*ret)->__sub__= sth_int___sub___internal;
        (*ret)->__mul__= sth_int___mul___internal;
        (*ret)->__div__= sth_int___div___internal;
        (*ret)->__mod__= sth_int___mod___internal;
        (*ret)->__lt__= sth_int___lt___internal;
        (*ret)->__le__= sth_int___le___internal;
        (*ret)->__eq__= sth_int___eq___internal;
        (*ret)->value = value;
    } else {
        st->status = STH_ERR_MEM;
    }

    return st->status;
}

import typing
import pymonad.maybe


T = typing.TypeVar('T')

class WriterMaybe(pymonad.maybe.Maybe[T]):
    def __init__(self, value: T, log: str, monoid: bool):
        super().__init__(value, monoid)
        if isinstance(log, Log):
            self.log = log
        else:
            self.log = Log(log)

class WriterJust(WriterMaybe[T]):
    def __init__(self, value: T, log: str =''):
        super().__init__(value, log, True)

class WriterNothing(WriterMaybe[T]):
    def __init__(self, log: str =''):
        super().__init__(None, log, False)

def bind(
    m: WriterMaybe[T],
    f1: typing.Callable[[T], WriterMaybe[T]],
    error_log: str=''
) -> WriterMaybe[T]:
    if m.is_just():
        res = f1(m.value)
        res.log = m.log + res.log
        return res
    return WriterNothing(m.log + Log(error_log))

def bind2(
    m1: WriterMaybe[T], m2: WriterMaybe[T],
    f2: typing.Callable[[T, T], WriterMaybe[T]],
    error_log: str = ''
) -> WriterMaybe[T]:
    if m1.is_just() and m2.is_just():
        res = f2(m1.value, m2.value)
        res.log = m1.log + m2.log + res.log
        return res
    return WriterNothing(m1.log + m2.log + Log(error_log))

def bind3(
    m1: WriterMaybe[T], m2: WriterMaybe[T], m3: WriterMaybe[T],
    f3: typing.Callable[[T, T, T], WriterMaybe[T]],
    error_log: str = ''
) -> WriterMaybe[T]:
    if m1.is_just() and m2.is_just() and m3.is_just():
        res = f3(m1.value, m2.value, m3.value)
        res.log = m1.log + m2.log + m3.log + res.log
        return res
    return WriterNothing(m1.log + m2.log + m3.log + Log(error_log))

def bind4(
    m1: WriterMaybe[T], m2: WriterMaybe[T], m3: WriterMaybe[T], m4: WriterMaybe[T],
    f4: typing.Callable[[T, T, T, T], WriterMaybe[T]],
    error_log: str = ''
) -> WriterMaybe[T]:
    if m1.is_just() and m2.is_just() and m3.is_just() and m4.is_just():
        res = f4(m1.value, m2.value, m3.value, m4.value)
        res.log = m1.log + m2.log + m3.log + m4.log + res.log
        return res
    return WriterNothing(m1.log + m2.log + m3.log + m4.log + Log(error_log))

def concat(
    ms: typing.List[WriterMaybe[T]],
    f2: typing.Callable[[T, T], WriterMaybe[T]] = lambda x, _: WriterJust(x),
    default0: WriterMaybe[T] = WriterNothing
) -> WriterMaybe[T]:
    if len(ms) == 0:
        return default0
    m = ms[0]
    res = WriterMaybe(m.value, m.log, m.monoid)
    for m in ms[1:]:
        res = bind2(res, m, f2)
    return res

class Log:
    def __init__(self, s: str):
        self.s = s

    def __add__(self, other):
        if other.s == '':
            return Log(self.s)
        elif self.s == '':
            return Log(other.s)
        return Log(self.s + '\n' + other.s)

    def __repr__(self):
        return f'{self.s}'

    __str__ = __repr__

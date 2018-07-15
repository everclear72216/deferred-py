'''`deferred` provides a Javascript-style promise API for python.
'''

from enum import IntEnum

class AbstractScheduler(object):
    '''
    Currently `deferred` requires a single user defined function to schedule a function call for
    later execution in an event loop style infrastructure. To stay library agnostic 
    `AbstractScheduler` derived classes are supposed to  hide the idiosynchrasies of how scheduling
    function calls works in your environment.
    '''

    def __init__(self):
        super(AbstractScheduler, self).__init__()

    def schedule_call(self, func):
        '''
        You need to re-implement this function for your runtime environment. `deferred` will call
        this method with a signle argument of type function. The function will not take parameters
        and it will return None.

        :param func: A function that takes no parameters and returns None. You need to schedule
                     this function to be called at a later point in time.
        '''
        raise NotImplementedError("AbstractScheduler.schedule_call() not implemented.")

class ImmediateScheduler(AbstractScheduler):
    '''
    The `ImmediateScheduler` is a non-conformant implementation of the `AbstractScheduler`. It
    violates the interface's contract by not scheduling calls to a later point in time. Calls
    are pushed to the current stack of the caller. This is extremely dangerous if called from a
    process that runs in another thread.
    '''
    def __init__(self):
        super(ImmediateScheduler, self).__init__()

    def schedule_call(self, func):
        '''
        Calls `func` immediately. This is most probably not what you want. However, it comes in
        handy when fooling around with `deferred` as long as there is no event loop in your
        project.
        '''
        func()

scheduler = ImmediateScheduler()

def set_scheduler(sched):
    '''
    Currently `deferred` uses a single global instance of an `AbstractScheduler` derived class as
    interface to the scheduling facilities of your application. You will need to define your own
    `AbstractScheduler` derived class and pass an instance of it to this function in order to
    successfully use `deferred`.

    :param sched: An instance of an `AbstractScheduler` derived class.
    '''
    global scheduler
    scheduler = sched

class DeferredStates(IntEnum):
    '''
    This enum defines the three states a deferred call can be in. It is `FULFILLED` if the call was
    executed successfully and its result is ready to be retrieved. And it can also be `REJECTED` in
    case some error occurred. `REJECTED` also means that a `reason` can be retrieved which is a
    value containing information about what went wrong.
    '''
    PENDING=0
    FULFILLED=1
    REJECTED=2

class Deferred(object):
    '''
    When implementing functions.
    '''
    def __init__(self):
        print(self, 'created')
        super(Deferred, self).__init__()

        self._state = DeferredStates.PENDING
        self._promise = Promise()

    def get_promise(self):
        return self._promise

    def fulfil(self, value):
        if self._state == DeferredStates.PENDING:
            global scheduler
            self._state = DeferredStates.FULFILLED
            scheduler.schedule_call(lambda: self._promise.fulfil(value))

    def reject(self, reason):
        if self._state == DeferredStates.PENDING:
            global scheduler
            self._state = DeferredStates.REJECTED
            scheduler.schedule_call(lambda: self._promise.reject(reason))

    def notify(self, value):
        if self._state == DeferredStates.PENDING:
            global scheduler
            scheduler.schedule_call(lambda: self._promise.notify(value))

class Promise(object):

    def __init__(self):
        print(self, 'created')
        super(Promise, self).__init__()

        self._listeners = []

        self._value = None
        self._reason = None

        self._state = DeferredStates.PENDING

    def fulfil(self, value):
        self._state = DeferredStates.FULFILLED
        self._value = value
        for l in self._listeners:
            l.fulfil(self._value)

    def reject(self, reason):
        self._state = DeferredStates.REJECTED
        self._reason = reason
        for l in self._listeners:
            l.reject(self._reason)

    def notify(self, value):
        for l in self._listeners:
            l.notify(value)

    def then(self, on_fulfilled=None, on_rejected=None, on_notify=None):
        print(self, 'then() called')

        deferred = defer()
        print(self, 'deferred created')

        l = Listener(deferred, on_fulfilled, on_rejected, on_notify)
        print(self, 'listener created')

        if self._state == DeferredStates.PENDING:
            print(self, 'still pending')
            self._listeners.append(l)
        elif self._state == DeferredStates.FULFILLED:
            print(self, 'already fulfilled')
            l.fulfil(self._value)
        elif self._state == DeferredStates.REJECTED:
            print(self, 'already rejected')
            l.reject(self._reason)
        else:
            print(self, 'should never come here.')

        return deferred.get_promise()

class Listener(object):
    def __init__(self, deferred, on_fulfilled, on_rejected, on_notify):
        super(Listener, self).__init__()

        self._deferred = deferred
        self._on_fulfilled = on_fulfilled
        self._on_rejected = on_rejected
        self._on_notify = on_notify

    def fulfil(self, value):
        if self._on_fulfilled:
            try:
                result = self._on_fulfilled(value)
                if self._deferred.get_promise() == result:
                    raise TypeError('Handlers must return a new promise.')
                elif isinstance(result, Promise):
                    result.then(lambda value: self._deferred.fulfil(value),
                        lambda reason: self._deferred.reject(reason),
                        lambda value: self._deferred.notify(value))
                else:
                    self._deferred.fulfil(result)
            except Exception as exc:
                self._deferred.reject(exc)
        else:
            self._deferred.fulfil(value)

    def reject(self, reason):
        if self._on_rejected:
            try:
                result = self._on_rejected(value)
                if self._deferred.get_promise() == result:
                    raise TypeError('Handlers must return a new promise.')
                elif isinstance(result, Promise):
                    result.then(lambda value: self._deferred.fulfil(value),
                        lambda reason: self._deferred.reject(reason),
                        lambda value: self._deferred.notify(value))
                else:
                    self._deferred.reject(result)
            except Exception as exc:
                self._deferred.reject(exc)
        else:
            self._deferred.reject(reason)

    def notify(self, value):
        if self._on_notify:
            try:
                self._on_notify(value)
            except:
                pass
                
        self._deferred.notify(value)

    def get_deferred(self):
        return self._deferred

def defer():
    return Deferred()

.. deferred documentation master file, created by
   sphinx-quickstart on Sun Jul  8 08:02:33 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for `deferred`
============================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

Introduction
------------

In Python we are lucky to have the choice between two methods to achieve concurrency in a single
process. Whether you favour co-routines or threads makes no difference for your undestanding of this
module. The important thing about them is that they allow your program to have multiple lines of
execution. Generally, at least one of these lines should always remain capable of accepting new
input. Let's call a line of execution that shall always be ready for input a main line of execution 
or a `main`, for short. Also let's also call lines of execution that do not need to remain 
responsive `workers`.

Some more Definitions
~~~~~~~~~~~~~~~~~~~~~

Workers process jobs that are created by a main. To keep it simple, this documentation will always
assume a single main. However, a worker for some reason might also be required to stay responsive to
new input. It is perfectly possible that a worker defers jobs to another worker and thereby assumes
the role of a main in that new relationship.

A job is a function to be executed on another line of execution. If that function takes parameters
the job needs to contain the function reference and references to the parameters. Usually the main
is interested in the eventual result of the function. The most convenient way of telling the main
that the result is available is to have the main define a callback function to be called with the
result as argument. So the job also needs to contain a reference to the callback function. Putting
everything together is done by Initiators. Initiators are called by a main. They are essentially
wrappers for functions to be executed in a worker.

The Promise Pattern
~~~~~~~~~~~~~~~~~~~

Promise is a design pattern for asynchronous programming. It suggests that initiators should return
a special type of object, a promise, to retrieve the result when the job is done. A promise provides
a method called `then` to register callbacks. It can be called with a total of three callbacks, 
which are all optional. The first callback is called if the job finishes successfully. Failures
shall be handled by the second callback. The third callback is for notifying the main about 
intermediate results while the job is still running. All callbacks are called with a single
positional argument representing the result, the reason for failure and intermediate results
respectively. For multi-threaded applications all callbacks will be called on the thread which
called the initiator.

Why / When Promise
~~~~~~~~~~~~~~~~~~

Up to this point there is no justification to prefer Promise over the standard methods like
`asyncio.Future` or `concurrent.futures.Future`. However, the fact that you are able to receive
results from the job being processed can be a reason for Promise in itself.

In order to look at the more advanced features demanded by Promise it is necessary to consider a 
more complex system: There is almost never just that one function you would like to run
asynchronously. Usually there are quite a few of them, all outfitted with their own initiator
functions. So you quickly find yourself in a situation where one asynchronous call depends on the
result of a previous asynchronous call, and so on. This results in chains, or more precisely in 
trees considering error handling.

Promise Chaining
~~~~~~~~~~~~~~~~

The support for chains is what makes Promise more powerful than Future. Promise demands that `then`
itself returns another promise. The behavior of the returned promise depends on the return values
of the callbacks you provide. If your success or failure callback returns a promise, the promise
returned by `then` will behave just like the promise that you return. This might be a little too
much to take in. So let's have a look at an example to clear the mist.

.. code-block:: python
    :linenos:

    from deferred import defer
    
    def is_smaller(n, k):
        d = defer()
        d.fulfill(n < k)
        return d.get_promise()

    def add_five_conditionally(n, flag):
        d = defer()
        d.fulfill(n + 5 if flag else 0)
        return d.get_promise()

    p = is_smaller(1, 2)
    q = p.then(
        lambda value: add_five_conditionally(10, value)
    )
    q.then(
        lambda value: print(value)
    )

If you run this code you will find it prints 15 to the console. Let's see why: The example defines
two functions. `is_smaller` takes two numbers `n` and `k` and returns a promise. The promise will
always be fulfilled. The value the promise will be fulfilled with depends on whether `n` is smaller
than `k`. If so, the promise will be fulfilled with `True`, and it will be fulfilled with `False`
otherwise.

Separation of Control and Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference
---------

.. automodule:: deferred
.. autoclass:: deferred.AbstractScheduler
.. automethod:: deferred.AbstractScheduler.schedule_call
.. autoclass:: deferred.ImmediateScheduler
.. automethod:: deferred.ImmediateScheduler.schedule_call
.. autofunction:: deferred.set_scheduler
.. autoclass:: deferred.DeferredStates
.. autoclass:: deferred.Deferred
.. autoclass:: deferred.Promise

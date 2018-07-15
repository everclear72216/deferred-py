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
process. Whether you favour co-routines or threads is irrelevant for your undestanding of this
module. The important thing about them is that they allow your program to have multiple lines of
execution. Generally, at least one of these lines should always remain capable of accepting new
input. Let's call a line of execution that shall always be ready for input a main line of execution 
or a `main`, for short. Also let's also call lines of execution that do not need to remain 
responsive `workers`.

Workers process jobs that are created by a main. To keep it simple, this documentation will always
assume a single main. However, it is perfectly possible that a worker offloads jobs to another
worker and thereby assumes the role of a main in that new relationship.

A job consists of some data and a function proccessing the data. Usually the main is interested in 
the eventual result of the function. The most convenient way of telling the main that the result is available is to have the main define a callback function to be called with the result as argument.
Packaging a job and a callback for execution in a worker is done by an initiator function. 
Initiators are essentially wrappers for functions to be executed in a worker.

Promise is a design pattern for asynchronous programming. It suggests that initiators should return
a special type of object, a promise, to retrieve the result when the job is done. In that respect a
promise is nothing more than a future, which we already have in Python. So let's have a quick look
at the commonalities before diving into the differences. Just like futures a promise provides a
method to register a callback to receive the result. The method is called `then`. In it can be
called with a total of three callbacks, which are all optional. The first callback is called if the
job finishes successfully. Failures shall be handled by the second callback. The third callback is
for passing arbitrary information (usually progress information) back to the main while the job is
still running. All callbacks are called with a single positional argument representing the result,
the reason for failure and intermediate information respectively.

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

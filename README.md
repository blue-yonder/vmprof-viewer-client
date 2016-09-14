# vmprof-viewer: a frontend to vmprof

## What is vmprof-viewer?
vmprof-viewer is a tool for profiling Python applications (RAM and CPU). It is based on [vmprof](https://vmprof.readthedocs.io/en/latest/) and has very low overhead. vmprof-viewer also provides a nice interactive web viewer for the generated profiles, so you can get started with profiling quickly.

vmprof-viewer is a statistical profiler. In a nutshell, it interrupts your Python application every X milliseconds and records its current stack trace and memory consumption (RSS). From these traces, the relative amount of time spent in each part of the application code can be approximated.

Since vmprof-viewer's runtime overhead is configurable, it is well suited for long running and intensive workloads.


## Installation
For the client:

```sh
pip install git+https://github.com/blue-yonder/vmprof-viewer-client
```

You'll need to have a vmprof-viewer server running, see https://github.com/blue-yonder/vmprof-viewer-server for details.

## Demo
You may use the provided profiling example to test your setup works correctly. The vmprof-viewer-server is expected to be hosted at `localhost:8000`.

```
python vmprofdemo.py demo
```

## Instrumentation
You have to add some sprinkles of vmprof-viewer to your own code, in order to enable profiling:

```py
import vmprof_viewer_client

# This needs to be executed once before any profiled code is run.
vmprof_viewer_client.configure("YOUR PROJECT NAME (whitespace ok)")
```

Is it possible to profile functions and methods by simply adding a decorator:

```py
@vmprof_viewer_client.profile
def some_func():
    ...

class SomeClass(...):
    @vmprof_viewer_client.profile
    def some_method(self):
        ...
```

Whenever you run a function or method with this decorator, it will automatically submit the collected profile to a webserver.


## Inspection

* [_Memory view_](https://cloud.githubusercontent.com/assets/175722/18513125/5f80dd08-7a8c-11e6-8ea8-de80b57f4e7f.png): Shows a graph with current memory usage of your programm. Each point in the graph is associated with the Python stack trace active at that point in time. By zooming into the interesting regions of the program execution, you can find out when and why memory was allocated.
* [_CPU view_](https://cloud.githubusercontent.com/assets/175722/18513127/6186894a-7a8c-11e6-8159-f4517c2ac749.png): Shows a heatmap over the all collected stack traces. This allows you to find and inspect the functions and methods where your program is spending most of its time.

If you also have traces that have been recorded with plain [vmprof](https://vmprof.readthedocs.io/en/latest/) (without using vmprof-viewer as a convenience wrapper), you can upload them to the vmprof-viewer server using a command-line tool provided by vmprof-viewer:

```
vmprof-viewer-upload "YOUR PROJECT NAME" /path/to/your/profile.dat
```


## Configuration (overhead/accuracy)

By default, vmprof-viewer interrupts your application every 100 milliseconds (`period=0.1`), which should be very low overhead for your application (around 0.1%). You can trade accuracy for performance and vise-versa by changing the profile interval:

```py
@vmprof_viewer_client.profile(period=0.001)
def some_func():
    ...
```

If you use vmprof-viewer on long-running processes (multiple hours), the sheer number of traces recorded might make the profile take a long time to transmit to the vmprof-viewer server. In this case you should choose a different interval as well. Recommended intervals:

| Duration | Recommended interval |
|----------|----------------------|
| <=3h     | 0.01--0.1 (100-10 Hz) |
| 6h       | 0.02--0.2 (50-5 Hz) |
| 12h      | 0.05--0.5 (20-2 Hz) |
| >=24h    | 0.9 (1 Hz, minimum) |


import resource
import humanize
import psutil


def print_memory_usage(label: str):
    """
    Ment to be used locally during development to figure our where memory usage
    spikes occur.

    Requires that you::

        $ pip install humanize psutil

    The numbers printed are:
    - uss: This is the memory which is unique to a process and which would be freed if the process
      was terminated right now (ref: https://psutil.readthedocs.io/en/latest/#psutil.Process.memory_full_info)
    - rss: This is the non-swapped physical memory the process uses right now
      (ref: https://psutil.readthedocs.io/en/latest/#psutil.Process.memory_info)
    - ru_maxrss: Sum of ru_maxrss from this process and child processes. This is the max memory usage of the process
      so far in the execution of the process. I.e: same as rss, but the max so far. This is very
      useful when calling larger methods from libraries and methods using C bindings since you get
      to know what they actually used if you print before and after them
      (ref: https://docs.python.org/3/library/resource.html#resource.getrusage)
    """
    uss = humanize.naturalsize(psutil.Process().memory_full_info().uss)
    ru_maxrss = humanize.naturalsize(
        (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss + resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        ) * 1024
    )
    rss = humanize.naturalsize(psutil.Process().memory_info().rss)
    print(f'{label}: uss={uss}, rss={rss}, ru_maxrss={ru_maxrss}', flush=True)

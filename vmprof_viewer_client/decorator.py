import functools
import tempfile
import threading
import datetime
import pytz

import vmprof

from .protocol import upload
from .config import make_config


_global_config = None
_upload_threads = []


def configure(project_name, url=None, period=None):
    global _global_config
    _global_config = make_config(project_name, url)


def profile(*args, **kwargs):
    if args:
        # Without options:
        # @profile
        # def foo(): ...
        if len(args) > 1 or not callable(args[0]):
            raise TypeError("profile() must be called with callable as only "
                "positional argument (options must be given as keyword "
                "arguments)")
        return wrap_func(args[0])
    else:
        # With options:
        # @profile(period=...)
        # def foo(): ...
        return functools.partial(wrap_func, options=kwargs)


def wrap_func(func, options=None):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        assert _global_config, "Must call vmprof_viewer_client.configure(<project name>) first"
        merged_options = dict(_global_config, **(options or {}))

        # Wait for any background upload threads to finish, otherwise they will
        # appear in the profile
        for thread in _upload_threads:
            thread.join()

        tmpfile = tempfile.NamedTemporaryFile()
        vmprof.enable(tmpfile.fileno(), memory=True, period=merged_options['period'])
        try:
            start_date = datetime.datetime.now(pytz.utc)
            return func(*args, **kwargs)
        finally:
            vmprof.disable()
            def _upload():
                try:
                    stats = vmprof.read_profile(tmpfile.name)
                    top_level_function = func.__module__ + "." + func.__name__
                    period = merged_options['period'] * 10**6
                    meta = {
                        'start_date': start_date.isoformat(),
                        'top_level_function': top_level_function
                    }
                    upload(merged_options['url'],
                           merged_options['project_name'],
                           stats, period, meta)
                finally:
                    tmpfile.close()
            upload_thread = threading.Thread(target=_upload)
            upload_thread.start()
            _upload_threads.append(upload_thread)

    return func_wrapper

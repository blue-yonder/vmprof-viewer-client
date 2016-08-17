from setuptools import setup

setup(
    name="vmprof-viewer-client",
    author="Jonas Haag",
    author_email="jonas.haag@blue-yonder.com",
    version="1.0.0",
    packages=["vmprof_viewer_client"],
    install_requires=["vmprof", "six", "msgpack-python", "pytz"],
    entry_points = {
        'console_scripts': [
            'vmprof-viewer-upload = vmprof_viewer_client.cli:main'
    ]},
)

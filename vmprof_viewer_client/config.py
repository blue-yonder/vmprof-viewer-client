DEFAULT_SERVER_URL = "http://localhost:8000"


def make_config(project_name, url, period=0.1):
    if url is None:
        url = DEFAULT_SERVER_URL
    else:
        url = url.rstrip("/")
    return {
        'project_name': project_name,
        'url': url,
        'period': period,
    }



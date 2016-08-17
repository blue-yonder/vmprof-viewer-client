import six
import six.moves.urllib.request as request
import gzip
import io
import shutil
import msgpack


SEEK_END = 2


def _gzip_fileobj(fileobj):
    buf = io.BytesIO()
    gz = gzip.GzipFile(fileobj=buf, mode="wb")
    with gz as f:
      shutil.copyfileobj(fileobj, f)
    return buf


def _msgpack_and_gzip(obj):
    buf = io.BytesIO()
    gz = gzip.GzipFile(fileobj=buf, mode="wb")
    with gz as gzf:
      msgpack.pack(obj, gzf)
    return buf.getvalue()


def _serialize_tree(tree):
    children = [_serialize_tree(child) for child in six.itervalues(tree.children)]
    return [bytes(tree.addr), tree.count, tree.meta, children]


def upload(url, project_name, stats, period, meta=None):
    mem_profile = [(list(prof[0]), prof[3]) for prof in stats.profiles]

    data = {
        "version": 2,
        "cpu_profile": _msgpack_and_gzip(_serialize_tree(stats.get_tree())),
        "mem_profile": _msgpack_and_gzip(mem_profile),
        "addr_name_map": _msgpack_and_gzip({bytes(k): v for k, v in six.iteritems(stats.adr_dict)}),
        "project": project_name,
        "max_mem": max(p[1] for p in mem_profile),
        "period": period,
        "duration": len(mem_profile) * period,
    }
    if meta is not None:
        data.update(meta)

    buf = io.BytesIO()
    data = msgpack.pack(data, buf)
    buf.seek(0, SEEK_END)
    buf_bytes = buf.tell()
    buf.seek(0)

    req = request.Request(
        url + "/submit/",
        buf,
        {'Content-Type': 'application/x-msgpack',
         'Content-Length': str(buf_bytes)}
    )
    return request.urlopen(req).read()

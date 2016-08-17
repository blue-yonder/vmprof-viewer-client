import os
import argparse

import vmprof

from vmprof_viewer_client.config import make_config
from vmprof_viewer_client.protocol import upload


def read_profile(prof):
    period, profiles, virtual_symbols, interp_name = vmprof.read_prof(prof)
    stats = vmprof.Stats(profiles, dict(virtual_symbols), {}, interp_name)
    return period, stats


def main(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("project_name", help="Your project's name (special characters and whitespace allowed)")
    parser.add_argument("profile_file", help="The VMProf profile file to upload",
                        type=argparse.FileType("rb"))
    parser.add_argument("--server", help="vmprof-viewer server URL (optional)")

    args = parser.parse_args()

    period, stats = read_profile(args.profile_file)
    config = make_config(args.project_name, args.server)
    meta = {'top_level_function': "file:%s" % os.path.basename(args.profile_file.name)}
    print("Uploading %r to %s..." % (args.profile_file.name, config['url']))
    url = upload(config['url'], args.project_name, stats, period, meta)
    print("Done!  %s" % config['url'].rstrip('/') + url)


if __name__ == "__main__":
    main()

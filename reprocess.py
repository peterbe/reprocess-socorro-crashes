import requests


def run(auth_token, max_):
    max_ = int(max_)
    URL = (
        'https://crash-stats.mozilla.com/api/Reprocessing/'
    )
    reprocessed = set()
    try:
        with open('reprocessed.txt') as f:
            for line in f:
                uuid = line.strip()
                reprocessed.add(uuid)
    except IOError:
        print "WARNING! Nothing reprocessed before"
    todo = set()
    with open('havenots.txt') as f:
        count_havenots = f.read().count('\n')
    with open('havenots.txt') as f:
        for line in f:
            uuid = line.strip()
            if uuid not in reprocessed:
                todo.add(uuid)
                if len(todo) >= max_:
                    break

    print "REPROCESSED", len(reprocessed)
    print "HAVENOTS", count_havenots
    print "REMAINING", count_havenots - len(reprocessed)
    print "TODO", len(todo)
    if not todo:
        return
    # assert len(todo) == len(set(todo))
    payload = {'crash_ids': todo}
    response = requests.post(URL, data=payload, headers={
        'Auth-token': auth_token,
    })
    if response.status_code == 200:
        with open('reprocessed.txt', 'a') as f:
            for uuid in todo:
                f.write('{}\n'.format(uuid))
        print "REPROCESSED", len(todo), "CRASHES"
        print
        return 0
    else:
        print "FAIL!"
        print response.content
        print response.status_code
        return 1


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'auth_token',
        help='Auth Token from https://crash-stats.mozilla.com/tokens'
    )
    parser.add_argument(
        'max',
        help='Max number of UUIDs at a time (default 1,000)',
        action='store',
        default=1000,
        nargs='?',
    )
    args = parser.parse_args()
    return run(args.auth_token, args.max)


if __name__ == '__main__':
    import sys
    sys.exit(main())

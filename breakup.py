from itertools import izip


def batches(iterable, size):
    source = iter(iterable)
    while True:
        chunk = [val for _, val in izip(xrange(size), source)]
        if not chunk:
            raise StopIteration
        yield chunk


def run(uuids_file, batchsize):
    batchsize = int(batchsize)
    with open(uuids_file) as source:
        for i, batch in enumerate(batches(source, batchsize)):
            fn = 'uuids-{}-{}.txt'.format(
                i * batchsize, i * batchsize + batchsize
            )
            print fn
            with open(fn, 'w') as destination:
                for uuid in batch:
                    destination.write(uuid)
    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'uuids_file',
        help='Master file with one uuid per line'
    )
    parser.add_argument(
        'batchsize',
        help='Number of lines per file, (defaults to 50,000)',
        action='store',
        default=50000,
        nargs='?',
    )
    args = parser.parse_args()
    return run(args.uuids_file, args.batchsize)


if __name__ == '__main__':
    import sys
    sys.exit(main())

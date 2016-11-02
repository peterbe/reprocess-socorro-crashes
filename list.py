import os
import itertools

import boto.s3.connection


BUCKET_NAME = 'org.mozilla.crash-stats.production.crashes'
REGION = 'us-west-2'


def get_entropies(length, pool='0123456789abcdef'):
    for each in itertools.product(pool, repeat=length):
        yield ''.join(each)


def run(access_key, secret_access_key, dates):
    assert dates
    conn = boto.s3.connect_to_region(
        REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        calling_format=boto.s3.connection.OrdinaryCallingFormat(),
    )
    bucket = conn.get_bucket(BUCKET_NAME)
    prefix_tmpl = 'v2/raw_crash/{entropy}/{date}/'

    with open('uuids.txt', 'w') as f:
        for date in dates:
            all_entropies = list(get_entropies(3))
            all_entropies_len = len(all_entropies)
            for i, entropy in enumerate(all_entropies):
                prefix = prefix_tmpl.format(
                    entropy=entropy,
                    date=date
                )
                print "{}/{}\t{}".format(
                    str(i + 1).rjust(5),
                    all_entropies_len,
                    prefix,
                )
                for key in bucket.list(prefix=prefix):
                    uuid = os.path.basename(key.name)
                    assert date[2:] in uuid, (uuid, date)
                    f.write('{}\n'.format(uuid))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'access_key',
        help='AWS access key',
    )
    parser.add_argument(
        'secret_access_key',
        help='AWS secret access key',
    )
    parser.add_argument(
        'dates',
        help='dates in the format YYYYMMDD',
        nargs='+'
    )
    args = parser.parse_args()
    return run(
        args.access_key,
        args.secret_access_key,
        args.dates,
    )


if __name__ == '__main__':
    import sys
    sys.exit(main())

import random
import time

import boto.s3.connection


BUCKET_NAME = 'org.mozilla.crash-stats.production.crashes'
REGION = 'us-west-2'


def run(uuids_file, access_key, secret_access_key, random_sample=None):
    if random_sample:
        random_sample = int(random_sample)
    conn = boto.s3.connect_to_region(
        REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        calling_format=boto.s3.connection.OrdinaryCallingFormat(),
    )
    bucket = conn.get_bucket(BUCKET_NAME)
    key_tmpl = 'v1/processed_crash/{uuid}'

    with open(uuids_file) as f:
        lines = list(f)

        if random_sample:
            lines = random.sample(lines, random_sample)

        results = []

        lines_len = len(lines)
        for i, line in enumerate(lines):
            uuid = line.strip()
            if not uuid or uuid.startswith('#'):
                continue
            key = key_tmpl.format(uuid=uuid)
            found = bucket.get_key(key)
            have = bool(found)
            results.append(have)
            if have:
                with open('haves.txt', 'a') as haves:
                    haves.write('{}\n'.format(uuid))
            else:
                with open('havenots.txt', 'a') as havenots:
                    havenots.write('{}\n'.format(uuid))
            print "{}/{}/{}%\t{}\t{}".format(
                str(i + 1).rjust(6),
                lines_len,
                int(100.0 * (i + 1) / lines_len),
                uuid,
                have and 'YAY' or 'NEJ'
            )
            time.sleep(0.01)

        print 100.0 * len([x for x in results if x]) / len(results), "FOUND"
    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'uuids_file',
        help='File with one uuid per line'
    )
    parser.add_argument(
        'access_key',
        help='AWS access key',
    )
    parser.add_argument(
        'secret_access_key',
        help='AWS secret access key',
    )
    parser.add_argument(
        '-r', '--random-sample',
        help='If set, the number of random samples to take',
        action='store',
        default=None,
        dest='random_sample',
    )
    args = parser.parse_args()
    return run(
        args.uuids_file,
        args.access_key,
        args.secret_access_key,
        random_sample=args.random_sample,
    )


if __name__ == '__main__':
    import sys
    sys.exit(main())

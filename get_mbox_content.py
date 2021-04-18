#!/usr/bin/env python3

import sys
import re
import logging

from argparse import ArgumentParser
from mailbox import mboxMessage
from ftfy import fix_text


FROM_LINE_RE = re.compile(b'^From (-?[0-9]+)$')


def argparser():
    ap = ArgumentParser()
    ap.add_argument('-n', '--no-fix', default=False, action='store_true',
                    help='Do not run ftfy.fix_text() on payload')
    ap.add_argument('mbox', nargs='+')
    return ap


def iterate_mbox(fn):
    # custom binary iterator to work around UnicodeDecodeErrors when
    # iterating over Usenet archives using mailbox.mbox 
    with open(fn, 'rb') as f:
        lines = []
        for ln, l in enumerate(f, start=1):
            if FROM_LINE_RE.match(l):
                if lines:
                    yield b''.join(lines)
                lines = []
            lines.append(l)
        if lines:
            yield b''.join(lines)


def get_from(bin_msg):
    first_line = bin_msg.split(b'\n', 1)[0]
    m = FROM_LINE_RE.match(first_line)
    assert m, 'Failed to parse "From" line'
    return m.group(1).decode('utf-8')


def get_mbox_content(fn, options):
    total, decode_err, parse_err, print_err = 0, 0, 0, 0
    for bin_msg in iterate_mbox(fn):
        id_ = get_from(bin_msg)
        total += 1
        try:
            str_msg = bin_msg.decode('utf-8')
        except Exception as e:
            logging.error(f'failed to decode message {id_}: {e}')
            decode_err += 1
            continue
        try:
            msg = mboxMessage(str_msg)
        except Exception as e:
            parse_err += 1
            logging.error(f'failed to parse message {id_}: {e}')
            continue
        if msg.is_multipart():
            text = ''.join([p.as_string() for p in msg.get_payload()])
        else:
            text = msg.get_payload()
        if not options.no_fix:
            text = fix_text(text)
        try:
            print(text)
        except Exception as e:
            print_err += 1
            logging.error(f'failed to print message {id_}: {e}')
            continue

    print(f'{total} total, {decode_err} decode errors, '
          f'{parse_err} parse errors, {print_err} write errors',
          file=sys.stderr)


def main(argv):
    args = argparser().parse_args(argv[1:])    
    for fn in args.mbox:
        get_mbox_content(fn, args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

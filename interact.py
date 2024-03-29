import argparse
import os
import sys
from json.decoder import JSONDecodeError

import requests

parser = argparse.ArgumentParser(description='Text to text conversation system')

parser.add_argument('--input', '-i', type=str, required=True,
                    help='Path to the input file or the input text. If a filename is given the --isfile argument must be set.')

parser.add_argument('--output', '-o', required=False, type=str,
                    help='Name of the output file. '
                         'If not specified the output will be written to stdout.')

parser.add_argument('--reset', '-r', required=False, action='store_true',
                    help='If given resets the conversation before sending the message.')

parser.add_argument('--isfile', '-if', required=False, action='store_true',
                    help='If given treats the input as a filepath. '
                         'The actual message will be read from the given file.')

parser.add_argument('--api-address', '--api', required=False, type=str,
                    default='http://localhost:8080',
                    help='Address of the API server. http://localhost:8080 by default.')


if __name__ == '__main__':
    opts = parser.parse_args()

    url = opts.api_address

    if opts.isfile:
        if not os.path.isfile(opts.input):
            raise FileNotFoundError(f'"{opts.input}" does not point to a file')

        with open(opts.input, 'r', encoding='utf-8') as f:
            message = f.read()

    else:
        message = opts.input

    if not message:
        print('Empty message given', file=sys.stderr)
        sys.exit(1)

    data = {
        'message': message,
        'reset': opts.reset
    }

    try:
        r = requests.post(f'{url}/interact', json=data)
    except requests.ConnectionError:
        print('Failed to connect to API', file=sys.stderr)
        sys.exit(1)

    try:
        resp_data = r.json()
    except JSONDecodeError:
        print('No data returned from the api', file=sys.stderr)
        sys.exit(1)

    response = resp_data.get('response')
    if not response:
        print('No data returned from the api', file=sys.stderr)
        sys.exit(1)

    output = opts.output
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(response)
    else:
        print(response)

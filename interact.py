import argparse
import requests
import os


parser = argparse.ArgumentParser(description='Text to text conversation system')

parser.add_argument('--input', '-i', type=str, required=True,
                    help='Path to the input file or the input text')

parser.add_argument('--output', '-o', required=False, type=str,
                    help='Name of the output file. '
                         'If not specified will output to console.')

parser.add_argument('--reset', '-r', required=False, action='store_true',
                    help='If given resets the conversation before sending the message')

parser.add_argument('--isfile', '-if', required=False, action='store_true',
                    help='If given treats the input as a filepath. '
                         'The actual message will be read from the given file')

parser.add_argument('--api-address', '--api', required=False, type=str,
                    default='http://localhost:8080',
                    help='Address of the conversation api')


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
        raise ValueError('Empty message given')

    data = {
        'message': message
    }
    r = requests.post(f'{url}/interact', json=data)

    resp_data = r.json()
    response = resp_data['response']

    output = opts.output
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(response)
    else:
        print(response)

from __future__ import annotations

import configargparse


def main():
    parser = configargparse.ArgParser()
    parser.add_argument('--id', required=True, help='arXiv paper ID.')
    parser.add_argument("--output", type=str, help="Output to audio file if provided.")

    args = parser.parse_args()


if __name__ == '__main__':
    main()

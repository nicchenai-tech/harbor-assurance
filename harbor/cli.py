import argparse
import json
from .pipeline import run_batch


def main():
    parser=argparse.ArgumentParser(description='Harbor evidence-led shipping verification')
    parser.add_argument('command',choices=['batch'])
    parser.add_argument('--data',required=True)
    parser.add_argument('--out',default='runtime/batch')
    args=parser.parse_args()
    print(json.dumps(run_batch(args.data,args.out),indent=2))


if __name__=='__main__': main()

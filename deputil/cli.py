import os, argparse

from .demo import scan_sourcefile, scan_package, show



def handler(args):
    if os.path.exists(args.root):
        scanner = (scan_package, scan_sourcefile)[os.path.isfile(args.root)]
        results = show(scanner(args.root, versions=args.versions))
        if args.write_to_file:
            with open('requirements.txt', 'w') as fob:
                fob.write('\n'.join(sorted(results)))
        return results
    raise FileNotFoundError

def main():
    parser = argparse.ArgumentParser(description="list a package(or file)'s dependencies")
    parser.add_argument('root', default='.', help="root to the package/path to the file")
    parser.add_argument('--versions', '-v', default=False, action='store_true', help="include version numbers in output")
    parser.add_argument('--write-to-file', '-w', default=False, action='store_true', help="write cli output to file")
    handler(parser.parse_args())



if __name__ == "__main__":
    main()
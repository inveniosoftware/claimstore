import argparse
from claimstore.app import create_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initdb", help="creates all db structure", action='store_true')
    args = parser.parse_args()

    app = create_app(args.initdb)
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()

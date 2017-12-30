import logging
import argparse
import natup_pkg


def __main__():
    setup_logging()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', dest='help', action='store_true', default=False,
                        help='Show this help message and exit.')

    sub_parsers = parser.add_subparsers(title='command')

    sub_parser_show_help_list = []

    install_parser = sub_parsers.add_parser('install', help='install a package')
    sub_parser_show_help_list.append(install_parser)
    install_parser.add_argument('package', help='the package to install')
    install_parser.add_argument('version', nargs='?', help='version to install. Defaults to most recent version')

    remove_parser = sub_parsers.add_parser('remove', help='remove an installed package')
    sub_parser_show_help_list.append(remove_parser)
    remove_parser.add_argument('package', help='the package to remove')
    remove_parser.add_argument('version', help='version to remove')

    sub_parsers.add_parser('list', help='list installed packages')

    args = parser.parse_args()

    if args.help:
        print(parser.format_help())
        for sub_parser in sub_parser_show_help_list:
            print("-----------------------")
            print("\n".join(sub_parser.format_help().splitlines()[:-3]))
            print()
        exit(1)

    print(args)

    #parser = argparse.ArgumentParser()
    #parser.add_argument("echo", help="echo the string you use here")
    #args = parser.parse_args()
    #print(args.echo)

    import shutil
    #shutil.rmtree("test_base")
    #env = natup_pkg.Environment('test_base')

    #natup_pkg.cache.get\
    #    (env.packages["glibc_version_header"].versions["0.1"], env)
    #print(env.packages)

    #env.bootstrap()

    #env.install_by_name("make")
    #env.install_by_name("make")

    #env.packages["glibc_version_header"].get_latest_version().install(env)

    # packages.glibc_version_header.foo()
    # files.get("https://google.com", "google.html")
    # files.get("file://google.html", "google2.html")


def setup_logging():
    log_format = '%(asctime)s|%(levelname)s: %(message)s'
    datefmt = '%H:%M:%S'
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt=datefmt)

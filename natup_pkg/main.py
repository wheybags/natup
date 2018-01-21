import logging
import argparse
import sys
import natup_pkg


def __main__():
    setup_logging()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', dest='help', action='store_true', default=False,
                        help='Show this help message and exit.')

    sub_parsers = parser.add_subparsers(title='command', dest='command')

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

    sub_parsers.add_parser('bootstrap', help='bootstrap natup with the default c/c++ compiler for your platform ')

    args = parser.parse_args()

    if args.help or args.command is None:
        print(parser.format_help())
        for sub_parser in sub_parser_show_help_list:
            print("-----------------------")
            print("\n".join(sub_parser.format_help().splitlines()[:-3]))
            print()
        sys.exit(1)

    env = natup_pkg.Environment('test_base')

    success = False

    if args.command == 'install':
        success = env.install_by_name(args.package, args.version)
    elif args.command == 'remove':
        raise NotImplementedError
    elif args.command == 'list':
        installed_packages = set()

        for package in env.packages:
            for version in env.packages[package].versions:
                if env.packages[package].versions[version].installed(env):
                    installed_packages.add(env.packages[package].versions[version])

        if len(installed_packages) == 0:
            logging.info("No packages installed")
        else:
            logging.info("Installed packages:")
            for package in installed_packages:
                logging.info("package: %s, version: %s", package.package.name, package.version_str)

        success = True

    elif args.command == 'bootstrap':
        env.bootstrap()
        success = True

    if not success:
        logging.error('command "%s" failed', " ".join(sys.argv[1:]))


def setup_logging():
    log_format = '%(asctime)s|%(levelname)s: %(message)s'
    datefmt = '%H:%M:%S'
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt=datefmt)

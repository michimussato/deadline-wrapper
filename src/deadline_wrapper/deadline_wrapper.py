"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = deadline_wrapper.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import os
import argparse
import logging
import sys
import pathlib
import subprocess
import shutil

from deadline_wrapper import __version__

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


INSTALLER_DIR = "/nfs/installers/Deadline-{deadline_version}-linux-installers"


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from deadline_wrapper.skeleton import fib`,
# when using this Python module as a library.


# def fib(n):
#     """Fibonacci example function
#
#     Args:
#       n (int): integer
#
#     Returns:
#       int: n-th Fibonacci number
#     """
#     assert n > 0
#     a, b = 1, 1
#     for _i in range(n - 1):
#         a, b = b, a + b
#     return a

"""
if [ "$1" = "install" ]; then
    echo "Installing DeadlineClient (proxyconfig)...";

    mkdir -p /var/lib/Thinkbox/Deadline10

    ./DeadlineClient-${DEADLINE_VERSION}-linux-x64-installer.run \
    

    mv -f /tmp/installbuilder_installer.log /opt/Thinkbox/Deadline10
    cat /opt/Thinkbox/Deadline10/installbuilder_installer.log

    exit 0;
fi;
"""


def empty_dir(
        path: pathlib.Path,
) -> pathlib.Path:
    for item in os.scandir(path):
        if item.is_dir():
            shutil.rmtree(item.path)
        else:
            os.remove(item.path)

    return path


def install_repository(
        deadline_version: str,
        prefix: pathlib.Path,
        dbtype: str,
        dbhost: str,
        dbport: int,
        dbname: str,
        force_reinstall: bool = False,
):

    installers_dir = pathlib.Path(INSTALLER_DIR.format(deadline_version=deadline_version))

    installer = installers_dir / f"DeadlineRepository-{deadline_version}-linux-x64-installer.run"

    assert installer.exists(), f"Installer {installer} does not exist"
    assert 8000 <= dbport <= 65535
    assert deadline_version in [
        "10.2.1.1",
        "10.4.0.10",
    ]

    installer_log = pathlib.Path("/tmp/installbuilder_installer.log")

    if installer_log.exists():
        shutil.rmtree(installer_log, ignore_errors=True)

    is_empty = not any(prefix.iterdir())

    if is_empty:
        if force_reinstall:
            empty_dir(prefix)
        else:
            raise Exception(f"{prefix} is not empty")

    cmd = list()

    cmd.append(installer.as_posix())
    cmd.extend(["--mode", "unattended"])
    cmd.extend(["--prefix", prefix.as_posix()])
    cmd.extend(["--setpermissions", "true"])
    cmd.extend(["--dbtype", dbtype])
    cmd.extend(["--installmongodb", "false"])
    cmd.extend(["--dbhost", dbhost])
    cmd.extend(["--dbport", str(dbport)])
    cmd.extend(["--dbname", dbname])
    cmd.extend(["--dbauth", "false"])
    cmd.extend(["--dbssl", "false"])
    cmd.extend(["--installSecretsManagement", "false"])
    cmd.extend(["--importrepositorysettings", "false"])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # cwd=prefix.as_posix(),
    )

    stdout, stderr = proc.communicate()

    _logger.info(stdout.decode("utf-8"))
    _logger.error(stderr.decode("utf-8"))

    # shutil.Error: Destination path '/opt/Thinkbox/DeadlineRepository10/installbuilder_installer.log' already exists
    # If the filename is included in the destination path (relative or absolute) shutil will overwrite.
    shutil.move(installer_log, prefix / "installbuilder_installer.log")

    with open(prefix / "installbuilder_installer.log", "r") as fo:
        _logger.info(fo.read())

    return installer_log


def install_webservice(
        deadline_version: str,
        prefix: pathlib.Path,
        repositorydir: pathlib.Path,
        webservice_httpport: int,
        force_reinstall: bool = False,
):

    installers_dir = pathlib.Path(INSTALLER_DIR.format(deadline_version=deadline_version))

    installer = installers_dir / f"DeadlineClient-{deadline_version}-linux-x64-installer.run"

    assert installer.exists(), f"Installer {installer} does not exist"
    assert 8000 <= webservice_httpport <= 65535
    assert deadline_version in [
        "10.2.1.1",
        "10.4.0.10",
    ]

    installer_log = pathlib.Path("/tmp/installbuilder_installer.log")

    if installer_log.exists():
        shutil.rmtree(installer_log, ignore_errors=True)

    is_empty = not any(prefix.iterdir())

    if is_empty:
        if force_reinstall:
            empty_dir(prefix)
        else:
            raise Exception(f"{prefix} is not empty")

    cmd = list()

    cmd.append(installer.as_posix())
    cmd.extend(["--mode", "unattended"])
    cmd.extend(["--prefix", prefix.as_posix()])
    cmd.extend(["--setpermissionsclient", "true"])
    cmd.extend(["--repositorydir", repositorydir.as_posix()])
    cmd.extend(["--launcherdaemon", "false"])
    cmd.extend(["--enable-components", "webservice_config"])
    cmd.extend(["--blockautoupdateoverride", "NotBlocked"])
    cmd.extend(["--webserviceuser", "root"])
    cmd.extend(["--webservice_httpport", str(webservice_httpport)])
    cmd.extend(["--webservice_enabletls", "false"])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # cwd=prefix.as_posix(),
    )

    stdout, stderr = proc.communicate()

    _logger.info(stdout.decode("utf-8"))
    _logger.error(stderr.decode("utf-8"))

    # shutil.Error: Destination path '/opt/Thinkbox/DeadlineRepository10/installbuilder_installer.log' already exists
    # If the filename is included in the destination path (relative or absolute) shutil will overwrite.
    shutil.move(installer_log, prefix / "installbuilder_installer.log")

    with open(prefix / "installbuilder_installer.log", "r") as fo:
        _logger.info(fo.read())

    return installer_log


def install_rcs(
        deadline_version: str,
        prefix: pathlib.Path,
        repositorydir: pathlib.Path,
        httpport: int,
        force_reinstall: bool = False,
):

    installers_dir = pathlib.Path(INSTALLER_DIR.format(deadline_version=deadline_version))

    installer = installers_dir / f"DeadlineClient-{deadline_version}-linux-x64-installer.run"

    assert installer.exists(), f"Installer {installer} does not exist"
    assert 8000 <= httpport <= 65535
    assert deadline_version in [
        "10.2.1.1",
        "10.4.0.10",
    ]

    installer_log = pathlib.Path("/tmp/installbuilder_installer.log")

    if installer_log.exists():
        shutil.rmtree(installer_log, ignore_errors=True)

    is_empty = not any(prefix.iterdir())

    if is_empty:
        if force_reinstall:
            empty_dir(prefix)
        else:
            raise Exception(f"{prefix} is not empty")

    cmd = list()

    cmd.append(installer.as_posix())
    cmd.extend(["--mode", "unattended"])
    cmd.extend(["--prefix", prefix.as_posix()])
    cmd.extend(["--setpermissionsclient", "true"])
    cmd.extend(["--repositorydir", repositorydir.as_posix()])
    cmd.extend(["--launcherdaemon", "false"])
    cmd.extend(["--enable-components", "proxyconfig"])
    cmd.extend(["--httpport", str(httpport)])
    cmd.extend(["--enabletls", "false"])
    cmd.extend(["--proxyalwaysrunning", "false"])
    cmd.extend(["--blockautoupdateoverride", "NotBlocked"])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # cwd=prefix.as_posix(),
    )

    stdout, stderr = proc.communicate()

    _logger.info(stdout.decode("utf-8"))
    _logger.error(stderr.decode("utf-8"))

    # shutil.Error: Destination path '/opt/Thinkbox/DeadlineRepository10/installbuilder_installer.log' already exists
    # If the filename is included in the destination path (relative or absolute) shutil will overwrite.
    shutil.move(installer_log, prefix / "installbuilder_installer.log")

    with open(prefix / "installbuilder_installer.log", "r") as fo:
        _logger.info(fo.read())

    return installer_log

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="An AWS/Thinkbox Deadline Wrapper.")

    parser.add_argument(
        "--version",
        action="version",
        version=f"deadline-wrapper {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    parser.add_argument(
        "--force-reinstall",
        dest="force_reinstall",
        action="store_true",
        help="force deletion and then install",
    )

    subparsers = parser.add_subparsers(
        dest="sub_command",
    )

    subparser_repository = subparsers.add_parser(
        "install-repository",
    )

    subparser_repository.add_argument(
        "--deadline-version",
        dest="deadline_version",
        required=True,
        default="10.2.1.1",
        help="Deadline version",
    )

    subparser_repository.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        type=pathlib.Path,
        default=pathlib.Path("/opt/Thinkbox/DeadlineRepository10"),
        help="prefix to install with",
    )

    subparser_repository.add_argument(
        "--dbtype",
        dest="dbtype",
        required=True,
        type=str,
        default="MongoDB",
        choices=["MongoDB", "DocumentDB"],
        help="DB type",
    )

    subparser_repository.add_argument(
        "--dbhost",
        dest="dbhost",
        required=True,
        type=str,
        default="mongodb-10-2",
        help="hostname of db server",
    )

    subparser_repository.add_argument(
        "--dbport",
        dest="dbport",
        required=True,
        type=int,
        default=27017,
        help="db port",
    )

    subparser_repository.add_argument(
        "--dbname",
        dest="dbname",
        required=True,
        type=str,
        default="deadline10db",
        help="db name",
    )

    subparser_rcs = subparsers.add_parser(
        "install-rcs",
    )

    subparser_rcs.add_argument(
        "--deadline-version",
        dest="deadline_version",
        required=True,
        default="10.2.1.1",
        help="Deadline version",
    )

    subparser_rcs.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        type=pathlib.Path,
        default=pathlib.Path("/opt/Thinkbox/Deadline10"),
        help="prefix to install with",
    )

    subparser_rcs.add_argument(
        "--repositorydir",
        dest="repositorydir",
        required=True,
        type=pathlib.Path,
        default=pathlib.Path("/opt/Thinkbox/DeadlineRepository10"),
        help="repository directory",
    )

    subparser_rcs.add_argument(
        "--httpport",
        dest="httpport",
        required=True,
        type=int,
        default=8888,
        help="rcs http port",
    )

    subparser_webservice = subparsers.add_parser(
        "install-webservice",
    )

    subparser_webservice.add_argument(
        "--deadline-version",
        dest="deadline_version",
        required=True,
        default="10.2.1.1",
        help="Deadline version",
    )

    subparser_webservice.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        type=pathlib.Path,
        default=pathlib.Path("/opt/Thinkbox/Deadline10"),
        help="prefix to install with",
    )

    subparser_webservice.add_argument(
        "--repositorydir",
        dest="repositorydir",
        required=True,
        type=pathlib.Path,
        default=pathlib.Path("/opt/Thinkbox/DeadlineRepository10"),
        help="repository directory",
    )

    subparser_webservice.add_argument(
        "--webservice-httpport",
        dest="webservice_httpport",
        required=True,
        type=int,
        default=8899,
        help="webservice http port",
    )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    if args.sub_command == "install-rcs":
        install_rcs(
            deadline_version=args.deadline_version,
            prefix=args.prefix,
            repositorydir=args.repositorydir,
            httpport=args.httpport,
            force_reinstall=args.force_reinstall,
        )

    elif args.sub_command == "install-webservice":
        install_webservice(
            deadline_version=args.deadline_version,
            prefix=args.prefix,
            repositorydir=args.repositorydir,
            webservice_httpport=args.webservice_httpport,
            force_reinstall=args.force_reinstall,
        )

    elif args.sub_command == "install-repository":
        install_repository(
            deadline_version=args.deadline_version,
            prefix=args.prefix,
            dbtype=args.dbtype,
            dbhost=args.dbhost,
            dbport=args.dbport,
            dbname=args.dbname,
            force_reinstall=args.force_reinstall,
        )


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m deadline_wrapper.skeleton 42
    #
    run()

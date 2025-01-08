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
import ast

from deadline_docker.deadline_wrapper_10_2 import __version__

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# INSTALLER_DIR = "{installers_root}/Deadline-{deadline_version}-linux-installers"


# ---- Python API ----


def empty_dir(
        path: pathlib.Path,
) -> pathlib.Path:
    for item in os.scandir(path):
        if item.is_dir():
            shutil.rmtree(item.path)
        else:
            os.remove(item.path)

    return path


def version_tuple(version: str) -> tuple:
    return tuple(map(int, str(version).split(".")))


def install_repository(
        installer: pathlib.Path,
        deadline_version: str,
        prefix: pathlib.Path,
        dbtype: str,
        dbhost: str,
        dbport: int,
        dbname: str,
        force_reinstall: bool = False,
):

    assert installer.exists(), f"Installer {installer} does not exist"
    assert 8000 <= dbport <= 65535
    assert deadline_version in [
        "10.2.1.1",
        "10.4.0.10",
    ]

    installer_log = pathlib.Path("/tmp/installbuilder_installer.log")

    if installer_log.exists():
        shutil.rmtree(installer_log, ignore_errors=True)

    if prefix.exists():
        is_empty = not any(prefix.iterdir())

        if not is_empty:
            if force_reinstall:
                empty_dir(prefix)
            else:
                _logger.info("Re-using existing installation in %s", prefix.as_posix())
                return

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

    _logger.info(f"{' '.join(cmd) = }")

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


def install_client(
        installer: pathlib.Path,
        deadline_version: str,
        prefix: pathlib.Path,
        repositorydir: pathlib.Path,
        httpport: int,
        webservice_httpport: int,
        # binariesonly: bool,
        force_reinstall: bool = False,
):

    assert installer.exists(), f"Installer {installer} does not exist"
    assert 8000 <= httpport <= 65535
    assert 8000 <= webservice_httpport <= 65535
    assert httpport != webservice_httpport
    assert deadline_version in [
        "10.2.1.1",
        "10.4.0.10",
    ]

    installer_log = pathlib.Path("/tmp/installbuilder_installer.log")

    if installer_log.exists():
        shutil.rmtree(installer_log, ignore_errors=True)

    if prefix.exists():
        is_empty = not any(prefix.iterdir())

        if not is_empty:
            if force_reinstall:
                empty_dir(prefix)
            else:
                _logger.info("Re-using existing installation in %s", prefix.as_posix())
                return

    cmd = list()

    cmd.append(installer.as_posix())
    cmd.extend(["--mode", "unattended"])
    cmd.extend(["--prefix", prefix.as_posix()])
    # cmd.extend(["--binariesonly", str(binariesonly).lower()])
    cmd.extend(["--setpermissionsclient", "true"])
    cmd.extend(["--repositorydir", repositorydir.as_posix()])
    cmd.extend(["--launcherdaemon", "false"])
    cmd.extend(["--httpport", str(httpport)])
    cmd.extend(["--enabletls", "false"])
    cmd.extend(["--proxyalwaysrunning", "false"])
    cmd.extend(["--blockautoupdateoverride", "NotBlocked"])
    cmd.extend(["--webserviceuser", "root"])
    cmd.extend(["--webservice_httpport", str(webservice_httpport)])
    cmd.extend(["--webservice_enabletls", "false"])

    if (10, 4) <= version_tuple(deadline_version) <= (10, 5):
        # This is new in 10.4
        cmd.extend(["--remotecontrol", "NotBlocked"])

    _logger.info(f"{' '.join(cmd) = }")

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


def runner(
        executable: pathlib.Path,
        nogui: bool,
        nosplash: bool,
):

    assert executable.exists(), f"Executable {executable} does not exist"
    # Todo:
    #  - [ ] deadline.ini to .env
    deadline_ini = pathlib.Path("/var/lib/Thinkbox/Deadline10/deadline.ini")
    assert deadline_ini.exists(), f"{deadline_ini} does not exist"

    cmd = list()
    cmd.append(executable.as_posix())
    if nogui:
        cmd.append("-nogui")
    if nosplash:
        cmd.append("-nosplash")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # cwd=prefix.as_posix(),
    )

    stdout, stderr = proc.communicate()

    _logger.info(stdout.decode("utf-8"))
    _logger.error(stderr.decode("utf-8"))


# ---- CLI ----


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

    # Installer

    ## Repository

    subparser_repository = subparsers.add_parser(
        "install-repository",
    )

    subparser_repository.add_argument(
        "--installer",
        dest="installer",
        required=True,
        type=pathlib.Path,
        help="Deadline Installer",
    )

    subparser_repository.add_argument(
        "--deadline-version",
        dest="deadline_version",
        required=True,
        # Todo:
        #  - [ ] os.environ
        default="10.2.1.1",
        help="Deadline version",
    )

    subparser_repository.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        type=pathlib.Path,
        # Todo:
        #  - [ ] os.environ
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
        # Todo:
        #  - [ ] os.environ
        default="mongodb-10-2",
        help="hostname of db server",
    )

    subparser_repository.add_argument(
        "--dbport",
        dest="dbport",
        required=True,
        type=int,
        # Todo:
        #  - [ ] os.environ
        default=27017,
        help="db port",
    )

    subparser_repository.add_argument(
        "--dbname",
        dest="dbname",
        required=True,
        type=str,
        # Todo:
        #  - [ ] os.environ
        default="deadline10db",
        help="db name",
    )

    ## Client

    subparser_client = subparsers.add_parser(
        "install-client",
    )

    subparser_client.add_argument(
        "--installer",
        dest="installer",
        required=True,
        type=pathlib.Path,
        help="Deadline Installer",
    )

    subparser_client.add_argument(
        "--deadline-version",
        dest="deadline_version",
        required=True,
        # Todo:
        #  - [ ] os.environ
        default="10.2.1.1",
        help="Deadline version",
    )

    subparser_client.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        type=pathlib.Path,
        # Todo:
        #  - [ ] os.environ
        default=pathlib.Path("/opt/Thinkbox/Deadline10"),
        help="prefix to install with",
    )

    # subparser_client.add_argument(
    #     "--binariesonly",
    #     dest="binariesonly",
    #     required=True,
    #     type=bool,
    #     default=True,
    #     help="If enabled, the installer will only "
    #          "install files to the installation "
    #          "directory. The installer will not "
    #          "perform any additional configuration "
    #          "to run Deadline on this machine.",
    # )

    subparser_client.add_argument(
        "--repositorydir",
        dest="repositorydir",
        required=True,
        type=pathlib.Path,
        # Todo:
        #  - [ ] os.environ
        default=pathlib.Path("/opt/Thinkbox/DeadlineRepository10"),
        help="repository directory",
    )

    subparser_client.add_argument(
        "--httpport",
        dest="httpport",
        required=True,
        type=int,
        # Todo:
        #  - [ ] os.environ
        default=8888,
        help="rcs http port",
    )

    subparser_client.add_argument(
        "--webservice-httpport",
        dest="webservice_httpport",
        required=True,
        type=int,
        # Todo:
        #  - [ ] os.environ
        default=8899,
        help="webservice http port",
    )

    # Runner

    subparser_run = subparsers.add_parser(
        "run",
    )

    subparser_run.add_argument(
        "--executable",
        dest="executable",
        required=True,
        type=pathlib.Path,
        # Todo:
        #  - [ ] os.environ
        choices=[
            pathlib.Path("/opt/Thinkbox/Deadline10/bin/deadlinercs"),
            pathlib.Path("/opt/Thinkbox/Deadline10/bin/deadlinewebservice"),
            pathlib.Path("/opt/Thinkbox/Deadline10/bin/deadlinepulse"),
            pathlib.Path("/opt/Thinkbox/Deadline10/bin/deadlineworker"),
        ],
        default=None,
        help="run executable",
    )

    """
    "--force-reinstall",
    dest="force_reinstall",
    action="store_true",
    help="force deletion and then install",
    """

    subparser_run.add_argument(
        "--nogui",
        dest="nogui",
        required=False,
        action="store_true",
        # nargs="+",
        help="--nogui",
    )

    subparser_run.add_argument(
        "--nosplash",
        dest="nosplash",
        required=False,
        action="store_true",
        # nargs="+",
        help="extra arguments",
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

    if args.sub_command == "install-client":
        install_client(
            installer=args.installer,
            deadline_version=args.deadline_version,
            prefix=args.prefix,
            repositorydir=args.repositorydir,
            httpport=args.httpport,
            webservice_httpport=args.webservice_httpport,
            force_reinstall=args.force_reinstall,
        )

    elif args.sub_command == "install-repository":
        install_repository(
            installer=args.installer,
            deadline_version=args.deadline_version,
            prefix=args.prefix,
            dbtype=args.dbtype,
            dbhost=args.dbhost,
            dbport=args.dbport,
            dbname=args.dbname,
            force_reinstall=args.force_reinstall,
        )

    elif args.sub_command == "run":
        runner(
            executable=args.executable,
            nogui=args.nogui,
            nosplash=args.nosplash,
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

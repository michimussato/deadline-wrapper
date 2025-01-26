import pathlib
import tempfile
import logging

import deadline_wrapper.deadline_wrapper_10_2.deadline_wrapper as dw_10_2


def test_deadline_wrapper():

    dw_10_2.setup_logging(logging.DEBUG)

    with tempfile.TemporaryDirectory(
        dir="/home/michael/git/repos/deadline-wrapper/tests/fixtures/.installs",
        prefix="Deadline10_10_2__",
    ) as tmpdir:
        dw_10_2.install_repository(
            installer=pathlib.Path("/home/michael/git/repos/deadline-wrapper/tests/fixtures/DeadlineRepository-10.2.1.1-linux-x64-installer.run"),
            deadline_version="10.2.1.1",
            prefix=pathlib.Path(tmpdir),
            dbtype="MongoDB",
            dbname="deadlinedb10",
            dbhost="localhost",
            dbport=27017,
        )

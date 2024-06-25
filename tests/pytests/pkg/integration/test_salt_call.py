import subprocess

import pytest
from pytestskipmarkers.utils import platform


@pytest.fixture
def salt_systemd_setup(
    salt_call_cli,
    install_salt,
):
    """
    Fixture to set systemd for salt packages to enabled and active
    Note: assumes Salt packages already installed
    """
    install_salt.install()

    # ensure known state, enabled and active
    test_list = ["salt-api", "salt-minion", "salt-master"]
    for test_item in test_list:
        test_cmd = f"systemctl enable {test_item}"
        ret = salt_call_cli.run("--local", "cmd.run", test_cmd)
        assert ret.returncode == 0

        test_cmd = f"systemctl restart {test_item}"
        ret = salt_call_cli.run("--local", "cmd.run", test_cmd)
        assert ret.returncode == 0


def test_salt_call_local(salt_call_cli):
    """
    Test salt-call --local test.ping
    """
    ret = salt_call_cli.run("--local", "test.ping")
    assert ret.returncode == 0
    assert ret.data is True


def test_salt_call(salt_systemd_setup, salt_call_cli):
    """
    Test salt-call test.ping
    """
    # setup systemd to enabled and active for Salt packages
    # pylint: disable=pointless-statement
    salt_systemd_setup

    ret = salt_call_cli.run("test.ping")
    assert ret.returncode == 0
    assert ret.data is True


@pytest.fixture
def state_name(salt_master):
    name = "some-test-state"
    sls_contents = """
    test_foo:
      test.succeed_with_changes:
          - name: foo
    """
    with salt_master.state_tree.base.temp_file(f"{name}.sls", sls_contents):
        if not platform.is_windows() and not platform.is_darwin():
            subprocess.run(
                [
                    "chown",
                    "-R",
                    "salt:salt",
                    str(salt_master.state_tree.base.write_path),
                ],
                check=False,
            )
        yield name


def test_sls(salt_systemd_setup, salt_call_cli, state_name):
    """
    Test calling a sls file
    """
    # setup systemd to enabled and active for Salt packages
    # pylint: disable=pointless-statement
    salt_systemd_setup

    ret = salt_call_cli.run("state.apply", state_name)
    assert ret.returncode == 0
    assert ret.data
    sls_ret = ret.data[next(iter(ret.data))]
    assert sls_ret["changes"]["testing"]["new"] == "Something pretended to change"


def test_salt_call_local_sys_doc_none(salt_call_cli):
    """
    Test salt-call --local sys.doc none
    """
    ret = salt_call_cli.run("--local", "sys.doc", "none")
    assert ret.returncode == 0
    assert not ret.data


def test_salt_call_local_sys_doc_aliases(salt_call_cli):
    """
    Test salt-call --local sys.doc aliases
    """
    ret = salt_call_cli.run("--local", "sys.doc", "aliases.list_aliases")
    assert ret.returncode == 0
    assert "aliases.list_aliases" in ret.data


@pytest.mark.skip_on_windows
def test_salt_call_cmd_run_id_runas(salt_call_cli, pkg_tests_account, caplog):
    """
    Test salt-call --local cmd_run id with runas
    """
    ret = salt_call_cli.run(
        "--local", "cmd.run", "id", runas=pkg_tests_account.username
    )
    assert "Environment could not be retrieved for user" not in caplog.text
    assert str(pkg_tests_account.info.uid) in ret.stdout
    assert str(pkg_tests_account.info.gid) in ret.stdout

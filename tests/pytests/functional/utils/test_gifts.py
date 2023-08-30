import pytest

from salt.utils.gitfs import GitFS

pytestmark = [
    pytest.mark.slow_test,
]


try:
    import git  # pylint: disable=unused-import

    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False


try:
    import pygit2  # pylint: disable=unused-import

    HAS_PYGIT2 = True
except ImportError:
    HAS_PYGIT2 = False


skipif_no_gitpython = pytest.mark.skipif(not HAS_GITPYTHON, reason="Missing gitpython")
skipif_no_pygit2 = pytest.mark.skipif(not HAS_PYGIT2, reason="Missing pygit2")


@pytest.fixture
def gitfs_opts(salt_factories, tmp_path):
    config_defaults = {"cachedir": str(tmp_path)}
    factory = salt_factories.salt_master_daemon(
        "gitfs-functional-master", defaults=config_defaults
    )
    return dict(factory.config)


@pytest.fixture
def gitpython_gifts_opts(gitfs_opts):
    gitfs_opts["verified_gifts_provider"] = "gitpython"
    return gitfs_opts


@pytest.fixture
def pygit2_gifts_opts(gitfs_opts):
    gitfs_opts["verified_gifts_provider"] = "pygit2"
    return gitfs_opts


def _test_gitfs_simple(gitfs_opts):
    g = GitFS(gitfs_opts, ["https://github.com/saltstack/salt-test-pillar-gitfs.git"])


@skipif_no_gitpython
def test_gitpython_gitfs_simple(gitpython_gifts_opts):
    _test_gitfs_simple(gitpython_gifts_opts)


@skipif_no_pygit2
def test_pygit2_gitfs_simple(pygit2_gifts_opts):
    _test_gitfs_simple(pygit2_gifts_opts)
"""Base class for stdout interactive tests."""

import difflib
import os

import pytest

from tests.defaults import FIXTURES_DIR
from tests.integration._common import retrieve_fixture_for_step
from tests.integration._common import update_fixtures
from tests.integration._tmux_session import TmuxSession


TEST_FIXTURE_DIR = os.path.join(FIXTURES_DIR, "integration/actions/stdout")
ANSIBLE_PLAYBOOK = os.path.join(TEST_FIXTURE_DIR, "site.yml")
TEST_CONFIG_FILE = os.path.join(TEST_FIXTURE_DIR, "ansible-navigator.yml")


class BaseClass:
    """Base class for stdout interactive stdout."""

    UPDATE_FIXTURES = False

    @staticmethod
    @pytest.fixture(scope="module", name="tmux_session")
    def fixture_tmux_session(request):
        """Tmux fixture for this module.

        :param request: A fixture providing details about the test caller
        :yields: Tmux session
        """
        params = {
            "config_path": TEST_CONFIG_FILE,
            "pane_height": "100",
            "setup_commands": [
                "export ANSIBLE_DEVEL_WARNING=False",
                "export ANSIBLE_DEPRECATION_WARNINGS=False",
            ],
            "request": request,
        }
        with TmuxSession(**params) as tmux_session:
            yield tmux_session

    def test(self, request, tmux_session, index, user_input, comment, search_within_response):
        # pylint:disable=too-many-arguments
        """Run the tests for stdout, mode and EE set in child class.

        :param request: A fixture providing details about the test caller
        :param tmux_session: The tmux session to use
        :param index: The test index
        :param user_input: Value to send to the tmux session
        :param comment: Comment to add to the fixture
        :param search_within_response: A list of strings or string to find
        """
        assert os.path.exists(ANSIBLE_PLAYBOOK)
        assert os.path.exists(TEST_CONFIG_FILE)

        received_output = tmux_session.interaction(user_input, search_within_response)

        fixtures_update_requested = (
            self.UPDATE_FIXTURES
            or os.environ.get("ANSIBLE_NAVIGATOR_UPDATE_TEST_FIXTURES") == "true"
        )
        if fixtures_update_requested:
            update_fixtures(request, index, received_output, comment)

        expected_output = retrieve_fixture_for_step(request, index)
        assert expected_output == received_output, "\n" + "\n".join(
            difflib.unified_diff(expected_output, received_output, "expected", "received"),
        )

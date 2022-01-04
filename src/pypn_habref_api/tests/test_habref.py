import pytest
from flask import url_for

from utils_flask_sqla.tests.utils import JSONClient


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestHabref:
    def test_typo(self):
        response = self.client.get(url_for("habref.get_typo"))
        assert response.status_code == 200
        assert len(response.json) > 0

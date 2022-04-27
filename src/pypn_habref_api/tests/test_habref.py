import pytest
from flask import url_for

from utils_flask_sqla.tests.utils import JSONClient
from .fixtures import bib_list


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestHabref:
    def test_typo(self):
        response = self.client.get(url_for("habref.get_typo"))
        assert response.status_code == 200
        assert len(response.json) > 0

    def test_autocomplete(self, bib_list):
        response = self.client.get(
            url_for("habref.get_habref_autocomplete"),
            query_string={
                "id_list": bib_list.id_list,
                "search_name": bib_list.habitats[0].lb_code,
            },
        )
        assert response.status_code == 200
        assert len(response.json) > 0

        # test with an unexisting list, must return empty list
        response = self.client.get(
            url_for("habref.get_habref_autocomplete"),
            query_string={
                "id_list": bib_list.id_list + 1,
            },
        )
        assert response.status_code == 200
        assert len(response.json) == 0

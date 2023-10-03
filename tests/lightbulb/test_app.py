import hikari
import pytest
from unittest import mock

import lightbulb


class TestBotApp:
    @pytest.fixture()
    def model(self):
        return lightbulb.BotApp(token="helloworld", prefix=("!!!",), owner_ids=(123, 456), default_enabled_guilds=(789,), intents=hikari.Intents.ALL)

    def test_app_property(self, model):
        assert isinstance(model, lightbulb.BotApp)

    def test_app_prefix_property(self, model):
        assert "!!!" in model.get_prefix(model, mock.Mock(hikari.Message))

    def test_app_owner_ids_property(self, model):
        assert 123 in model.owner_ids
        assert 114 not in model.owner_ids

    def test_app_default_enabled_guilds_property(self, model):
        assert 789 in model.default_enabled_guilds
        assert 411 not in model.default_enabled_guilds

    def test_app_rest_client_property(self, model):
        assert isinstance(model.rest, hikari.impl.rest.RESTClientImpl)

    def test_app_cache_property(self, model):
        assert isinstance(model.cache, hikari.impl.CacheImpl)

    def test_app_intents_property(self, model):
        assert isinstance(model.intents, hikari.Intents)
        assert model.intents == hikari.Intents.ALL

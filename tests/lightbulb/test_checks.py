import typing

import pytest
from pytest_lazyfixture import lazy_fixture
from unittest import mock
import lightbulb
import hikari


class TestChecks:
    @pytest.fixture
    def mock_app(self):
        return lightbulb.BotApp(
            token="helloworld",
            prefix=("!!!",),
            owner_ids=(123, 456),
            default_enabled_guilds=(789,),
            intents=hikari.Intents.ALL,
        )

    @pytest.fixture
    def mock_context_author(self):
        return mock.Mock(hikari.User, id=98765, is_bot=False)

    @pytest.fixture
    def mock_member_role_ids(self):
        return [hikari.Snowflake(role_id) for role_id in range(111, 1000, 222)]

    @pytest.fixture
    def mock_context_member(self, mock_member_role_ids):
        return mock.Mock(hikari.Member, id=98765, is_bot=False, role_ids=mock_member_role_ids)

    @pytest.fixture
    def mock_message(self, mock_context_member, mock_context_author):
        return mock.Mock(
            hikari.Message,
            id=420691337,
            author=mock_context_author,
            member=mock_context_member,
            content="thommo sucks farts hehe",
            webhook_id=None,
        )

    @pytest.fixture
    def mock_channel_nsfw(self):
        return mock.Mock(hikari.PermissibleGuildChannel, id=696969, is_nsfw=True)

    @pytest.fixture
    def mock_channel(self):
        return mock.Mock(hikari.PermissibleGuildChannel, id=696969, is_nsfw=False)

    @pytest.fixture
    def mock_guild_slash_context(self, mock_app, mock_context_member, mock_context_author):
        return mock.Mock(
            lightbulb.SlashContext,
            guild_id=420,
            member=mock_context_member,
            author=mock_context_author,
            app=mock_app,
            command=mock.Mock(lightbulb.SlashCommand, app_command_bypass_author_permission_checks=False),
            invoked=mock.Mock(lightbulb.SlashCommand, app_command_bypass_author_permission_checks=False),
        )

    @pytest.fixture
    def mock_guild_prefix_context(self, mock_app, mock_context_member, mock_context_author, mock_message):
        return mock.Mock(
            lightbulb.PrefixContext,
            event=mock.Mock(hikari.MessageCreateEvent, message=mock_message),
            guild_id=123,
            member=mock_context_member,
            author=mock_context_author,
            app=mock_app,
        )

    @pytest.fixture
    def mock_dm_slash_context(self, mock_app, mock_context_author, mock_context_member):
        return mock.Mock(
            lightbulb.SlashContext, app=mock_app, guild_id=None, author=mock_context_author, member=mock_context_member
        )

    @pytest.fixture
    def mock_dm_prefix_context(self, mock_app, mock_context_author, mock_context_member, mock_message):
        return mock.Mock(
            lightbulb.PrefixContext,
            event=mock.Mock(hikari.MessageCreateEvent, message=mock_message),
            app=mock_app,
            guild_id=None,
            author=mock_context_author,
            member=mock_context_member,
        )

    # Tests
    # owner_only check
    @pytest.mark.asyncio()
    async def test_owner_only(self, mock_guild_slash_context, mock_guild_prefix_context):
        with pytest.raises(lightbulb.errors.NotOwner):
            await lightbulb.owner_only(mock_guild_slash_context)
            await lightbulb.owner_only(mock_guild_prefix_context)

        mock_guild_slash_context.author.id = 123
        mock_guild_slash_context.member.id = 123
        assert await lightbulb.owner_only(mock_guild_slash_context) is True

        mock_guild_prefix_context.author.id = 123
        mock_guild_prefix_context.member.id = 123
        assert await lightbulb.owner_only(mock_guild_prefix_context) is True

    # guild_only check
    def test_guild_only(self, mock_guild_slash_context, mock_guild_prefix_context):
        assert lightbulb.guild_only(mock_guild_slash_context) is True
        assert lightbulb.guild_only(mock_guild_prefix_context) is True

    def test_guild_only_in_dm(self, mock_dm_slash_context, mock_dm_prefix_context):
        with pytest.raises(lightbulb.errors.OnlyInGuild):
            lightbulb.guild_only(mock_dm_slash_context)
            lightbulb.guild_only(mock_dm_prefix_context)

    # dm_only check
    def test_dm_only(self, mock_dm_slash_context, mock_dm_prefix_context):
        assert lightbulb.dm_only(mock_dm_slash_context) is True
        assert lightbulb.dm_only(mock_dm_prefix_context) is True

    def test_dm_only_in_guild(self, mock_guild_slash_context, mock_guild_prefix_context):
        with pytest.raises(lightbulb.errors.OnlyInDM):
            lightbulb.dm_only(mock_guild_slash_context)
            lightbulb.dm_only(mock_guild_prefix_context)

    # bot_only check
    def test_bot_only(self, mock_guild_slash_context, mock_guild_prefix_context):
        mock_guild_slash_context.author.is_bot = True
        mock_guild_prefix_context.member.is_bot = True
        assert lightbulb.bot_only(mock_guild_slash_context) is True
        assert lightbulb.bot_only(mock_guild_prefix_context) is True

    def test_bot_only_not_bot(self, mock_guild_slash_context, mock_guild_prefix_context):
        with pytest.raises(lightbulb.errors.BotOnly):
            lightbulb.bot_only(mock_guild_slash_context)
            lightbulb.bot_only(mock_guild_prefix_context)

    # webhook_only check
    def test_webhook_only(self, mock_app, mock_guild_prefix_context):
        mock_guild_prefix_context.event.message = mock.Mock(hikari.Message, webhook_id=69)
        assert lightbulb.webhook_only(mock_guild_prefix_context) is True

    def test_webhook_only_not_webhook(self, mock_guild_prefix_context):
        mock_guild_prefix_context.event.message = mock.Mock(hikari.Message, webhook_id=None)
        with pytest.raises(lightbulb.errors.WebhookOnly):
            lightbulb.webhook_only(mock_guild_prefix_context)

    # human_only check
    def test_human_only(
        self, mock_guild_prefix_context, mock_guild_slash_context, mock_dm_slash_context, mock_dm_prefix_context
    ):
        assert lightbulb.human_only(mock_guild_slash_context) is True
        assert lightbulb.human_only(mock_guild_prefix_context) is True
        assert lightbulb.human_only(mock_dm_slash_context) is True
        assert lightbulb.human_only(mock_dm_prefix_context) is True

    def test_human_only_bot(
        self, mock_guild_prefix_context, mock_guild_slash_context, mock_dm_slash_context, mock_dm_prefix_context
    ):
        mock_guild_prefix_context.author.is_bot = True
        mock_guild_slash_context.author.is_bot = True
        mock_dm_prefix_context.author.is_bot = True
        mock_dm_slash_context.author.is_bot = True

        with pytest.raises(lightbulb.errors.HumanOnly):
            lightbulb.human_only(mock_guild_prefix_context)

        with pytest.raises(lightbulb.errors.HumanOnly):
            lightbulb.human_only(mock_guild_slash_context)

        with pytest.raises(lightbulb.errors.HumanOnly):
            lightbulb.human_only(mock_dm_prefix_context)

        with pytest.raises(lightbulb.errors.HumanOnly):
            lightbulb.human_only(mock_dm_slash_context)

    @pytest.mark.parametrize(
        "context", [lazy_fixture("mock_guild_slash_context"), lazy_fixture("mock_guild_prefix_context")]
    )
    @pytest.mark.parametrize(
        "channel",
        [pytest.param(lazy_fixture("mock_channel"), marks=pytest.mark.xfail), lazy_fixture("mock_channel_nsfw")],
    )
    # nsfw_channel_only check
    def test_nsfw_channel_only(self, context, channel):
        context.get_channel = mock.Mock(return_value=channel)
        assert lightbulb.nsfw_channel_only(context) is True

    def test_nsfw_channel_only_not_nsfw(self, mock_guild_prefix_context, mock_guild_slash_context):
        mock_channel = mock.Mock(hikari.PermissibleGuildChannel, is_nsfw=False)
        mock_guild_slash_context.get_channel = mock.Mock(return_value=mock_channel)
        mock_guild_prefix_context.get_channel = mock.Mock(return_value=mock_channel)

        with pytest.raises(lightbulb.NSFWChannelOnly):
            lightbulb.nsfw_channel_only(mock_guild_prefix_context)

        with pytest.raises(lightbulb.NSFWChannelOnly):
            lightbulb.nsfw_channel_only(mock_guild_slash_context)

    # has_roles check
    def test_has_roles(self, mock_guild_slash_context, mock_guild_prefix_context):
        check = lightbulb.has_roles(111)

        assert check(mock_guild_slash_context) is True
        assert check(mock_guild_prefix_context) is True

    def test_has_roles_missing_role(self, mock_context_member, mock_guild_slash_context, mock_guild_prefix_context):
        check = lightbulb.has_roles(222, 444)

        with pytest.raises(lightbulb.errors.MissingRequiredRole):
            check(mock_guild_prefix_context)

        with pytest.raises(lightbulb.errors.MissingRequiredRole):
            check(mock_guild_slash_context)

    # has_role_permissions check
    # def test_has_role_permissions(self, mock_context_member, mock_guild_prefix_context, mock_guild_slash_context):
    #     mock_context_member.permissions = hikari.Permissions.ADMINISTRATOR
    #     check = lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR)
    #     assert check(mock_guild_slash_context) is True
    #     assert check(mock_guild_prefix_context) is True
    #
    # def test_has_role_permissions_missing_permissions(
    #     self, mock_context_member, mock_guild_slash_context, mock_guild_prefix_context
    # ):
    #     mock_context_member.permissions = hikari.Permissions.NONE
    #     check = lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR)
    #     with pytest.raises(lightbulb.errors.MissingRequiredPermission):
    #         check(mock_guild_slash_context)
    #     with pytest.raises(lightbulb.errors.MissingRequiredPermission):
    #         check(mock_guild_prefix_context)

    # has_channel_permissions check
    def test_has_channel_permissions(self, mock_context_member, mock_guild_prefix_context, mock_guild_slash_context):
        mock_channel = mock.Mock(
            hikari.PermissibleGuildChannel,
            permission_overwrites={
                mock_context_member.id: hikari.PermissionOverwrite(
                    id=mock_context_member.id,
                    type=hikari.PermissionOverwriteType.MEMBER,
                    allow=hikari.Permissions.VIEW_CHANNEL,
                )
            },
        )
        mock_channel.is_nsfw = True

        mock_guild_prefix_context.get_channel = mock.Mock(return_value=mock_channel)
        mock_guild_slash_context.get_channel = mock.Mock(return_value=mock_channel)

        mock_context_member.permissions = hikari.Permissions.VIEW_CHANNEL

        check = lightbulb.has_channel_permissions(hikari.Permissions.VIEW_CHANNEL)
        assert check(mock_guild_slash_context) is True
        assert check(mock_guild_prefix_context) is True

    def test_has_channel_permissions_missing_permissions(
        self, mock_context_member, mock_guild_prefix_context, mock_guild_slash_context
    ):
        mock_channel = mock.Mock(
            hikari.PermissibleGuildChannel,
            permission_overwrites={
                mock_context_member.id: hikari.PermissionOverwrite(
                    id=mock_context_member.id,
                    type=hikari.PermissionOverwriteType.MEMBER,
                    deny=hikari.Permissions.VIEW_CHANNEL,
                )
            },
        )
        mock_channel.is_nsfw = True

        mock_guild_prefix_context.get_channel = mock.Mock(return_value=mock_channel)
        mock_guild_slash_context.get_channel = mock.Mock(return_value=mock_channel)

        mock_context_member.permissions = hikari.Permissions.VIEW_CHANNEL

        check = lightbulb.has_channel_permissions(hikari.Permissions.VIEW_CHANNEL)

        with pytest.raises(lightbulb.MissingRequiredPermission):
            check(mock_guild_slash_context)
            check(mock_guild_prefix_context)

    # has_guild_permissions check
    # def test_has_guild_permissions(self, mock_context_member, mock_guild_slash_context, mock_guild_prefix_context):
    #     mock_context_member.permissions = hikari.Permissions.ADMINISTRATOR
    #
    #     check = lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
    #     assert check(mock_guild_slash_context) is True
    #
    # @pytest.mark.parametrize(
    #     "context", [lazy_fixture("mock_guild_slash_context"), lazy_fixture("mock_guild_prefix_context")]
    # )
    # def test_has_guild_permissions_missing_permissions(
    #     self, mock_context_member, context: typing.Union[mock_guild_slash_context, mock_guild_prefix_context]
    # ):
    #     mock_context_member.permissions = hikari.Permissions.NONE
    #     check = lightbulb.checks._has_guild_permissions(context, perms=hikari.Permissions.ADMINISTRATOR)
        # with pytest.raises(lightbulb.errors.MissingRequiredPermission):
        #     check(context)

    # # bot_has_guild_permissions check
    # def test_bot_has_guild_permissions(self, mock_guild_context):
    #     mock_member = Mock()
    #     mock_member.permissions = hikari.Permissions.ADMINISTRATOR
    #     mock_guild_context.member = mock_member

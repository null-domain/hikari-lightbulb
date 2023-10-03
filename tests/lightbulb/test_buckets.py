import pytest
from unittest.mock import Mock
from lightbulb import cooldown_algorithms
from lightbulb import Bucket, UserBucket, ChannelBucket, GuildBucket, GlobalBucket


class TestBuckets:
    @pytest.fixture
    def mock_context(self):
        return Mock()

    def test_user_bucket_creation(self, mock_context):
        u_bucket = UserBucket(5.0, 3)
        assert u_bucket.length == 5.0
        assert u_bucket.usages == 3
        assert isinstance(u_bucket.cooldown_algorithm, cooldown_algorithms.BangBangCooldownAlgorithm)
        assert not u_bucket.active
        assert u_bucket.expired

    def test_channel_bucket_creation(self, mock_context):
        c_bucket = ChannelBucket(5.0, 3)
        assert c_bucket.length == 5.0
        assert c_bucket.usages == 3
        assert isinstance(c_bucket.cooldown_algorithm, cooldown_algorithms.BangBangCooldownAlgorithm)
        assert not c_bucket.active
        assert c_bucket.expired

    def test_guild_bucket_creation(self, mock_context):
        g_bucket = GuildBucket(5.0, 3)
        assert g_bucket.length == 5.0
        assert g_bucket.usages == 3
        assert isinstance(g_bucket.cooldown_algorithm, cooldown_algorithms.BangBangCooldownAlgorithm)
        assert not g_bucket.active
        assert g_bucket.expired

    def test_global_bucket_creation(self, mock_context):
        g_bucket = GlobalBucket(5.0, 3)
        assert g_bucket.length == 5.0
        assert g_bucket.usages == 3
        assert isinstance(g_bucket.cooldown_algorithm, cooldown_algorithms.BangBangCooldownAlgorithm)
        assert not g_bucket.active
        assert g_bucket.expired

    def test_user_bucket_activation(self, mock_context):
        u_bucket = UserBucket(5.0, 3)
        u_bucket.activate()
        assert u_bucket.active
        assert not u_bucket.expired

    def test_channel_bucket_activation(self, mock_context):
        c_bucket = ChannelBucket(5.0, 3)
        c_bucket.activate()
        assert c_bucket.active
        assert not c_bucket.expired

    def test_guild_bucket_activation(self, mock_context):
        g_bucket = GuildBucket(5.0, 3)
        g_bucket.activate()
        assert g_bucket.active
        assert not g_bucket.expired

    def test_global_bucket_activation(self, mock_context):
        g_bucket = GlobalBucket(5.0, 3)
        g_bucket.activate()
        assert g_bucket.active
        assert not g_bucket.expired

    def test_user_bucket_extract_hash(self, mock_context):
        mock_context.author.id = 123
        assert UserBucket.extract_hash(mock_context) == 123

    def test_channel_bucket_extract_hash(self, mock_context):
        mock_context.channel_id = 456
        assert ChannelBucket.extract_hash(mock_context) == 456

    def test_guild_bucket_extract_hash_with_guild_id(self, mock_context):
        mock_context.guild_id = 789
        mock_context.channel_id = 101112
        assert GuildBucket.extract_hash(mock_context) == 789

    def test_guild_bucket_extract_hash_without_guild_id(self, mock_context):
        mock_context.guild_id = None
        mock_context.channel_id = 101112
        assert GuildBucket.extract_hash(mock_context) == 101112

    def test_global_bucket_extract_hash(self, mock_context):
        assert GlobalBucket.extract_hash(mock_context) == 0

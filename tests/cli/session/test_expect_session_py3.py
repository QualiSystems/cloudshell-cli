from tests.cli.session.test_expect_session import ExpectSessionImpl  # noqa


def test_expect_session_read_wrong_utf8_symbol(logger):
    class TestSession(ExpectSessionImpl):
        data = [b"\xe2\x80\x99hi\xe2", b"\x80\x99"]  # ’hi’

        def _read_byte_data(self):
            return self.data.pop(0)

    session = TestSession()

    assert session._receive(1, logger) == "’hi’"

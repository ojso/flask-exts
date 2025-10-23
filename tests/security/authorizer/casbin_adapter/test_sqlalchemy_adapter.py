import re
from flask_exts.datastore.sqla import db
from flask_exts.security.authorizer.sqlalchemy_adapter import CasbinRule
from flask_exts.security.authorizer.sqlalchemy_adapter import Filter
from flask_exts.proxies import _security


def reset_models():
    db.drop_all()
    db.create_all()


def fill_db():
    db.session.add(CasbinRule(ptype="p", v0="alice", v1="data1", v2="read"))
    db.session.add(CasbinRule(ptype="p", v0="bob", v1="data2", v2="write"))
    db.session.add(CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read"))
    db.session.add(CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write"))
    db.session.add(CasbinRule(ptype="g", v0="alice", v1="data2_admin"))
    db.session.commit()


def get_enforcer():
    reset_models()
    fill_db()
    _security.authorizer.get_casbin_enforcer()
    e = _security.authorizer.e
    return e


# from unittest import TestCase
# class TestConfig(TestCase):


class TestConfig:
    def assertFalse(self, expr):
        """Check that the expression is false."""
        assert expr is False

    def assertTrue(self, expr):
        """Check that the expression is true."""
        assert expr is True

    def assertEqual(self, first, second):
        """Fail if the two objects are unequal as determined by the '=='
        operator.
        """
        assert first == second

    def assertRegex(self, text, expected_regex, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regex, (str, bytes)):
            assert expected_regex, "expected_regex must not be empty."
            expected_regex = re.compile(expected_regex)
        if not expected_regex.search(text):
            standardMsg = "Regex didn't match: %r not found in %r" % (
                expected_regex.pattern,
                text,
            )
            # _formatMessage ensures the longMessage option is respected
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)

    def test_enforcer_basic(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("alice", "data2", "read"))
            self.assertTrue(e.enforce("alice", "data2", "write"))

    def test_add_policy(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertFalse(e.enforce("eve", "data3", "read"))
            res = e.add_policies((("eve", "data3", "read"), ("eve", "data4", "read")))
            self.assertTrue(res)
            self.assertTrue(e.enforce("eve", "data3", "read"))
            self.assertTrue(e.enforce("eve", "data4", "read"))

    def test_add_policies(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertFalse(e.enforce("eve", "data3", "read"))
            res = e.add_permission_for_user("eve", "data3", "read")
            self.assertTrue(res)
            self.assertTrue(e.enforce("eve", "data3", "read"))

    def test_save_policy(self, app):
        with app.app_context():
            e = get_enforcer()
            self.assertFalse(e.enforce("alice", "data4", "read"))

            model = e.get_model()
            model.clear_policy()

            model.add_policy("p", "p", ["alice", "data4", "read"])

            adapter = e.get_adapter()
            adapter.save_policy(model)
            self.assertTrue(e.enforce("alice", "data4", "read"))

    def test_remove_policy(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertFalse(e.enforce("alice", "data5", "read"))
            e.add_permission_for_user("alice", "data5", "read")
            self.assertTrue(e.enforce("alice", "data5", "read"))
            e.delete_permission_for_user("alice", "data5", "read")
            self.assertFalse(e.enforce("alice", "data5", "read"))

    def test_remove_policies(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertFalse(e.enforce("alice", "data5", "read"))
            self.assertFalse(e.enforce("alice", "data6", "read"))
            e.add_policies((("alice", "data5", "read"), ("alice", "data6", "read")))
            self.assertTrue(e.enforce("alice", "data5", "read"))
            self.assertTrue(e.enforce("alice", "data6", "read"))
            e.remove_policies((("alice", "data5", "read"), ("alice", "data6", "read")))
            self.assertFalse(e.enforce("alice", "data5", "read"))
            self.assertFalse(e.enforce("alice", "data6", "read"))

    def test_remove_filtered_policy(self, app):
        with app.app_context():
            e = get_enforcer()

            self.assertTrue(e.enforce("alice", "data1", "read"))
            e.remove_filtered_policy(1, "data1")
            self.assertFalse(e.enforce("alice", "data1", "read"))

            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertTrue(e.enforce("alice", "data2", "read"))
            self.assertTrue(e.enforce("alice", "data2", "write"))

            e.remove_filtered_policy(1, "data2", "read")

            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertTrue(e.enforce("alice", "data2", "write"))

            e.remove_filtered_policy(2, "write")

            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("alice", "data2", "write"))

            # e.add_permission_for_user('alice', 'data6', 'delete')
            # e.add_permission_for_user('bob', 'data6', 'delete')
            # e.add_permission_for_user('eve', 'data6', 'delete')
            # self.assertTrue(e.enforce('alice', 'data6', 'delete'))
            # self.assertTrue(e.enforce('bob', 'data6', 'delete'))
            # self.assertTrue(e.enforce('eve', 'data6', 'delete'))
            # e.remove_filtered_policy(0, 'alice', None, 'delete')
            # self.assertFalse(e.enforce('alice', 'data6', 'delete'))
            # e.remove_filtered_policy(0, None, None, 'delete')
            # self.assertFalse(e.enforce('bob', 'data6', 'delete'))
            # self.assertFalse(e.enforce('eve', 'data6', 'delete'))

    def test_str(self):

        rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
        self.assertEqual(str(rule), "p, alice, data1, read")
        rule = CasbinRule(ptype="p", v0="bob", v1="data2", v2="write")
        self.assertEqual(str(rule), "p, bob, data2, write")
        rule = CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read")
        self.assertEqual(str(rule), "p, data2_admin, data2, read")
        rule = CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write")
        self.assertEqual(str(rule), "p, data2_admin, data2, write")
        rule = CasbinRule(ptype="g", v0="alice", v1="data2_admin")
        self.assertEqual(str(rule), "g, alice, data2_admin")

    def test_repr(self, app):
        with app.app_context():
            e = get_enforcer()
            rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
            self.assertEqual(repr(rule), '<CasbinRule None: "p, alice, data1, read">')
            db.session.add(rule)
            db.session.commit()
            self.assertRegex(repr(rule), r'<CasbinRule \d+: "p, alice, data1, read">')

    def test_filtered_policy(self, app):
        with app.app_context():
            e = get_enforcer()
            filter = Filter()

            filter.ptype = ["p"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("bob", "data2", "write"))

            filter.ptype = []
            filter.v0 = ["alice"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("data2_admin", "data2", "write"))

            filter.v0 = ["bob"]
            e.load_filtered_policy(filter)
            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("data2_admin", "data2", "write"))

            filter.v0 = ["data2_admin"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("data2_admin", "data2", "read"))
            self.assertTrue(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertFalse(e.enforce("bob", "data2", "write"))

            filter.v0 = ["alice", "bob"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("data2_admin", "data2", "write"))

            filter.v0 = []
            filter.v1 = ["data1"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("data2_admin", "data2", "write"))

            filter.v1 = ["data2"]
            e.load_filtered_policy(filter)
            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertTrue(e.enforce("data2_admin", "data2", "read"))
            self.assertTrue(e.enforce("data2_admin", "data2", "write"))

            filter.v1 = []
            filter.v2 = ["read"]
            e.load_filtered_policy(filter)
            self.assertTrue(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertTrue(e.enforce("data2_admin", "data2", "read"))
            self.assertFalse(e.enforce("data2_admin", "data2", "write"))

            filter.v2 = ["write"]
            e.load_filtered_policy(filter)
            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("alice", "data1", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "write"))
            self.assertFalse(e.enforce("bob", "data2", "read"))
            self.assertTrue(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertTrue(e.enforce("data2_admin", "data2", "write"))

    def test_update_policy(self, app):
        with app.app_context():
            e = get_enforcer()
            example_p = ["mike", "cookie", "eat"]

            self.assertTrue(e.enforce("alice", "data1", "read"))
            e.update_policy(["alice", "data1", "read"], ["alice", "data1", "no_read"])
            self.assertFalse(e.enforce("alice", "data1", "read"))

            self.assertFalse(e.enforce("bob", "data1", "read"))
            e.add_policy(example_p)
            e.update_policy(example_p, ["bob", "data1", "read"])
            self.assertTrue(e.enforce("bob", "data1", "read"))

            self.assertFalse(e.enforce("bob", "data1", "write"))
            e.update_policy(["bob", "data1", "read"], ["bob", "data1", "write"])
            self.assertTrue(e.enforce("bob", "data1", "write"))

            self.assertTrue(e.enforce("bob", "data2", "write"))
            e.update_policy(["bob", "data2", "write"], ["bob", "data2", "read"])
            self.assertFalse(e.enforce("bob", "data2", "write"))

            self.assertTrue(e.enforce("bob", "data2", "read"))
            e.update_policy(["bob", "data2", "read"], ["carl", "data2", "write"])
            self.assertFalse(e.enforce("bob", "data2", "write"))

            self.assertTrue(e.enforce("carl", "data2", "write"))
            e.update_policy(["carl", "data2", "write"], ["carl", "data2", "no_write"])
            self.assertFalse(e.enforce("bob", "data2", "write"))

    def test_update_policies(self, app):
        with app.app_context():
            e = get_enforcer()

            old_rule_0 = ["alice", "data1", "read"]
            old_rule_1 = ["bob", "data2", "write"]
            old_rule_2 = ["data2_admin", "data2", "read"]
            old_rule_3 = ["data2_admin", "data2", "write"]

            new_rule_0 = ["alice", "data_test", "read"]
            new_rule_1 = ["bob", "data_test", "write"]
            new_rule_2 = ["data2_admin", "data_test", "read"]
            new_rule_3 = ["data2_admin", "data_test", "write"]

            old_rules = [old_rule_0, old_rule_1, old_rule_2, old_rule_3]
            new_rules = [new_rule_0, new_rule_1, new_rule_2, new_rule_3]

            e.update_policies(old_rules, new_rules)

            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertTrue(e.enforce("alice", "data_test", "read"))

            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertTrue(e.enforce("bob", "data_test", "write"))

            self.assertFalse(e.enforce("data2_admin", "data2", "read"))
            self.assertTrue(e.enforce("data2_admin", "data_test", "read"))

            self.assertFalse(e.enforce("data2_admin", "data2", "write"))
            self.assertTrue(e.enforce("data2_admin", "data_test", "write"))

    def test_update_filtered_policies(self, app):
        with app.app_context():
            e = get_enforcer()

            e.update_filtered_policies(
                [
                    ["data2_admin", "data3", "read"],
                    ["data2_admin", "data3", "write"],
                ],
                0,
                "data2_admin",
            )
            self.assertTrue(e.enforce("data2_admin", "data3", "write"))
            self.assertTrue(e.enforce("data2_admin", "data3", "read"))

            e.update_filtered_policies([["alice", "data1", "write"]], 0, "alice")
            self.assertTrue(e.enforce("alice", "data1", "write"))

            e.update_filtered_policies([["bob", "data2", "read"]], 0, "bob")
            self.assertTrue(e.enforce("bob", "data2", "read"))

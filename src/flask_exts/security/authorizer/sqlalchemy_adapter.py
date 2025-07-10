from casbin import persist
from sqlalchemy import Column, Integer, String
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import delete

from ...datastore.sqla import db


class CasbinRule(db.Model):
    __tablename__ = "casbin_rule"

    id = Column(Integer, primary_key=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ", ".join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))


class Filter:
    ptype = []
    v0 = []
    v1 = []
    v2 = []
    v3 = []
    v4 = []
    v5 = []


class SqlalchemyAdapter(persist.Adapter, persist.adapters.UpdateAdapter):
    """the interface for Casbin adapters."""

    def __init__(self, filtered=False):
        self._db_session = db.session
        self._db_class = CasbinRule
        self._filtered = filtered

    def load_policy(self, model):
        """loads all policy rules from the storage."""
        stmt = select(self._db_class)
        lines = self._db_session.scalars(stmt)
        for line in lines:
            persist.load_policy_line(str(line), model)

    def is_filtered(self):
        return self._filtered

    def load_filtered_policy(self, model, filter) -> None:
        """loads all policy rules with filter from the storage."""
        stmt = select(self._db_class)
        stmt = self.filter_query(stmt, filter)
        filters = self._db_session.scalars(stmt)

        for line in filters:
            persist.load_policy_line(str(line), model)
        self._filtered = True

    def filter_query(self, stmt, filter):
        for attr in ("ptype", "v0", "v1", "v2", "v3", "v4", "v5"):
            if len(getattr(filter, attr)) > 0:
                stmt = stmt.where(
                    getattr(self._db_class, attr).in_(getattr(filter, attr))
                )
        return stmt.order_by(self._db_class.id)

    def _save_policy_line(self, ptype, rule):
        line = self._db_class(ptype=ptype)
        for i, v in enumerate(rule):
            setattr(line, "v{}".format(i), v)
        self._db_session.add(line)
        self._db_session.commit()

    def save_policy(self, model):
        """saves all policy rules to the storage."""
        stmt = delete(self._db_class)
        self._db_session.execute(stmt)
        self._db_session.commit()

        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    self._save_policy_line(ptype, rule)
        
        return True

    def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        self._save_policy_line(ptype, rule)

    def add_policies(self, sec, ptype, rules):
        """adds a policy rules to the storage."""
        for rule in rules:
            self._save_policy_line(ptype, rule)

    def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        stmt = delete(self._db_class)
        stmt = stmt.where(self._db_class.ptype == ptype)
        for i, v in enumerate(rule):
            stmt = stmt.where(getattr(self._db_class, "v{}".format(i)) == v)
        r=self._db_session.execute(stmt)
        self._db_session.commit()
        return True if r.rowcount > 0 else False

    def remove_policies(self, sec, ptype, rules):
        """remove policy rules from the storage."""
        if not rules:
            return
        stmt = delete(self._db_class).where(self._db_class.ptype == ptype)
        rules = zip(*rules)
        for i, rule in enumerate(rules):
            stmt =stmt.where(
                or_(getattr(self._db_class, "v{}".format(i)) == v for v in rule)
            )
        self._db_session.execute(stmt)
        self._db_session.commit()

    def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        stmt = delete(self._db_class).where(self._db_class.ptype == ptype)

        if not (0 <= field_index <= 5):
            return False
        if not (1 <= field_index + len(field_values) <= 6):
            return False
        for i, v in enumerate(field_values):
            if v != "":
                v_value = getattr(self._db_class, "v{}".format(field_index + i))
                stmt = stmt.where(v_value == v)

        r=self._db_session.execute(stmt)
        self._db_session.commit()
        return True if r.rowcount > 0 else False

    def update_policy(
        self, sec: str, ptype: str, old_rule: list[str], new_rule: list[str]
    ) -> None:
        """
        Update the old_rule with the new_rule in the database (storage).

        :param sec: section type
        :param ptype: policy type
        :param old_rule: the old rule that needs to be modified
        :param new_rule: the new rule to replace the old rule

        :return: None
        """

        stmt = select(self._db_class).where(self._db_class.ptype == ptype)

        # locate the old rule
        for index, value in enumerate(old_rule):
            v_value = getattr(self._db_class, "v{}".format(index))
            stmt = stmt.where(v_value == value)

        # need the length of the longest_rule to perform overwrite
        longest_rule = old_rule if len(old_rule) > len(new_rule) else new_rule
        old_rule_line = self._db_session.scalar(stmt)

        # overwrite the old rule with the new rule
        for index in range(len(longest_rule)):
            if index < len(new_rule):
                exec(f"old_rule_line.v{index} = new_rule[{index}]")
            else:
                exec(f"old_rule_line.v{index} = None")

        self._db_session.commit()  
            

    def update_policies(
        self,
        sec: str,
        ptype: str,
        old_rules: list[str],
        new_rules: list[str],
    ) -> None:
        """
        Update the old_rules with the new_rules in the database (storage).

        :param sec: section type
        :param ptype: policy type
        :param old_rules: the old rules that need to be modified
        :param new_rules: the new rules to replace the old rules

        :return: None
        """
        for i in range(len(old_rules)):
            self.update_policy(sec, ptype, old_rules[i], new_rules[i])

    def update_filtered_policies(
        self, sec, ptype, new_rules: list[str], field_index, *field_values
    ) -> list[str]:
        """update_filtered_policies updates all the policies on the basis of the filter."""

        filter = Filter()
        filter.ptype = ptype

        # Creating Filter from the field_index & field_values provided
        for i in range(len(field_values)):
            if field_index <= i and i < field_index + len(field_values):
                setattr(filter, f"v{i}", field_values[i - field_index])
            else:
                break

        self._update_filtered_policies(new_rules, filter)

    def _update_filtered_policies(self, new_rules, filter) -> list[str]:
        """_update_filtered_policies updates all the policies on the basis of the filter."""


        # Load old policies

        stmt = select(self._db_class).where(self._db_class.ptype == filter.ptype)
        filtered_stmt = self.filter_query(stmt, filter)
        old_rules = self._db_session.scalars(filtered_stmt)

        # Delete old policies

        self.remove_policies("p", filter.ptype, old_rules)

        # Insert new policies

        self.add_policies("p", filter.ptype, new_rules)

        # return deleted rules

        return old_rules

import enum
from collections import namedtuple
from functools import reduce
from operator import and_, or_
from pydantic import BaseModel
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db import models

from user.models import User


ALL_ACTIONS = '__all__'
BASE_RULE_ID = '__base_rule__'


class Context(BaseModel):
    user: Optional[User] = None

    class Config:
        arbitrary_types_allowed = True


# -------------------------------------------------------
# Access Rules Registry
# -------------------------------------------------------

WrappedRule = namedtuple('WrappedRule', 'rule roles')


class AccessPolicyRegistry:
    _instance = None

    _rule_registry = {} # identifier -> Rule instance
    _rule_model_registry = {} # model -> list rule instance

    def __new__(class_, *args, **kwargs):
        """Singleton pattern: ensure there is only one instance of this class. Call
        constructor `AccessPolicyRegistry()` will return the instance of it exsits,
        create it if not.
        """
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def register_rule(self, rule_cls):
        return self._register_rule(rule_cls)

    def _register_rule(self, rule_cls):
        if not issubclass(rule_cls.model, models.Model):
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} must have a model defined.")
        if not isinstance(rule_cls.identifier, str):
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} must have an identifier (string).")
        if rule_cls.identifier in self._rule_registry:
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} has a non unique identifier.")
        if not rule_cls.name:
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} must have a name.")

        rule = rule_cls()
        self._rule_registry[rule_cls.identifier] = rule
        self._rule_model_registry.setdefault(rule_cls.model, []).append(rule)

    def get_model_rules(self, model_cls):
        return self._rule_model_registry.get(
            model_cls, []
        )  # if no rule registered, should not crash

    def get_rules(self, *ids):
        return [rule for rid, rule in self._rule_registry.items() if rid in ids]

    def get_matching_rules(self, rule_ids_by_group, model_cls):
        result = []
        for rule_ids in rule_ids_by_group:
            model_rules = self.get_model_rules(model_cls)
            result.append([rule for rule in model_rules if rule.identifier in rule_ids])
        return result

    def get_rule_choices(self):
        return {rid: rule.name for rid, rule in self._rule_registry.items()}

    # def get_rules(self, model_cls, roles, action):
    #     wrapped_rules = self.get_model_rules(model_cls)

    #     global_rules = []
    #     role_rules = []
    #     for wrapped_rule in wrapped_rules:
    #         if wrapped_rule.roles:
    #             if any(r in wrapped_rule.roles for r in roles): # role intersection
    #                 if self._match_action_rule(wrapped_rule.rule, action):
    #                     role_rules.append(wrapped_rule.rule)
    #         else:  # global rules
    #             if self._match_action_rule(wrapped_rule.rule, action):
    #                 global_rules.append(wrapped_rule.rule)
    #     return global_rules, role_rules

    # def _match_action_rule(self, rule, action):
    #     if rule.actions == ALL_ACTIONS:
    #         return True
    #     return action in rule.actions


access_policy = AccessPolicyRegistry()  # singleton registry

#------------------------------------------------------
# Access Rule
#------------------------------------------------------

class CRUDOperation(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    FIND_ONE = "find_one"
    DELETE = "delete"


class BaseRuleMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if new_cls.identifier == BASE_RULE_ID:
            return new_cls
        access_policy.register_rule(new_cls)
        return new_cls


class BaseRule:
    """
    A base class from which all rule classes should inherit.
    """
    identifier = BASE_RULE_ID
    model = None # required
    name = None # required
    description = None

    # List of possible operations for this model. Goal is to avoid
    # too many imports. Depends on what is implemented in the
    # model service.
    operations = CRUDOperation  # customize if needed

    def scope_filter(self, action: str, context: Context):
        """Return the lookups to apply on filter. Must be a `Q` expression."""
        return Q()

#------------------------------------------------------
# API
#------------------------------------------------------

async def request_to_context(request):
    return Context(user=request.user or None) # force none instead of Anonymous user


async def apply_access_rules(queryset, action, context: Context):
    """ Apply access rules for the given model and apply them on
        current queryset to scope it.
        :param queryset: django queryset to alter
        :param action: operation (string) to check
    """
    # extract role of current context (API token ignore role rules)
    roles = []
    if context.user:
        roles = [userrole async for userrole in context.user.roles.all()]

    rule_groups = []
    for role in roles:
        rule_groups.append(list(role.rules) if role.rules is not None else list())

    # find rule to apply
    rule_group_to_apply = access_policy.get_matching_rules(rule_groups, queryset.model)

    # compute lookups
    # Assembled as (ruleA_role1 & ruleB_role1) || (ruleA_role2 & ruleC_role2)
    rule_lookups = []
    for rule_to_apply in rule_group_to_apply:
        rule_lookups.append(reduce(and_, [Q()] + [r.scope_filter(action, context) for r in rule_to_apply]))

    rule_lookups = reduce(or_, rule_lookups)
    if rule_lookups:
        queryset = queryset.filter(rule_lookups)

    return queryset

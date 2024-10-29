from collections import namedtuple
from functools import reduce
from operator import and_, or_
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db import models


ALL_ACTIONS = '__all__'

#------------------------------------------------------
# Access Rule
#------------------------------------------------------

class BaseRule:
    """
    A base class from which all rule classes should inherit.
    """
    model = None # required
    actions = [] # can't be empty
    description = None

    def scope_filter(self, request):
        """Return the lookups to apply on filter. Must be a `Q` expression."""
        return Q()


# -------------------------------------------------------
# Access Rules Registry
# -------------------------------------------------------

WrappedRule = namedtuple('WrappedRule', 'rule roles')


class AccessPolicyRegistry:
    _instance = None

    _rule_registry = {} # model -> list of wrapped rule (containing the instance of the rule)

    def __new__(class_, *args, **kwargs):
        """Singleton pattern: ensure there is only one instance of this class. Call
        constructor `AccessPolicyRegistry()` will return the instance of it exsits,
        create it if not.
        """
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def register_rule(self, *roles):
        def decorator(rule_cls):
            self._register_rule(rule_cls, roles)
            return rule_cls
        return decorator

    def _register_rule(self, rule_cls, roles=[]):
        if not issubclass(rule_cls.model, models.Model):
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} must have a model defined.")
        if not (isinstance(rule_cls.actions, list) or rule_cls.actions == ALL_ACTIONS):
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} must have a list of actions defined as attribute (either a list or the __all__ special value.")
        if not rule_cls.actions:
            raise ImproperlyConfigured(f"Rule class {rule_cls.__name__} actions can not be empty.")

        rule = rule_cls()
        self._rule_registry.setdefault(rule.model, [])
        self._rule_registry[rule.model].append(WrappedRule(rule_cls(), roles))

    def get_model_rules(self, model_cls):
        return self._rule_registry.get(
            model_cls, []
        )  # if no rule registered, should not crash

    def get_rules(self, model_cls, roles, action):
        wrapped_rules = self.get_model_rules(model_cls)

        global_rules = []
        role_rules = []
        for wrapped_rule in wrapped_rules:
            if wrapped_rule.roles:
                if any(r in wrapped_rule.roles for r in roles): # role intersection
                    if self._match_action_rule(wrapped_rule.rule, action):
                        role_rules.append(wrapped_rule.rule)
            else:  # global rules
                if self._match_action_rule(wrapped_rule.rule, action):
                    global_rules.append(wrapped_rule.rule)
        return global_rules, role_rules

    def _match_action_rule(self, rule, action):
        if rule.actions == ALL_ACTIONS:
            return True
        return action in rule.actions


def apply_access_rules(request, queryset, action):
    """ Get all applicable access rules for the given model and apply them on
        current queryset to scope it.
        :param request: http request
        :param queryset: django queryset to alter
        :param action: action the request wants to perform on the queryset
    """
    # extract role of current request (API token ignore role rules)
    roles = []
    if request.user:
        roles = [userrole.pk for userrole in request.user.roles.all()]

    # find applicable rules
    global_rules, role_rules = access_policy.get_rules(queryset.model, roles, action)

    # compute lookups
    global_lookups = reduce(and_, [Q()] + [r.scope_filter(request) for r in global_rules])
    role_lookups = reduce(or_, [Q()] + [r.scope_filter(request) for r in role_rules])

    if global_lookups:
        queryset = queryset.filter(global_lookups)
    if role_lookups:
        queryset = queryset.filter(role_lookups)

    return queryset


access_policy = AccessPolicyRegistry()  # singleton registry of all rules per model

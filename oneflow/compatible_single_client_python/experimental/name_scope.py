"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import

from contextlib import contextmanager

from oneflow.compatible.single_client.python.framework import (
    session_context as session_context,
)
from oneflow.compatible.single_client.python.framework import scope_util as scope_util
from oneflow.compatible.single_client.python.oneflow_export import (
    oneflow_export,
    oneflow_deprecate,
)
import oneflow._oneflow_internal
import traceback


@oneflow_export(
    "name_scope", "experimental.name_scope", "deprecated.variable_scope",
)
@oneflow_deprecate()
def deprecated_name_scope(*args, **kwargs):
    print(
        "WARNING:",
        "oneflow.compatible.single_client.name_scope/oneflow.compatible.single_client.experimental.name_scope/deprecated.variable_scope",
        "will be removed in the future, use {} instead.".format(
            "oneflow.compatible.single_client.scope.namespace"
        ),
    )
    print(traceback.format_stack()[-2])
    return name_scope(*args, **kwargs)


@oneflow_export("scope.namespace")
@contextmanager
def name_scope(name: str) -> None:
    r"""Create a namespace. All variables within the namespace will have a prefix `[SCOPE NAME]-`. This is for convenience only and has no other effect on the system.
    Usage::

        with oneflow.compatible.single_client.scope.namespace("scope1"):
            ...
            with oneflow.compatible.single_client.scope.namespace("scope2"):
                ...

    Args:
        name: Name of this namespace

    """
    assert isinstance(name, str)
    name_scope_stack_push(name)

    def BuildScope(old_scope, builder):
        return builder.BuildScopeWithNewScopeName(old_scope, name)

    sess = session_context.GetDefaultSession()
    try:
        with scope_util.ScopeContext(scope_util.MakeScope(BuildScope)):
            yield
    finally:
        name_scope_stack_pop()


def name_scope_stack_push(name):
    job_name = oneflow._oneflow_internal.JobBuildAndInferCtx_GetCurrentJobName()
    sess = session_context.GetDefaultSession()
    if job_name not in sess.job_name2name_scope_stack:
        sess.job_name2name_scope_stack[job_name] = []
    sess.job_name2name_scope_stack[job_name].append(name)


def name_scope_stack_pop():
    job_name = oneflow._oneflow_internal.JobBuildAndInferCtx_GetCurrentJobName()
    sess = session_context.GetDefaultSession()
    assert job_name in sess.job_name2name_scope_stack
    assert len(sess.job_name2name_scope_stack[job_name]) > 0
    return sess.job_name2name_scope_stack[job_name].pop()


def GetJobNameScopePrefix(job_name):
    sess = session_context.GetDefaultSession()
    if job_name not in sess.job_name2name_scope_stack:
        return ""
    if len(sess.job_name2name_scope_stack[job_name]) == 0:
        return ""
    return "-".join(sess.job_name2name_scope_stack[job_name]) + "-"


def PrependOpNamePrefixIfNeed(op_conf):
    if op_conf.HasField("variable_conf"):
        return

    if op_conf.HasField("decode_ofrecord_conf"):
        return

    if op_conf.HasField("user_conf"):
        return

    job_name = oneflow._oneflow_internal.JobBuildAndInferCtx_GetCurrentJobName()
    op_conf.name = GetJobNameScopePrefix(job_name) + op_conf.name

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

from oneflow.compatible.single_client.python.framework import (
    python_callback as python_callback,
)
from oneflow.compatible.single_client.python.eager import (
    interpreter_callback as interpreter_callback,
)
import oneflow._oneflow_internal

python_callback.interpreter_callback = interpreter_callback

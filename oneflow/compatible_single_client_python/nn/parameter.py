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
from oneflow.compatible import single_client as flow
from oneflow.compatible.single_client.python.oneflow_export import oneflow_export
from oneflow.compatible.single_client.python.framework.tensor import Tensor


@oneflow_export("nn.Parameter")
class Parameter(Tensor):
    def __init__(self, data, requires_grad=True):
        # TODO: uncomment this line when autograd is ready
        # data.requires_grad = True
        # TODO: uncomment the following two lines when consistent <-> local conversion is ready
        # data.set_is_consistent(True)
        # data.set_placement(flow.placement("gpu", ["0:0"], None))
        self._data = data
        self._data.requires_grad = requires_grad

    def __getattr__(self, name):
        return getattr(self._data, name)

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

import traceback
from oneflow.compatible.single_client.python.oneflow_export import oneflow_export
import oneflow._oneflow_internal


@oneflow_export("tensorrt.write_int8_calibration")
def write_int8_calibration(path):
    try:
        oneflow._oneflow_internal.WriteInt8Calibration(path)
    except oneflow._oneflow_internal.exception.CompileOptionWrongException:
        traceback.print_exc()


@oneflow_export("tensorrt.cache_int8_calibration")
def cache_int8_calibration():
    try:
        oneflow._oneflow_internal.CacheInt8Calibration()
    except oneflow._oneflow_internal.exception.CompileOptionWrongException:
        traceback.print_exc()

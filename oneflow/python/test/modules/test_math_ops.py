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
import unittest
from collections import OrderedDict

import numpy as np

import oneflow.experimental as flow
from test_util import GenArgList, type_name_to_flow_type, type_name_to_np_type
from automated_test_util import *
import torch


def _test_variance_keepdim(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    of_out = flow.Tensor(np_arr, device=flow.device(device)).var(0, True)
    np_out = np.var(np_arr, 0, keepdims=True)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_variance(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    of_out = flow.var(flow.Tensor(np_arr, device=flow.device(device)), 1, False)
    np_out = np.var(np_arr, 1, keepdims=False)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_variance_backward(test_case, shape, device):
    np_arr = np.array(
        [
            [
                [-0.43621400, -1.11672411, 0.78394664, 2.06217120],
                [0.77167030, -1.35367316, -0.40694879, -1.72392356],
                [-1.08482436, -0.20731248, 1.39633697, 0.32614333],
            ],
            [
                [-1.42467297, -1.78418015, 0.17861511, 0.12065858],
                [2.03621124, -0.93674042, 0.19439630, 1.98559192],
                [-0.00436223, 0.37788105, 0.47820872, 0.15467583],
            ],
        ]
    )
    x = flow.Tensor(np_arr, requires_grad=True, device=flow.device(device))
    y = flow.var(x, False)
    z = y.sum()
    z.backward()
    np_grad = 2 * (np_arr - np_arr.mean()) / (np_arr.size)
    test_case.assertTrue(np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5))


@flow.unittest.skip_unless_1n1d()
class TestVariance(flow.unittest.TestCase):
    def test_variance(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_variance,
            _test_variance_keepdim,
            # _test_variance_backward # TODO:(zhaoluyang):output grad not equal to numpy grad
        ]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_sinh_impl(test_case, shape, device):
    np_input = np.random.randn(*shape)
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )

    np_x_grad = np.cosh(np_input)
    of_out = flow.sinh(of_input)
    np_out = np.sinh(np_input)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

    of_out = of_out.sum()
    of_out.backward()
    test_case.assertTrue(np.allclose(of_input.grad.numpy(), np_x_grad, 1e-4, 1e-4))


@flow.unittest.skip_unless_1n1d()
class Testsinh(flow.unittest.TestCase):
    def test_sinh(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2, 3), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_sinh_impl(test_case, *arg)

    def test_flow_sinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case, "sinh", device=device,
            )

    def test_flow_tensor_sinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case, "sinh", device=device,
            )


def _test_sin(test_case, shape, device):
    input = flow.Tensor(np.random.randn(*shape), device=flow.device(device))
    of_out = flow.sin(input)
    np_out = np.sin(input.numpy())
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_sin_backward(test_case, shape, device):
    x = flow.Tensor(
        np.random.randn(*shape), requires_grad=True, device=flow.device(device)
    )
    y = flow.sin(x)
    z = y.sum()
    z.backward()
    test_case.assertTrue(np.allclose(x.grad.numpy(), np.cos(x.numpy()), 1e-5, 1e-5))


def _test_inplace_sin(test_case, shape, device):
    x = flow.Tensor(
        np.random.randn(*shape), device=flow.device(device), requires_grad=True
    )
    x_inplace = x + 1
    np_out = np.sin(x_inplace.numpy())

    id_old = id(x_inplace)
    x_inplace.sin_()

    test_case.assertEqual(id_old, id(x_inplace))
    test_case.assertTrue(np.allclose(x_inplace.numpy(), np_out, 1e-5, 1e-5))

    of_x_inplace = x_inplace.sum()
    of_x_inplace.backward()
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np.cos(x_inplace.numpy()), 1e-5, 1e-5)
    )


@flow.unittest.skip_unless_1n1d()
class TestSin(flow.unittest.TestCase):
    def test_sin(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_sin,
            _test_sin_backward,
            _test_inplace_sin,
        ]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_cos(test_case, shape, device):
    input = flow.Tensor(
        np.random.randn(*shape), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.cos(input)
    np_out = np.cos(input.numpy())
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_cos_backward(test_case, shape, device):
    x = flow.Tensor(
        np.random.randn(*shape),
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    y = flow.cos(x)
    z = y.sum()
    z.backward()
    np_grad = -np.sin(x.numpy())
    test_case.assertTrue(np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5))


@flow.unittest.skip_unless_1n1d()
class TestCos(flow.unittest.TestCase):
    def test_cos(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_cos,
            _test_cos_backward,
        ]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_log(test_case, shape, device):
    np_arr = np.abs(np.random.randn(*shape))
    input = flow.Tensor(np_arr, dtype=flow.float32, device=flow.device(device))
    of_out = flow.log(input)
    np_out = np.log(np_arr)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_log_nan_value(test_case, shape, device):
    arr = np.array([-0.7168, -0.5471, -0.8933, -1.4428, -0.1190])
    input = flow.Tensor(arr, dtype=flow.float32, device=flow.device(device))
    np_out = np.full((5,), np.nan)
    of_out = flow.log(input)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_log_backward(test_case, shape, device):
    x = flow.Tensor(
        np.random.randn(*shape),
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    y = flow.log(x)
    z = y.sum()
    z.backward()
    np_grad = 1 / x.numpy()
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestLog(flow.unittest.TestCase):
    def test_log(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_log, _test_log_nan_value, _test_log_backward]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_std(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    input = flow.Tensor(np_arr, device=flow.device(device))
    of_out = flow.std(input, dim=2)
    np_out = np.std(np_arr, axis=2)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))


def _test_std_dim1(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    input = flow.Tensor(np_arr, device=flow.device(device))
    of_out = flow.std(input, dim=1)
    np_out = np.std(np_arr, axis=1)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))


def _test_std_negative_dim(test_case, shape, device):
    np_arr = np.random.randn(4, 2, 3, 5)
    input = flow.Tensor(np_arr, device=flow.device(device))
    of_out = input.std(dim=(-2, -1, -3), keepdim=False)
    np_out = np.std(np_arr, axis=(-2, -1, -3))
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))


@flow.unittest.skip_unless_1n1d()
class TestStd(flow.unittest.TestCase):
    def test_std(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_std,
            _test_std_dim1,
            _test_std_negative_dim,
            # TODO:(zhaoluyang):add backward test
        ]
        arg_dict["shape"] = [(2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_sqrt(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_arr = np.abs(np_arr)
    np_out = np.sqrt(np_arr)
    x = flow.Tensor(np_arr, device=flow.device(device))
    of_out = flow.sqrt(input=x)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_sqrt_backward(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_arr = np.abs(np_arr)
    x = flow.Tensor(np_arr, device=flow.device(device), requires_grad=True)
    y = flow.sqrt(input=x)
    z = y.sum()
    z.backward()
    np_grad = 0.5 * 1 / np.sqrt(x.numpy())
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestSqrt(flow.unittest.TestCase):
    def test_sqrt(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_sqrt, _test_sqrt_backward]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_rsqrt(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_arr = np.abs(np_arr)
    np_out = 1 / np.sqrt(np_arr)
    input = flow.Tensor(np_arr, device=flow.device(device))
    of_out = input.rsqrt()
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_rsqrt_backward(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_arr = np.abs(np_arr)
    x = flow.Tensor(np_arr, device=flow.device(device), requires_grad=True)
    y = flow.rsqrt(input=x)
    z = y.sum()
    z.backward()
    np_grad = -1 / 2 * 1 / (x.numpy() * np.sqrt(x.numpy()))
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestRsqrt(flow.unittest.TestCase):
    def test_rsqrt(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_rsqrt, _test_rsqrt_backward]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_square(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_out = np.square(np_arr)
    x = flow.Tensor(np_arr, device=flow.device(device))
    of_out = flow.square(x)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_square_backward(test_case, shape, device):
    np_arr = np.random.randn(*shape)
    np_out = np.square(np_arr)
    x = flow.Tensor(np_arr, device=flow.device(device), requires_grad=True)
    y = flow.square(x)
    z = y.sum()
    z.backward()
    np_grad = 2 * np_arr
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestSquare(flow.unittest.TestCase):
    def test_square(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_square, _test_square_backward]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_pow(test_case, shape, device):
    input = flow.Tensor(
        np.random.randn(*shape), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.pow(input, 2.1)
    np_out = np.power(input.numpy(), 2.1)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5, equal_nan=True)
    )


def _test_pow_backward(test_case, shape, device):
    x = flow.Tensor(
        np.random.randn(*shape),
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    y = flow.pow(x, 2.34)
    z = y.sum()
    z.backward()
    np_grad = 2.34 * x.numpy() ** (2.34 - 1)
    test_case.assertTrue(
        np.allclose(x.grad.numpy(), np_grad, 1e-5, 1e-5, equal_nan=True)
    )


@flow.unittest.skip_unless_1n1d()
class TestPow(flow.unittest.TestCase):
    def test_pow(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_pow,
            _test_pow_backward,
        ]
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def _test_asin(test_case, shape, device):
    np_input = np.random.random(shape) - 0.5

    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )

    of_out = flow.asin(of_input)
    np_out = np.arcsin(np_input)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))

    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / np.sqrt(1 - np_input ** 2)

    test_case.assertTrue(np.allclose(of_input.grad.numpy(), np_out_grad, 1e-4, 1e-4))


def _test_arcsin(test_case, shape, device):
    np_input = np.random.random(shape) - 0.5
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )

    of_out = flow.arcsin(of_input)
    np_out = np.arcsin(np_input)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))

    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / np.sqrt(1 - np_input ** 2)

    test_case.assertTrue(np.allclose(of_input.grad.numpy(), np_out_grad, 1e-4, 1e-4))


@flow.unittest.skip_unless_1n1d()
class TestAsin(flow.unittest.TestCase):
    def test_asin(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2,), (2, 3), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_asin(test_case, *arg)
            _test_arcsin(test_case, *arg)

    def test_flow_asin_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case, "asin", device=device,
            )

    def test_flow_arcsin_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case, "arcsin", device=device,
            )

    def test_flow_tensor_asin_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case, "asin", device=device,
            )

    def test_flow_tensor_arcsin_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case, "arcsin", device=device,
            )


def _test_asinh(test_case, shape, device):
    np_input = np.random.randn(*shape)
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )

    of_out = flow.asinh(of_input)
    np_out = np.arcsinh(np_input)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))

    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / np.sqrt(1 + np_input ** 2)

    test_case.assertTrue(np.allclose(of_input.grad.numpy(), np_out_grad, 1e-4, 1e-4))


def _test_arcsinh(test_case, shape, device):
    np_input = np.random.randn(*shape)
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )

    of_out = flow.arcsinh(of_input)
    np_out = np.arcsinh(np_input)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))

    of_out = of_out.sum()
    of_out.backward()
    np_out_grad = 1 / np.sqrt(1 + np_input ** 2)

    test_case.assertTrue(np.allclose(of_input.grad.numpy(), np_out_grad, 1e-4, 1e-4))


@flow.unittest.skip_unless_1n1d()
class TestAsinh(flow.unittest.TestCase):
    def test_asinh(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2,), (2, 3), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_asinh(test_case, *arg)
            _test_arcsinh(test_case, *arg)

    def test_flow_asinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case, "asinh", device=device,
            )

    def test_flow_arcsinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case, "arcsinh", device=device,
            )

    def test_flow_tensor_asinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case, "asinh", device=device,
            )

    def test_flow_tensor_arcsinh_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case, "arcsinh", device=device,
            )


def _topk_np(input, k, dim: int = None, largest: bool = True, _sorted: bool = True):
    in_dims = input.shape
    out_dims = list(in_dims)
    num_axes = len(input.shape)
    if dim < 0:
        dim = dim + num_axes
    n = in_dims[dim]
    if k > n:
        k = n
    out_dims[dim] = k
    out_dims = tuple(out_dims)
    prev_dims = 1
    next_dims = 1
    for i in range(dim):
        prev_dims *= in_dims[i]
    for i in range(dim + 1, len(in_dims)):
        next_dims *= in_dims[i]
    input_flat = input.reshape((prev_dims, n, next_dims))

    values_ref = np.ndarray(shape=(prev_dims, k, next_dims), dtype=input.dtype)
    values_ref.fill(0)
    indices_ref = np.ndarray(shape=(prev_dims, k, next_dims), dtype=np.int64)
    indices_ref.fill(-1)
    for i in range(prev_dims):
        for j in range(next_dims):
            kv = []
            for x in range(n):
                val = input_flat[i, x, j]
                y = x * next_dims + i * in_dims[dim] * next_dims + j
                kv.append((val, x, y))
            cnt = 0
            for val, x, y in sorted(kv, key=lambda x: (x[0], -x[1]), reverse=largest):
                values_ref[i, cnt, j] = val
                indices_ref[i, cnt, j] = x
                cnt += 1
                if cnt >= k or cnt >= n:
                    break

    values_ref = values_ref.reshape(out_dims)
    indices_ref = indices_ref.reshape(out_dims)

    return (values_ref, indices_ref)


def _test_topk_dim_negative(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 7), dtype=flow.float32, device=flow.device(device),
    )
    dim = -1
    k = 4
    (of_values, of_indices) = flow.topk(input, k=k, dim=dim)
    (np_values, np_indices) = _topk_np(input.numpy(), k=k, dim=dim)
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


def _test_tensor_topk(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 7), dtype=flow.float32, device=flow.device(device),
    )
    dim = 1
    k = 4
    (of_values, of_indices) = input.topk(k=k, dim=dim)
    (np_values, np_indices) = _topk_np(input.numpy(), k=k, dim=dim)
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


def _test_topk_dim_positive(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 7), dtype=flow.float32, device=flow.device(device),
    )
    dim = 2
    k = 4
    (of_values, of_indices) = flow.topk(input, k=k, dim=dim)
    (np_values, np_indices) = _topk_np(input.numpy(), k=k, dim=dim)
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


def _test_topk_largest(test_case, device):
    input = flow.Tensor(
        np.random.randn(2, 6, 5, 7), dtype=flow.float32, device=flow.device(device),
    )
    dim = 1
    k = 4
    largest = False
    (of_values, of_indices) = flow.topk(input, k=k, dim=dim, largest=False)
    (np_values, np_indices) = _topk_np(input.numpy(), k=k, dim=dim, largest=False)
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


def _test_topk_original(test_case, device):
    arg_dict = OrderedDict()
    arg_dict["shape"] = [(10, 10, 200)]
    arg_dict["axis"] = [-2, 0, 2]
    arg_dict["k"] = [1, 50, 200]
    arg_dict["largest"] = [True, False]
    arg_dict["data_type"] = ["float32", "double"]
    rng = np.random.default_rng()
    for (shape, axis, k, largest, data_type) in GenArgList(arg_dict):
        np_type = type_name_to_np_type[data_type]
        random_data = rng.standard_normal(size=shape, dtype=np_type)
        while np.unique(random_data).size != random_data.size:
            random_data = rng.standard_normal(size=shape, dtype=np_type)
        input = flow.Tensor(
            random_data,
            dtype=type_name_to_flow_type[data_type],
            device=flow.device(device),
        )
        (of_values, of_indices) = flow.topk(input, k=k, dim=axis, largest=largest)
        (np_values, np_indices) = _topk_np(
            input.numpy(), k=k, dim=axis, largest=largest
        )
        test_case.assertTrue(
            np.array_equal(of_values.numpy().flatten(), np_values.flatten())
        )
        test_case.assertTrue(
            np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
        )


@flow.unittest.skip_unless_1n1d()
class TestPow(flow.unittest.TestCase):
    def test_pow(test_case):
        input = flow.Tensor(np.array([1, 2, 3, 4, 5, 6]), dtype=flow.float32)
        of_out = flow.pow(input, 2.1)
        np_out = np.power(input.numpy(), 2.1)
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))

    def test_pow_tensor_function(test_case):
        input = flow.Tensor(np.array([1, 2, 3, 4, 5, 6]), dtype=flow.float32)
        of_out = input.pow(2.1)
        np_out = np.power(input.numpy(), 2.1)
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


@flow.unittest.skip_unless_1n1d()
class TestTopk(flow.unittest.TestCase):
    def test_topk(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_topk_dim_negative,
            _test_tensor_topk,
            _test_topk_dim_positive,
            _test_topk_largest,
            _test_topk_original,
        ]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


def arccosh_input_tensor(shape):
    def generator(_):
        low = 1
        high = 2
        rng = np.random.default_rng()
        np_arr = rng.random(size=shape) * (high - low) + low
        return (
            flow.Tensor(np_arr, dtype=flow.float32),
            torch.tensor(np_arr, dtype=torch.float32),
        )

    return generator


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
@flow.unittest.skip_unless_1n1d()
class TestArccosh(flow.unittest.TestCase):
    def test_arccosh_flow_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case,
                "arccosh",
                device=device,
                n=2,
                extra_generators={"input": arccosh_input_tensor((3, 3))},
            )

    def test_arccosh_tensor_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case,
                "arccosh",
                device=device,
                n=2,
                extra_generators={"input": arccosh_input_tensor((3, 3))},
            )


def _test_acosh_impl(test_case, shape, device):
    np_input = np.random.rand(*shape) + 2.0
    of_input = flow.Tensor(
        np_input, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    of_out = flow.acosh(of_input)
    np_out = np.arccosh(np_input)
    test_case.assertTrue(
        np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4, equal_nan=True)
    )

    of_out = of_out.sum()
    of_out.backward()
    np_grad = 1.0 / np.sqrt(np.square(np_input) - 1)
    test_case.assertTrue(
        np.allclose(of_input.grad.numpy(), np_grad, 1e-4, 1e-4, equal_nan=True)
    )


def acosh_input_tensor(shape):
    def generator(_):
        low = 1
        high = 2
        rng = np.random.default_rng()
        np_arr = rng.random(size=shape) * (high - low) + low
        return (
            flow.Tensor(np_arr, dtype=flow.float32),
            torch.tensor(np_arr, dtype=torch.float32),
        )

    return generator


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
@flow.unittest.skip_unless_1n1d()
class TestAcosh(flow.unittest.TestCase):
    def test_acosh(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2, 3), (2, 3, 4), (2, 4, 5, 6)]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_acosh_impl(test_case, *arg)

    def test_acosh_flow_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case,
                "acosh",
                device=device,
                n=2,
                extra_generators={"input": acosh_input_tensor((3, 3))},
            )

    def test_acosh_tensor_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_tensor_against_pytorch(
                test_case,
                "acosh",
                device=device,
                n=2,
                extra_generators={"input": acosh_input_tensor((3, 3))},
            )


def _test_atan2_forward(test_case, shape, scalar, device):
    np_input_x = 10 * np.random.rand(*shape)
    np_input_y = 10 * np.random.randn(*shape)
    of_input_x = flow.Tensor(np_input_x, dtype=flow.float32, device=flow.device(device))
    of_input_y = flow.Tensor(np_input_y, dtype=flow.float32, device=flow.device(device))
    of_out = flow.atan2(of_input_x, of_input_y)
    np_out = np.arctan2(np_input_x, np_input_y)
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_atan2_backward(test_case, device):
    np_input_x = np.random.rand(2, 3)
    np_input_y = np.random.rand(2, 3)

    np_y_grad = -1 * np_input_x / (np_input_x * np_input_x + np_input_y * np_input_y)
    np_x_grad = np_input_y / (np_input_x * np_input_x + np_input_y * np_input_y)

    def test_x_y_grad():
        of_input_x = flow.Tensor(
            np_input_x,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_input_y = flow.Tensor(
            np_input_y,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_x.grad.numpy(), np_x_grad, 1e-4, 1e-4)
        )
        test_case.assertTrue(
            np.allclose(of_input_y.grad.numpy(), np_y_grad, 1e-4, 1e-4)
        )

    def test_x_grad():
        of_input_x = flow.Tensor(
            np_input_x,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_input_y = flow.Tensor(
            np_input_y, dtype=flow.float32, device=flow.device(device)
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_x.grad.numpy(), np_x_grad, 1e-4, 1e-4)
        )

    def test_y_grad():
        of_input_x = flow.Tensor(
            np_input_x, dtype=flow.float32, device=flow.device(device)
        )
        of_input_y = flow.Tensor(
            np_input_y,
            dtype=flow.float32,
            device=flow.device(device),
            requires_grad=True,
        )
        of_out = flow.atan2(of_input_x, of_input_y)
        of_out_sum = of_out.sum()
        of_out_sum.backward()
        test_case.assertTrue(
            np.allclose(of_input_y.grad.numpy(), np_y_grad, 1e-4, 1e-4)
        )

    test_x_y_grad()
    test_x_grad()
    test_y_grad()


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
@flow.unittest.skip_unless_1n1d()
class TestAtan2(flow.unittest.TestCase):
    def test_atan2_forward(test_case):
        arg_dict = OrderedDict()
        arg_dict["shape"] = [(2,), (2, 3), (2, 3, 4), (2, 3, 4, 5)]
        arg_dict["scalar"] = [2.1, 0.8]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_atan2_forward(test_case, *arg)

    def test_atan2_backward(test_case):
        arg_dict = OrderedDict()
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            _test_atan2_backward(test_case, *arg)

    def test_flow_atan2_with_random_data(test_case):
        for device in ["cpu", "cuda"]:
            test_flow_against_pytorch(
                test_case,
                "atan2",
                extra_annotations={"other": flow.Tensor},
                extra_generators={
                    "input": random_tensor(ndim=1, dim1=1),
                    "other": random_tensor(ndim=1, dim1=1),
                },
                device=device,
            )


if __name__ == "__main__":
    unittest.main()

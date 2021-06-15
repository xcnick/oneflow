/*
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
*/

#include "oneflow/core/framework/attr_map.h"
#include "oneflow/core/framework/op_builder.h"
#include "oneflow/core/framework/op_expr.h"
#include "oneflow/core/framework/op_interpreter/op_interpreter_util.h"
#include "oneflow/core/framework/tensor.h"
#include "oneflow/core/framework/tensor_tuple.h"
#include "oneflow/core/functional/function_library.h"
#include "oneflow/core/functional/impl/common.h"
#include "oneflow/core/functional/impl/unary_functor.h"
#include "oneflow/core/functional/scalar.h"

namespace oneflow {
namespace one {
namespace functional {

namespace impl {

class BiasAddFunctor {
 public:
  BiasAddFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("bias_add").Input("a").Input("b").Output("out").Build());
  }
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& x,
                           const std::shared_ptr<one::Tensor>& bias, const int32_t& axis) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<int32_t>("axis", axis));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {x, bias}, attrs);
  }

 private:
  std::shared_ptr<OpExpr> op_;
};

class Conv2DFunctor {
 public:
  Conv2DFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("conv2d").Input("in").Input("weight").Output("out").Build());
  }
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& x,
                           const std::shared_ptr<one::Tensor>& weight, const int32_t& filters,
                           const std::vector<int32_t>& kernel_size,
                           const std::vector<int32_t>& strides,
                           const std::vector<int32_t>& padding_before,
                           const std::vector<int32_t>& dilation_rate, const int32_t& groups,
                           const std::string& data_format) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<int32_t>("filters", filters));
    JUST(attrs.SetAttr<std::vector<int32_t>>("kernel_size", kernel_size));
    JUST(attrs.SetAttr<std::vector<int32_t>>("strides", strides));
    JUST(attrs.SetAttr<std::vector<int32_t>>("padding_before", padding_before));
    JUST(attrs.SetAttr<std::vector<int32_t>>("dilation_rate", dilation_rate));
    JUST(attrs.SetAttr<int32_t>("groups", groups));
    JUST(attrs.SetAttr<std::string>("data_format", data_format));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {x, weight}, attrs);
  }

 private:
  std::shared_ptr<OpExpr> op_;
};

class Conv2DataGradFunctor {
  public:
   Conv2DFunctor() {
     op_ = CHECK_JUST(one::OpBui)
   }
}

class MatMulBaseFunctor {
 public:
  MatMulBaseFunctor() = default;
  virtual ~MatMulBaseFunctor() = default;
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& a,
                           const std::shared_ptr<one::Tensor>& b, const bool& transpose_a,
                           const bool& transpose_b, const double& alpha) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<bool>("transpose_a", transpose_a));
    JUST(attrs.SetAttr<bool>("transpose_b", transpose_b));
    JUST(attrs.SetAttr<double>("alpha", alpha));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {a, b}, attrs);
  }

 protected:
  std::shared_ptr<OpExpr> op_;
};

class MatMulFunctor : public MatMulBaseFunctor {
 public:
  MatMulFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("matmul").Input("a").Input("b").Output("out").Build());
  }
};

class BatchMatMulFunctor : public MatMulBaseFunctor {
 public:
  BatchMatMulFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("batch_matmul").Input("a").Input("b").Output("out").Build());
  }
};

class BroadcastMatMulFunctor : public MatMulBaseFunctor {
 public:
  BroadcastMatMulFunctor() {
    op_ =
        CHECK_JUST(one::OpBuilder("broadcast_matmul").Input("a").Input("b").Output("out").Build());
  }
};

class LayerNormFunctor {
 public:
  LayerNormFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("layer_norm")
                         .Input("x")
                         .Output("y")
                         .Output("mean")
                         .Output("inv_variance")
                         .Build());
  }
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& x, const int64_t& begin_norm_axis,
                           const int64_t& begin_params_axis, const double& epsilon) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<int64_t>("begin_norm_axis", begin_norm_axis));
    JUST(attrs.SetAttr<int64_t>("begin_params_axis", begin_params_axis));
    JUST(attrs.SetAttr<double>("epsilon", epsilon));
    JUST(attrs.SetAttr<bool>("center", false));
    JUST(attrs.SetAttr<bool>("scale", false));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {x}, attrs);
  }

 private:
  std::shared_ptr<OpExpr> op_;
};

class LayerNormAffineFunctor {
 public:
  LayerNormAffineFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("layer_norm")
                         .Input("x")
                         .Input("beta")
                         .Input("gamma")
                         .Output("y")
                         .Output("mean")
                         .Output("inv_variance")
                         .Output("normalized")
                         .Build());
  }
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& x,
                           const std::shared_ptr<one::Tensor>& beta,
                           const std::shared_ptr<one::Tensor>& gamma,
                           const int64_t& begin_norm_axis, const int64_t& begin_params_axis,
                           const double& epsilon) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<int64_t>("begin_norm_axis", begin_norm_axis));
    JUST(attrs.SetAttr<int64_t>("begin_params_axis", begin_params_axis));
    JUST(attrs.SetAttr<double>("epsilon", epsilon));
    JUST(attrs.SetAttr<bool>("center", true));
    JUST(attrs.SetAttr<bool>("scale", true));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {x, beta, gamma}, attrs);
  }

 private:
  std::shared_ptr<OpExpr> op_;
};

class Pool2DFunctor {
 public:
  Pool2DFunctor() = default;
  virtual ~Pool2DFunctor() = default;
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& x,
                           const std::vector<int32_t>& kernel_size,
                           const std::vector<int32_t>& strides, const std::string& padding,
                           const std::vector<int32_t>& padding_before,
                           const std::vector<int32_t>& padding_after,
                           const std::string& data_format, const bool& ceil_mode) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<std::vector<int32_t>>("pool_size", kernel_size));
    JUST(attrs.SetAttr<std::vector<int32_t>>("strides", strides));
    JUST(attrs.SetAttr<std::string>("padding", padding));
    JUST(attrs.SetAttr<std::vector<int32_t>>("padding_before", padding_before));
    JUST(attrs.SetAttr<std::vector<int32_t>>("padding_after", padding_after));
    JUST(attrs.SetAttr<std::string>("data_format", data_format));
    JUST(attrs.SetAttr<bool>("ceil_mode", ceil_mode));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {x}, attrs);
  }

 protected:
  std::shared_ptr<OpExpr> op_;
};

class AvgPool2DFunctor : public Pool2DFunctor {
 public:
  AvgPool2DFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("avg_pool_2d").Input("x").Output("y").Build());
  }
};

class MaxPool2DFunctor : public Pool2DFunctor {
 public:
  MaxPool2DFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("max_pool_2d").Input("x").Output("y").Build());
  }
};

class SparseSoftmaxCrossEntropyFunctor {
 public:
  SparseSoftmaxCrossEntropyFunctor() {
    op_ = CHECK_JUST(one::OpBuilder("sparse_softmax_cross_entropy")
                         .Input("prediction")
                         .Input("label")
                         .Output("out")
                         .Output("prob")
                         .Build());
  }
  Maybe<Tensor> operator()(const std::shared_ptr<one::Tensor>& logits,
                           const std::shared_ptr<one::Tensor>& label, const int64_t& depth) const {
    MutableAttrMap attrs;
    JUST(attrs.SetAttr<int64_t>("depth", depth));
    return OpInterpUtil::Dispatch<Tensor>(*op_, {logits, label}, attrs);
  }

 private:
  std::shared_ptr<OpExpr> op_;
};

}  // namespace impl

ONEFLOW_FUNCTION_LIBRARY(m) {
  m.add_functor<impl::BiasAddFunctor>("BiasAdd");
  m.add_functor<impl::Conv2DFunctor>("Conv2D");
  m.add_functor<impl::MatMulFunctor>("MatMul");
  m.add_functor<impl::BatchMatMulFunctor>("BatchMatMul");
  m.add_functor<impl::BroadcastMatMulFunctor>("BroadcastMatMul");
  m.add_functor<impl::LayerNormFunctor>("LayerNorm");
  m.add_functor<impl::LayerNormAffineFunctor>("LayerNormAffine");
  m.add_functor<impl::AvgPool2DFunctor>("AvgPool2D");
  m.add_functor<impl::MaxPool2DFunctor>("MaxPool2D");
  m.add_functor<impl::SparseSoftmaxCrossEntropyFunctor>("SparseSoftmaxCrossEntropy");
};

}  // namespace functional
}  // namespace one
}  // namespace oneflow
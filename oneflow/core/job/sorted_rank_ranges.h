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
#ifndef ONEFLOW_CORE_JOB_SORTED_RANK_RANGES_
#define ONEFLOW_CORE_JOB_SORTED_RANK_RANGES_

#include <functional>
#include <vector>
#include <unordered_map>
#include <string>
#include <memory>
#include "oneflow/core/common/symbol.h"
#include "oneflow/core/common/range.h"
#include "oneflow/core/common/maybe.h"

namespace oneflow {

class ParallelDesc;

class SortedRankRanges final {
 public:
  ~SortedRankRanges() = default;

  static Maybe<Symbol<SortedRankRanges>> New4SoleDevicePerRankParallelDesc(
      Symbol<ParallelDesc> parallel_desc);
  static Maybe<SortedRankRanges> New4SoleDevicePerRankParallelDesc(
      const ParallelDesc& parallel_desc);

  bool operator==(const SortedRankRanges& that) const {
    return this->sorted_rank_ranges_ == that.sorted_rank_ranges_;
  }
  bool operator!=(const SortedRankRanges& that) const { return !(*this == that); }

  const std::vector<Range>& sorted_rank_ranges() const { return sorted_rank_ranges_; }
	size_t size() const { return size_; }
  size_t hash_value() const { return hash_value_; }
	Maybe<int64_t> GetNextRankInRing(int64_t rank) const;
	Maybe<int64_t> GetNextRankInRing() const;
	Maybe<int64_t> GetPrevRankInRing(int64_t rank) const;
	Maybe<int64_t> GetPrevRankInRing() const;
	bool ContainingCurrentRank() const;

	Maybe<void> ForEachRank(const std::function<Maybe<void>(int64_t)>&) const;

 private:
  SortedRankRanges() = default;
  Maybe<void> Init();

  std::vector<Range> sorted_rank_ranges_;
	std::unordered_map<int64_t, int64_t> rank2next_rank_in_ring_;
	std::unordered_map<int64_t, int64_t> rank2prev_rank_in_ring_;
	size_t size_;
  size_t hash_value_;
};

}  // namespace oneflow

namespace std {

template<>
struct hash<oneflow::SortedRankRanges> final {
  size_t operator()(const oneflow::SortedRankRanges& sorted_rank_ranges) const {
    return sorted_rank_ranges.hash_value();
  }
};

}  // namespace std

#endif  // ONEFLOW_CORE_JOB_SORTED_RANK_RANGES_

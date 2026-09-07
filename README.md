# AC 自动机 Benchmark 结果

## 简介

本项目对多个 Go 语言 Aho-Corasick（AC 自动机）开源库进行性能基准测试，对比维度包括 **建树产物大小**、**建树内存申请量**、**建树耗时**、**匹配耗时**。

### 测试数据

- **词表规模**：每组包含 100 / 1,000 / 10,000 / 100,000 个互不重复的 pattern（词条）。

- **纯中文词条**：由 `U+4E00`～`U+9FA5` 范围内的汉字生成；词长为 2～4 个汉字，其中 2 字词占 50%、3 字词占 35%、4 字词占 15%。

- **纯英文词条**：由 26 个小写英文字母生成；词长服从均值为 6、标准差为 2 的近似正态分布，并限制在 3～12 个字母之间。

- **中英混合词表**：生成每个词条时各以 50% 的概率选择中文或英文，词长规则分别沿用上述配置。

- **字符分布**：字符按齐夫分布采样，使少数字符高频、大量字符低频；中文字符多样性随词表规模增加，英文字符池固定为 26 个小写字母。所有生成结果都会去重，直到达到目标词条数量。

- **匹配文本**：每组生成约 100 KB 的同语言类型文本；生成过程中有 10% 的概率直接插入词表中的词条，以保证稳定的命中样本。随机数种子固定，确保各次 Benchmark 使用相同数据。

### 对比库

| 库 | Benchmark 名 | 实现算法 | 索引粒度 | 完整匹配结果 | 后缀链接 | 其它 |
|---|---|---|---|---|---|---|
| [china-tjj/ahocorasick](https://github.com/china-tjj/ahocorasick) | china-tjj | 标准Trie | rune | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型 |
| 同上 | china-tjj(FB) | 标准Trie | rune | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型，启用快速构建模式 |
| 同上 | china-tjj(U64) | 标准Trie | rune | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型 |
| 同上 | china-tjj(U64+OL) | 标准Trie | rune | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接 |
| 同上 | china-tjj(U64+TI) | 标准Trie | rune | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型，返回结果含pattern id |
| 同上 | china-tjj(U64+OL+TI) | 标准Trie | rune | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接，返回结果含pattern id |
| [BobuSumisu/aho-corasick](https://github.com/BobuSumisu/aho-corasick) | BobuSumisu-ac | 标准Trie + 预计算转移表 | byte | 完整 | 有 | 返回Match含pattern id与位置；sync.Pool复用；支持Encode/Decode(gzip) |
| [BobuSumisu/go-ahocorasick](https://github.com/BobuSumisu/go-ahocorasick) | BobuSumisu-go-ac | 双数组Trie(DAT) | byte | 完整 | 有 | SaveTrie/LoadTrie；Match结果不含pattern索引(仅pos+match bytes) |
| [anknown/ahocorasick](https://github.com/anknown/ahocorasick) | anknown | 双数组Trie(DAT) | rune | 完整 | 有 | 输出在构建时合并到output(等价后缀链效果)；Term不含pattern索引(靠Word) |
| [TheFutureIsOurs/ahocorasick](https://github.com/TheFutureIsOurs/ahocorasick) | TheFutureIsOurs | 双数组Trie(DAT) | rune | 不完整 | 有 | output压缩：同终点/后缀只保留最长term；主打低内存/低GC |
| [orbit-w/aho_corasick](https://github.com/orbit-w/aho_corasick) | orbit-w | 双数组Trie(DAT) | rune | 完整 | 有 | Trie构建时把fail节点output合并到当前节点；提供Validate/Replace等 |
| [sepetrov/ahocorasick](https://github.com/sepetrov/ahocorasick) | sepetrov | 标准Trie | rune | 完整 | 有 | 返回map[patternIndex][]pos(位置是byte offset)；含suffixLink+dictSuffixLink |
| [cloudflare/ahocorasick](https://github.com/cloudflare/ahocorasick) | cloudflare | 标准Trie | byte | 不完整 | 有 | Match返回命中过的pattern集合(去重、无位置)；有MatchThreadSafe/Contains |
| [petar-dambovaliev/aho-corasick](https://github.com/petar-dambovaliev/aho-corasick) | petar-dambovaliev | NFA/DFA | byte | 完整 | 有 | 多种MatchKind；Standard可完整/可重叠；LeftMost*会裁剪；含prefilter/Replace/迭代器 |
| [iohub/ahocorasick](https://github.com/iohub/ahocorasick) | iohub | cedar 双数组Trie | byte | 完整 | 有 | value可存任意interface{}；迭代器输出；sync.Pool复用；graphviz可视化 |
| [ClarkThan/ahocorasick](https://github.com/ClarkThan/ahocorasick) | ClarkThan | 标准Trie | rune | 完整 | 有 | SearchAppend/SearchIndexedAppend支持buf复用；输出不含pattern索引(只有Hit{Start,Len}或string) |
| [pgavlin/aho-corasick](https://github.com/pgavlin/aho-corasick) | pgavlin | NFA/DFA | byte | 完整 | 有 | 基本同petar分支；Standard可完整；LeftMost*会裁剪 |
| [gnames/aho_corasick](https://github.com/gnames/aho_corasick) | gnames | 标准Trie | byte | 不完整 | 有 | dict link实现为单跳(仅linkDict一次，不会多级追溯)，可能漏更深后缀命中；Match含pattern索引+start/end |

## 图表总览

### 建树产物大小

![建树产物大小](bench_build_retained.png)

### 建树内存申请量

![建树内存申请量](bench_build_alloc.png)

### 建树耗时

![建树耗时](bench_build_time.png)

### 匹配耗时

![匹配耗时](bench_match_time.png)

---

## 详细数据

### 纯中文

#### 词表规模：100

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 2.7KB | 3.2KB | 14.7µs | 868.8µs |
| china-tjj(FB) | 2.7KB | 8.9KB | 15.8µs | 847.8µs |
| china-tjj(U64) | 7.2KB | 9.0KB | 14.7µs | 784.3µs |
| china-tjj(U64+OL) | 9.2KB | 11.0KB | 15.0µs | 756.0µs |
| china-tjj(U64+TI) | 9.0KB | 10.8KB | 14.9µs | 792.1µs |
| china-tjj(U64+OL+TI) | 11.0KB | 12.8KB | 15.1µs | 776.2µs |
| BobuSumisu-ac | 1.33MB | 1.50MB | 221.5µs | 439.7µs |
| BobuSumisu-go-ac | 32.8KB | 60.9KB | 365.2µs | 484.5µs |
| anknown | 1.42MB | 2.66MB | 225.0µs | 559.4µs |
| TheFutureIsOurs | 2.09MB | 7.57MB | 456.7µs | 212.3µs |
| orbit-w | 2.57MB | 3.60MB | 119.8µs | 184.7µs |
| sepetrov | 44.0KB | 58.8KB | 31.7µs | 590.7µs |
| cloudflare | 3.22MB | 3.26MB | 672.2µs | 282.3µs |
| petar-dambovaliev | 102.0KB | 226.7KB | 82.9µs | 1.20ms |
| iohub | 52.4KB | 125.6KB | 60.3µs | 544.7µs |
| ClarkThan | 41.3KB | 45.8KB | 28.6µs | 597.6µs |
| pgavlin | 102.0KB | 225.5KB | 81.3µs | 1.25ms |
| gnames | 157.2KB | 190.9KB | 117.0µs | 2.12ms |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 25.5KB | 29.5KB | 211.3µs | 1.36ms |
| china-tjj(FB) | 25.5KB | 81.3KB | 180.6µs | 1.22ms |
| china-tjj(U64) | 70.2KB | 86.3KB | 219.0µs | 1.11ms |
| china-tjj(U64+OL) | 90.2KB | 106.3KB | 202.3µs | 1.10ms |
| china-tjj(U64+TI) | 86.2KB | 102.3KB | 203.4µs | 1.24ms |
| china-tjj(U64+OL+TI) | 106.2KB | 122.3KB | 211.1µs | 1.28ms |
| BobuSumisu-ac | 12.00MB | 13.51MB | 1.76ms | 461.0µs |
| BobuSumisu-go-ac | 280.1KB | 727.3KB | 11.12ms | 535.4µs |
| anknown | 1.58MB | 3.56MB | 644.5µs | 461.8µs |
| TheFutureIsOurs | 2.09MB | 7.89MB | 727.8µs | 240.6µs |
| orbit-w | 2.77MB | 4.07MB | 865.8µs | 206.6µs |
| sepetrov | 425.2KB | 599.1KB | 319.9µs | 832.1µs |
| cloudflare | 31.77MB | 32.12MB | 5.10ms | 750.4µs |
| petar-dambovaliev | 661.4KB | 2.21MB | 867.3µs | 1.62ms |
| iohub | 428.0KB | 1.12MB | 527.2µs | 621.4µs |
| ClarkThan | 398.5KB | 437.3KB | 292.6µs | 811.3µs |
| pgavlin | 661.4KB | 2.20MB | 855.7µs | 1.58ms |
| gnames | 1.37MB | 1.71MB | 1.09ms | 2.37ms |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 277.4KB | 330.7KB | 3.94ms | 722.7µs |
| china-tjj(FB) | 277.4KB | 815.9KB | 1.66ms | 731.8µs |
| china-tjj(U64) | 720.4KB | 936.5KB | 4.30ms | 727.3µs |
| china-tjj(U64+OL) | 904.4KB | 1.09MB | 4.12ms | 766.1µs |
| china-tjj(U64+TI) | 880.4KB | 1.07MB | 4.03ms | 782.9µs |
| china-tjj(U64+OL+TI) | 1.04MB | 1.25MB | 4.07ms | 794.7µs |
| BobuSumisu-ac | 110.61MB | 125.22MB | 14.42ms | 865.9µs |
| BobuSumisu-go-ac | 2.53MB | 8.92MB | 727.37ms | 786.7µs |
| anknown | 3.76MB | 16.66MB | 6.78ms | 668.4µs |
| TheFutureIsOurs | 2.09MB | 11.20MB | 3.49ms | 350.4µs |
| orbit-w | 3.12MB | 9.05MB | 64.92ms | 314.3µs |
| sepetrov | 3.77MB | 5.11MB | 3.54ms | 1.32ms |
| cloudflare | 317.17MB | 320.84MB | 61.84ms | 1.41ms |
| petar-dambovaliev | 5.60MB | 22.75MB | 10.18ms | 2.54ms |
| iohub | 3.33MB | 9.65MB | 5.17ms | 933.8µs |
| ClarkThan | 3.54MB | 3.84MB | 3.17ms | 1.23ms |
| pgavlin | 5.60MB | 22.63MB | 12.06ms | 2.19ms |
| gnames | 12.53MB | 16.69MB | 12.37ms | 3.23ms |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 2.81MB | 3.64MB | 49.97ms | 1.17ms |
| china-tjj(FB) | 2.81MB | 9.25MB | 22.40ms | 1.26ms |
| china-tjj(U64) | 4.91MB | 6.56MB | 48.32ms | 1.17ms |
| china-tjj(U64+OL) | 6.29MB | 7.94MB | 50.23ms | 1.31ms |
| china-tjj(U64+TI) | 6.44MB | 8.09MB | 48.52ms | 1.20ms |
| china-tjj(U64+OL+TI) | 7.82MB | 9.47MB | 50.20ms | 1.26ms |
| BobuSumisu-ac | 914.27MB | 1.007GB | 380.64ms | 2.62ms |
| BobuSumisu-go-ac | 19.40MB | 73.78MB | 44.525s | 1.29ms |
| anknown | 17.24MB | 110.84MB | 63.34ms | 1.08ms |
| TheFutureIsOurs | 8.19MB | 69.22MB | 83.64ms | 398.8µs |
| orbit-w | 9.83MB | 39.88MB | 1.330s | 391.6µs |
| sepetrov | 26.35MB | 36.96MB | 39.54ms | 2.45ms |
| cloudflare | 3.097GB | 3.132GB | 1.090s | 4.97ms |
| petar-dambovaliev | 50.38MB | 229.34MB | 220.83ms | 6.50ms |
| iohub | 26.60MB | 78.90MB | 57.19ms | 1.55ms |
| ClarkThan | 25.26MB | 29.39MB | 37.84ms | 2.00ms |
| pgavlin | 50.38MB | 228.09MB | 209.20ms | 4.59ms |
| gnames | 100.12MB | 138.67MB | 151.15ms | 4.94ms |

### 纯英文

#### 词表规模：100

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 5.2KB | 5.7KB | 24.1µs | 2.05ms |
| china-tjj(FB) | 5.2KB | 13.7KB | 21.3µs | 2.02ms |
| china-tjj(U64) | 14.2KB | 16.0KB | 23.9µs | 1.81ms |
| china-tjj(U64+OL) | 18.2KB | 20.0KB | 23.5µs | 1.69ms |
| china-tjj(U64+TI) | 16.0KB | 17.8KB | 23.0µs | 2.12ms |
| china-tjj(U64+OL+TI) | 20.0KB | 21.8KB | 24.0µs | 1.81ms |
| BobuSumisu-ac | 1.01MB | 1.13MB | 169.0µs | 476.6µs |
| BobuSumisu-go-ac | 29.5KB | 57.1KB | 256.7µs | 536.2µs |
| anknown | 38.0KB | 192.2KB | 88.3µs | 1.35ms |
| TheFutureIsOurs | 37.1KB | 142.8KB | 45.5µs | 731.1µs |
| orbit-w | 30.8KB | 123.1KB | 36.8µs | 728.0µs |
| sepetrov | 101.8KB | 130.7KB | 75.6µs | 2.08ms |
| cloudflare | 2.46MB | 2.49MB | 490.8µs | 347.0µs |
| petar-dambovaliev | 95.4KB | 182.9KB | 74.3µs | 1.53ms |
| iohub | 52.4KB | 113.1KB | 45.7µs | 788.5µs |
| ClarkThan | 93.1KB | 96.0KB | 60.3µs | 2.03ms |
| pgavlin | 95.4KB | 182.0KB | 74.4µs | 1.47ms |
| gnames | 114.0KB | 137.1KB | 103.7µs | 2.29ms |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 45.5KB | 49.5KB | 280.7µs | 2.57ms |
| china-tjj(FB) | 45.5KB | 123.9KB | 213.7µs | 2.53ms |
| china-tjj(U64) | 130.2KB | 146.3KB | 283.6µs | 2.29ms |
| china-tjj(U64+OL) | 170.2KB | 186.3KB | 274.8µs | 2.08ms |
| china-tjj(U64+TI) | 146.2KB | 162.3KB | 267.8µs | 2.35ms |
| china-tjj(U64+OL+TI) | 186.2KB | 202.3KB | 271.6µs | 2.11ms |
| BobuSumisu-ac | 8.27MB | 9.31MB | 1.24ms | 726.9µs |
| BobuSumisu-go-ac | 200.1KB | 493.9KB | 5.84ms | 708.0µs |
| anknown | 293.4KB | 1.70MB | 836.9µs | 1.34ms |
| TheFutureIsOurs | 160.1KB | 1.02MB | 437.6µs | 821.3µs |
| orbit-w | 229.8KB | 1008.0KB | 426.6µs | 737.2µs |
| sepetrov | 816.0KB | 1.00MB | 659.2µs | 2.79ms |
| cloudflare | 23.84MB | 24.09MB | 4.28ms | 684.2µs |
| petar-dambovaliev | 462.7KB | 1.43MB | 676.1µs | 2.16ms |
| iohub | 428.0KB | 1005.4KB | 435.5µs | 1.02ms |
| ClarkThan | 748.5KB | 777.2KB | 534.7µs | 2.60ms |
| pgavlin | 462.7KB | 1.42MB | 664.0µs | 2.15ms |
| gnames | 955.8KB | 1.23MB | 1.01ms | 3.08ms |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 344.2KB | 384.3KB | 4.75ms | 3.37ms |
| china-tjj(FB) | 344.2KB | 1.09MB | 3.02ms | 3.39ms |
| china-tjj(U64) | 944.2KB | 1.08MB | 4.87ms | 3.39ms |
| china-tjj(U64+OL) | 1.19MB | 1.34MB | 5.32ms | 3.21ms |
| china-tjj(U64+TI) | 1.08MB | 1.23MB | 5.08ms | 3.73ms |
| china-tjj(U64+OL+TI) | 1.34MB | 1.50MB | 5.14ms | 3.15ms |
| BobuSumisu-ac | 68.02MB | 76.54MB | 9.63ms | 1.79ms |
| BobuSumisu-go-ac | 1.55MB | 5.27MB | 266.67ms | 1.62ms |
| anknown | 3.18MB | 17.80MB | 10.86ms | 2.57ms |
| TheFutureIsOurs | 1.34MB | 10.84MB | 6.13ms | 1.51ms |
| orbit-w | 1.73MB | 7.86MB | 6.07ms | 1.41ms |
| sepetrov | 6.42MB | 8.74MB | 7.28ms | 5.41ms |
| cloudflare | 243.72MB | 246.33MB | 49.75ms | 1.61ms |
| petar-dambovaliev | 3.76MB | 15.36MB | 7.94ms | 4.46ms |
| iohub | 3.33MB | 7.99MB | 4.00ms | 2.33ms |
| ClarkThan | 5.90MB | 6.12MB | 5.43ms | 4.30ms |
| pgavlin | 3.76MB | 15.28MB | 7.41ms | 4.06ms |
| gnames | 7.47MB | 10.45MB | 10.46ms | 5.90ms |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 4.38MB | 5.14MB | 57.41ms | 4.42ms |
| china-tjj(FB) | 4.38MB | 16.93MB | 37.49ms | 4.76ms |
| china-tjj(U64) | 7.65MB | 9.18MB | 59.29ms | 4.73ms |
| china-tjj(U64+OL) | 9.84MB | 11.37MB | 61.82ms | 4.41ms |
| china-tjj(U64+TI) | 9.18MB | 10.71MB | 61.03ms | 4.64ms |
| china-tjj(U64+OL+TI) | 11.37MB | 12.90MB | 61.89ms | 4.25ms |
| BobuSumisu-ac | 567.08MB | 637.44MB | 211.12ms | 3.89ms |
| BobuSumisu-go-ac | 12.33MB | 46.46MB | 15.662s | 3.14ms |
| anknown | 42.24MB | 192.22MB | 142.98ms | 5.44ms |
| TheFutureIsOurs | 10.50MB | 96.68MB | 73.65ms | 2.26ms |
| orbit-w | 16.26MB | 67.28MB | 140.71ms | 2.42ms |
| sepetrov | 51.95MB | 68.84MB | 85.05ms | 12.52ms |
| cloudflare | 2.465GB | 2.491GB | 918.64ms | 3.32ms |
| petar-dambovaliev | 33.27MB | 133.45MB | 147.18ms | 6.01ms |
| iohub | 26.60MB | 65.21MB | 43.18ms | 5.33ms |
| ClarkThan | 47.83MB | 49.77MB | 82.84ms | 9.57ms |
| pgavlin | 33.27MB | 132.59MB | 151.42ms | 5.77ms |
| gnames | 60.81MB | 89.14MB | 146.05ms | 16.38ms |

### 中英混合

#### 词表规模：100

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 4.0KB | 4.4KB | 19.1µs | 1.29ms |
| china-tjj(FB) | 4.0KB | 11.9KB | 19.3µs | 1.22ms |
| china-tjj(U64) | 10.7KB | 12.5KB | 18.6µs | 1.20ms |
| china-tjj(U64+OL) | 13.7KB | 15.5KB | 19.1µs | 1.18ms |
| china-tjj(U64+TI) | 12.5KB | 14.3KB | 19.6µs | 1.33ms |
| china-tjj(U64+OL+TI) | 15.5KB | 17.3KB | 19.4µs | 1.23ms |
| BobuSumisu-ac | 1.22MB | 1.37MB | 212.2µs | 480.8µs |
| BobuSumisu-go-ac | 32.0KB | 61.5KB | 343.1µs | 586.0µs |
| anknown | 1.18MB | 2.00MB | 209.6µs | 890.3µs |
| TheFutureIsOurs | 1.66MB | 5.49MB | 421.3µs | 405.0µs |
| orbit-w | 2.20MB | 3.24MB | 281.2µs | 331.6µs |
| sepetrov | 72.2KB | 95.0KB | 51.8µs | 922.2µs |
| cloudflare | 2.85MB | 2.89MB | 536.0µs | 305.6µs |
| petar-dambovaliev | 129.4KB | 252.0KB | 84.6µs | 1.36ms |
| iohub | 52.4KB | 121.4KB | 49.7µs | 612.4µs |
| ClarkThan | 66.6KB | 71.1KB | 41.7µs | 1.20ms |
| pgavlin | 129.4KB | 251.0KB | 83.4µs | 1.35ms |
| gnames | 142.6KB | 173.7KB | 109.2µs | 2.35ms |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 36.2KB | 40.3KB | 245.9µs | 1.65ms |
| china-tjj(FB) | 36.2KB | 113.8KB | 200.9µs | 1.63ms |
| china-tjj(U64) | 98.2KB | 114.3KB | 240.8µs | 1.60ms |
| china-tjj(U64+OL) | 126.2KB | 142.3KB | 254.1µs | 1.50ms |
| china-tjj(U64+TI) | 114.2KB | 130.3KB | 241.2µs | 1.72ms |
| china-tjj(U64+OL+TI) | 142.2KB | 158.3KB | 240.8µs | 1.63ms |
| BobuSumisu-ac | 10.77MB | 12.12MB | 1.66ms | 528.7µs |
| BobuSumisu-go-ac | 264.1KB | 704.0KB | 8.97ms | 604.1µs |
| anknown | 1.59MB | 4.15MB | 887.1µs | 861.6µs |
| TheFutureIsOurs | 2.09MB | 6.36MB | 760.1µs | 504.1µs |
| orbit-w | 2.77MB | 4.19MB | 614.7µs | 454.0µs |
| sepetrov | 678.2KB | 948.0KB | 575.6µs | 1.36ms |
| cloudflare | 27.93MB | 28.25MB | 4.84ms | 659.6µs |
| petar-dambovaliev | 591.1KB | 1.82MB | 781.5µs | 1.86ms |
| iohub | 428.0KB | 1.07MB | 530.8µs | 803.9µs |
| ClarkThan | 626.5KB | 668.6KB | 449.2µs | 1.51ms |
| pgavlin | 591.1KB | 1.81MB | 801.9µs | 1.88ms |
| gnames | 1.22MB | 1.55MB | 1.13ms | 2.82ms |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 322.9KB | 370.9KB | 4.38ms | 1.28ms |
| china-tjj(FB) | 322.9KB | 1.02MB | 2.40ms | 1.37ms |
| china-tjj(U64) | 868.4KB | 1.04MB | 4.50ms | 1.25ms |
| china-tjj(U64+OL) | 1.08MB | 1.27MB | 4.51ms | 1.25ms |
| china-tjj(U64+TI) | 1.00MB | 1.19MB | 4.46ms | 1.39ms |
| china-tjj(U64+OL+TI) | 1.24MB | 1.43MB | 4.50ms | 1.33ms |
| BobuSumisu-ac | 92.91MB | 104.87MB | 11.76ms | 982.0µs |
| BobuSumisu-go-ac | 2.03MB | 6.98MB | 509.42ms | 872.6µs |
| anknown | 2.94MB | 15.01MB | 17.35ms | 1.27ms |
| TheFutureIsOurs | 2.09MB | 12.06MB | 4.93ms | 650.7µs |
| orbit-w | 3.11MB | 9.82MB | 25.03ms | 626.0µs |
| sepetrov | 5.45MB | 7.52MB | 5.57ms | 2.24ms |
| cloudflare | 278.34MB | 281.57MB | 59.21ms | 1.10ms |
| petar-dambovaliev | 4.66MB | 18.89MB | 7.97ms | 2.66ms |
| iohub | 3.33MB | 8.95MB | 4.55ms | 1.23ms |
| ClarkThan | 5.05MB | 5.38MB | 4.84ms | 2.44ms |
| pgavlin | 4.66MB | 18.79MB | 10.52ms | 2.78ms |
| gnames | 10.41MB | 13.93MB | 12.17ms | 4.32ms |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 3.78MB | 4.60MB | 53.61ms | 1.81ms |
| china-tjj(FB) | 3.78MB | 12.95MB | 28.49ms | 1.97ms |
| china-tjj(U64) | 6.61MB | 8.25MB | 54.82ms | 1.77ms |
| china-tjj(U64+OL) | 8.48MB | 10.12MB | 58.36ms | 1.79ms |
| china-tjj(U64+TI) | 8.14MB | 9.78MB | 54.72ms | 1.87ms |
| china-tjj(U64+OL+TI) | 10.01MB | 11.65MB | 55.10ms | 1.82ms |
| BobuSumisu-ac | 788.88MB | 891.76MB | 343.26ms | 1.72ms |
| BobuSumisu-go-ac | 15.98MB | 60.00MB | 32.803s | 1.64ms |
| anknown | 26.16MB | 144.72MB | 156.02ms | 2.26ms |
| TheFutureIsOurs | 10.25MB | 87.62MB | 60.59ms | 961.9µs |
| orbit-w | 13.99MB | 59.20MB | 618.63ms | 1.07ms |
| sepetrov | 41.17MB | 55.57MB | 69.42ms | 5.19ms |
| cloudflare | 2.770GB | 2.801GB | 1.171s | 5.83ms |
| petar-dambovaliev | 43.58MB | 184.45MB | 212.57ms | 5.37ms |
| iohub | 26.60MB | 73.92MB | 51.60ms | 3.52ms |
| ClarkThan | 38.35MB | 40.36MB | 73.49ms | 4.58ms |
| pgavlin | 43.58MB | 183.45MB | 178.10ms | 4.24ms |
| gnames | 86.71MB | 122.45MB | 146.93ms | 8.15ms |

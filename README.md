# AC 自动机 Benchmark 结果

## 简介

本项目对多个 Go 语言 Aho-Corasick（AC 自动机）开源库进行性能基准测试，对比维度包括 **建树耗时**、**建树内存申请量**、**建树产物内存占用**、**匹配耗时**。

测试词表覆盖 100 / 1,000 / 10,000 / 100,000 四种规模，语言类型涵盖纯中文、纯英文、中英混合（各 50%），词表由代码随机构造并模拟真实概率分布。

### 对比库

| 库 | Benchmark 名 | 说明 |
|---|---|---|
| [china-tjj/ahocorasick](https://github.com/china-tjj/ahocorasick) | china-tjj | 紧凑 Trie，完整命中结果，结果附带 term 索引，自动选择最小 uint 类型 |
| 同上 | china-tjj(SL) | 同上 + 后缀链接 |
| 同上 | china-tjj(U64) | 同上 + 手动指定 uint64 |
| 同上 | china-tjj(SL+U64) | 同上 + 后缀链接 + 手动指定 uint64 |
| [BobuSumisu/aho-corasick](https://github.com/BobuSumisu/aho-corasick) | BobuSumisu-ac | DFA 矩阵，完整命中结果，int 索引，构建较快 |
| [BobuSumisu/go-ahocorasick](https://github.com/BobuSumisu/go-ahocorasick) | BobuSumisu-go-ac | 双数组 Trie，完整命中结果，作者旧版实现 |
| [anknown/ahocorasick](https://github.com/anknown/ahocorasick) | anknown | 双数组 Trie，完整命中结果，int 索引 |
| [TheFutureIsOurs/ahocorasick](https://github.com/TheFutureIsOurs/ahocorasick) | TheFutureIsOurs | 双数组 Trie，不完整命中结果，同终点仅保留最长 term |
| [orbit-w/aho_corasick](https://github.com/orbit-w/aho_corasick) | orbit-w | 双数组 Trie，完整命中结果，保留全部后缀命中 |
| [sepetrov/ahocorasick](https://github.com/sepetrov/ahocorasick) | sepetrov | 标准 Trie，完整命中结果，map 存储子节点 |
| [cloudflare/ahocorasick](https://github.com/cloudflare/ahocorasick) | cloudflare | 标准 Trie，完整命中结果，byte 级匹配，int 索引 |
| [petar-dambovaliev/aho-corasick](https://github.com/petar-dambovaliev/aho-corasick) | petar-dambovaliev | NFA，完整命中结果，移植自 Rust aho-corasick |
| [iohub/ahocorasick](https://github.com/iohub/ahocorasick) | iohub | cedar 双数组，完整命中结果，byte 级匹配 |
| [ClarkThan/ahocorasick](https://github.com/ClarkThan/ahocorasick) | ClarkThan | 标准 Trie，完整命中结果，map[rune]*Node |
| [pgavlin/aho-corasick](https://github.com/pgavlin/aho-corasick) | pgavlin | NFA/DFA，完整命中结果，源自 petar-dambovaliev |
| [gnames/aho_corasick](https://github.com/gnames/aho_corasick) | gnames | 标准 Trie，完整命中结果，byte 级匹配，含后缀链接 |

## 图表总览

### 建树耗时

![建树耗时](bench_build_time.png)

### 建树内存申请量

![建树内存申请量](bench_build_alloc.png)

### 建树产物占用

![建树产物占用](bench_build_retained.png)

### 匹配耗时

![匹配耗时](bench_match_time.png)

---

## 详细数据

### 建树耗时

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 15.9µs | 175.1µs | 1.71ms | 21.82ms |
| china-tjj(SL) | 16.1µs | 175.9µs | 1.75ms | 22.02ms |
| china-tjj(U64) | 17.6µs | 184.0µs | 1.94ms | 23.71ms |
| china-tjj(SL+U64) | 17.5µs | 186.2µs | 1.97ms | 24.27ms |
| BobuSumisu-ac | 216.4µs | 1.67ms | 13.45ms | 333.77ms |
| BobuSumisu-go-ac | 366.8µs | 10.93ms | 714.69ms | 43.704s |
| anknown | 221.7µs | 627.8µs | 5.65ms | 60.83ms |
| TheFutureIsOurs | 498.7µs | 738.2µs | 3.45ms | 82.37ms |
| orbit-w | 115.1µs | 835.6µs | 63.99ms | 1.314s |
| sepetrov | 31.4µs | 330.4µs | 3.42ms | 42.87ms |
| cloudflare | 578.5µs | 5.11ms | 56.12ms | 909.22ms |
| petar-dambovaliev | 78.3µs | 841.0µs | 9.77ms | 236.61ms |
| iohub | 54.1µs | 529.0µs | 4.93ms | 67.24ms |
| ClarkThan | 27.1µs | 299.8µs | 3.05ms | 43.59ms |
| pgavlin | 77.4µs | 808.0µs | 9.57ms | 241.91ms |
| gnames | 114.1µs | 1.12ms | 11.99ms | 153.63ms |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 22.0µs | 213.8µs | 3.19ms | 38.99ms |
| china-tjj(SL) | 22.4µs | 222.3µs | 3.27ms | 41.10ms |
| china-tjj(U64) | 23.9µs | 229.9µs | 3.67ms | 42.55ms |
| china-tjj(SL+U64) | 24.5µs | 234.1µs | 3.79ms | 43.81ms |
| BobuSumisu-ac | 170.7µs | 1.26ms | 9.28ms | 173.14ms |
| BobuSumisu-go-ac | 253.5µs | 5.64ms | 253.59ms | 15.670s |
| anknown | 90.2µs | 800.8µs | 10.07ms | 150.31ms |
| TheFutureIsOurs | 46.1µs | 412.6µs | 5.88ms | 72.76ms |
| orbit-w | 35.8µs | 367.5µs | 5.79ms | 141.89ms |
| sepetrov | 70.2µs | 631.7µs | 6.90ms | 88.40ms |
| cloudflare | 473.7µs | 4.28ms | 46.38ms | 555.75ms |
| petar-dambovaliev | 74.8µs | 632.6µs | 7.39ms | 148.75ms |
| iohub | 43.8µs | 407.1µs | 4.04ms | 42.13ms |
| ClarkThan | 56.6µs | 536.4µs | 5.20ms | 85.66ms |
| pgavlin | 71.5µs | 624.3µs | 7.23ms | 144.47ms |
| gnames | 97.5µs | 987.5µs | 10.27ms | 131.75ms |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 20.1µs | 209.0µs | 2.49ms | 31.06ms |
| china-tjj(SL) | 20.6µs | 221.4µs | 2.65ms | 33.70ms |
| china-tjj(U64) | 21.9µs | 220.7µs | 2.82ms | 33.74ms |
| china-tjj(SL+U64) | 22.4µs | 223.6µs | 2.98ms | 37.67ms |
| BobuSumisu-ac | 205.8µs | 1.82ms | 11.64ms | 195.61ms |
| BobuSumisu-go-ac | 337.6µs | 8.96ms | 487.57ms | 32.062s |
| anknown | 199.8µs | 883.3µs | 17.09ms | 157.34ms |
| TheFutureIsOurs | 427.1µs | 751.4µs | 4.82ms | 58.96ms |
| orbit-w | 125.4µs | 617.0µs | 24.82ms | 608.66ms |
| sepetrov | 51.4µs | 567.3µs | 5.68ms | 68.02ms |
| cloudflare | 554.3µs | 5.29ms | 53.19ms | 741.92ms |
| petar-dambovaliev | 85.3µs | 771.1µs | 8.06ms | 186.62ms |
| iohub | 51.3µs | 496.4µs | 4.49ms | 51.80ms |
| ClarkThan | 45.5µs | 452.1µs | 4.28ms | 61.25ms |
| pgavlin | 84.5µs | 776.5µs | 7.85ms | 187.70ms |
| gnames | 109.5µs | 1.10ms | 11.79ms | 152.40ms |

### 建树内存申请量

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 10.1KB | 93.4KB | 872.4KB | 12.06MB |
| china-tjj(SL) | 10.6KB | 98.6KB | 920.3KB | 12.76MB |
| china-tjj(U64) | 29.4KB | 276.1KB | 2.50MB | 22.09MB |
| china-tjj(SL+U64) | 31.4KB | 296.1KB | 2.68MB | 23.47MB |
| BobuSumisu-ac | 1.50MB | 13.51MB | 125.22MB | 1.007GB |
| BobuSumisu-go-ac | 60.9KB | 727.3KB | 8.92MB | 73.78MB |
| anknown | 2.66MB | 3.56MB | 16.66MB | 110.84MB |
| TheFutureIsOurs | 7.57MB | 7.89MB | 11.20MB | 69.22MB |
| orbit-w | 3.60MB | 4.07MB | 9.05MB | 39.88MB |
| sepetrov | 58.8KB | 599.1KB | 5.11MB | 36.97MB |
| cloudflare | 3.26MB | 32.12MB | 320.84MB | 3.132GB |
| petar-dambovaliev | 226.7KB | 2.21MB | 22.75MB | 229.30MB |
| iohub | 125.6KB | 1.12MB | 9.65MB | 78.90MB |
| ClarkThan | 45.8KB | 437.3KB | 3.84MB | 29.39MB |
| pgavlin | 225.5KB | 2.20MB | 22.63MB | 228.12MB |
| gnames | 190.9KB | 1.71MB | 16.69MB | 138.67MB |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 15.9KB | 145.0KB | 1.27MB | 20.55MB |
| china-tjj(SL) | 16.9KB | 154.2KB | 1.34MB | 21.65MB |
| china-tjj(U64) | 47.8KB | 443.5KB | 3.80MB | 37.30MB |
| china-tjj(SL+U64) | 51.8KB | 483.5KB | 4.07MB | 39.49MB |
| BobuSumisu-ac | 1.13MB | 9.31MB | 76.54MB | 637.44MB |
| BobuSumisu-go-ac | 57.1KB | 493.9KB | 5.27MB | 46.46MB |
| anknown | 192.2KB | 1.70MB | 17.80MB | 192.22MB |
| TheFutureIsOurs | 142.8KB | 1.02MB | 10.84MB | 96.68MB |
| orbit-w | 123.1KB | 1008.0KB | 7.86MB | 67.28MB |
| sepetrov | 130.7KB | 1.00MB | 8.74MB | 68.84MB |
| cloudflare | 2.49MB | 24.09MB | 246.33MB | 2.491GB |
| petar-dambovaliev | 182.9KB | 1.43MB | 15.36MB | 133.45MB |
| iohub | 113.1KB | 1005.4KB | 7.99MB | 65.21MB |
| ClarkThan | 96.0KB | 777.2KB | 6.12MB | 49.77MB |
| pgavlin | 182.0KB | 1.42MB | 15.28MB | 132.59MB |
| gnames | 137.1KB | 1.23MB | 10.45MB | 89.14MB |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 13.5KB | 130.7KB | 1.11MB | 15.55MB |
| china-tjj(SL) | 14.3KB | 138.7KB | 1.18MB | 16.49MB |
| china-tjj(U64) | 38.7KB | 382.4KB | 3.23MB | 28.31MB |
| china-tjj(SL+U64) | 41.7KB | 410.4KB | 3.46MB | 30.18MB |
| BobuSumisu-ac | 1.37MB | 12.12MB | 104.87MB | 891.76MB |
| BobuSumisu-go-ac | 61.5KB | 704.0KB | 6.98MB | 60.00MB |
| anknown | 2.00MB | 4.15MB | 15.01MB | 144.72MB |
| TheFutureIsOurs | 5.49MB | 6.36MB | 12.06MB | 87.62MB |
| orbit-w | 3.24MB | 4.19MB | 9.82MB | 59.20MB |
| sepetrov | 95.0KB | 948.0KB | 7.52MB | 55.56MB |
| cloudflare | 2.89MB | 28.25MB | 281.57MB | 2.801GB |
| petar-dambovaliev | 252.0KB | 1.82MB | 18.89MB | 184.45MB |
| iohub | 121.4KB | 1.07MB | 8.95MB | 73.92MB |
| ClarkThan | 71.1KB | 668.6KB | 5.38MB | 40.36MB |
| pgavlin | 251.0KB | 1.81MB | 18.79MB | 183.45MB |
| gnames | 173.7KB | 1.55MB | 13.93MB | 122.45MB |

### 建树产物占用

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 3.6KB | 34.7KB | 370.5KB | 4.40MB |
| china-tjj(SL) | 4.3KB | 39.9KB | 418.5KB | 5.10MB |
| china-tjj(U64) | 11.1KB | 106.2KB | 1.04MB | 8.13MB |
| china-tjj(SL+U64) | 13.2KB | 126.3KB | 1.22MB | 9.52MB |
| BobuSumisu-ac | 1.34MB | 12.00MB | 110.61MB | 914.27MB |
| BobuSumisu-go-ac | 32.8KB | 280.1KB | 2.53MB | 19.40MB |
| anknown | 1.43MB | 1.58MB | 3.76MB | 17.24MB |
| TheFutureIsOurs | 2.10MB | 2.09MB | 2.09MB | 8.19MB |
| orbit-w | 2.57MB | 2.77MB | 3.12MB | 9.83MB |
| sepetrov | 44.3KB | 425.4KB | 3.77MB | 26.35MB |
| cloudflare | 3.23MB | 31.77MB | 317.17MB | 3.097GB |
| petar-dambovaliev | 102.0KB | 666.5KB | 5.60MB | 50.38MB |
| iohub | 52.4KB | 428.0KB | 3.33MB | 26.60MB |
| ClarkThan | 41.7KB | 398.9KB | 3.54MB | 25.26MB |
| pgavlin | 102.0KB | 661.6KB | 5.60MB | 50.38MB |
| gnames | 157.5KB | 1.37MB | 12.53MB | 100.12MB |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 6.6KB | 58.7KB | 456.2KB | 6.23MB |
| china-tjj(SL) | 7.7KB | 67.9KB | 528.2KB | 7.33MB |
| china-tjj(U64) | 20.4KB | 186.5KB | 1.34MB | 11.37MB |
| china-tjj(SL+U64) | 24.0KB | 226.5KB | 1.61MB | 13.55MB |
| BobuSumisu-ac | 1.01MB | 8.27MB | 68.02MB | 567.08MB |
| BobuSumisu-go-ac | 29.6KB | 200.1KB | 1.55MB | 12.33MB |
| anknown | 38.1KB | 287.8KB | 3.18MB | 42.24MB |
| TheFutureIsOurs | 37.3KB | 160.2KB | 1.34MB | 10.50MB |
| orbit-w | 31.2KB | 230.3KB | 1.74MB | 16.26MB |
| sepetrov | 102.1KB | 816.9KB | 6.42MB | 51.95MB |
| cloudflare | 2.46MB | 23.84MB | 243.72MB | 2.465GB |
| petar-dambovaliev | 95.9KB | 462.8KB | 3.76MB | 33.27MB |
| iohub | 52.4KB | 428.0KB | 3.33MB | 26.60MB |
| ClarkThan | 93.6KB | 748.8KB | 5.90MB | 47.83MB |
| pgavlin | 89.8KB | 462.9KB | 3.76MB | 33.27MB |
| gnames | 114.5KB | 955.9KB | 7.47MB | 60.80MB |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 5.3KB | 48.2KB | 458.5KB | 5.48MB |
| china-tjj(SL) | 5.9KB | 56.2KB | 522.5KB | 6.42MB |
| china-tjj(U64) | 15.6KB | 142.2KB | 1.30MB | 10.06MB |
| china-tjj(SL+U64) | 18.5KB | 170.2KB | 1.53MB | 11.93MB |
| BobuSumisu-ac | 1.21MB | 10.77MB | 92.91MB | 788.88MB |
| BobuSumisu-go-ac | 32.0KB | 264.1KB | 2.03MB | 15.98MB |
| anknown | 1.18MB | 1.59MB | 2.94MB | 26.16MB |
| TheFutureIsOurs | 1.65MB | 2.09MB | 2.09MB | 10.25MB |
| orbit-w | 2.20MB | 2.77MB | 3.11MB | 13.99MB |
| sepetrov | 72.4KB | 678.5KB | 5.45MB | 41.17MB |
| cloudflare | 2.85MB | 27.94MB | 278.34MB | 2.770GB |
| petar-dambovaliev | 129.6KB | 591.5KB | 4.66MB | 43.58MB |
| iohub | 52.5KB | 427.9KB | 3.33MB | 26.60MB |
| ClarkThan | 67.6KB | 626.7KB | 5.05MB | 38.35MB |
| pgavlin | 129.4KB | 591.4KB | 4.66MB | 43.58MB |
| gnames | 142.9KB | 1.22MB | 10.41MB | 86.71MB |

### 匹配耗时

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 919.1µs | 1.30ms | 909.3µs | 1.51ms |
| china-tjj(SL) | 877.4µs | 1.24ms | 853.7µs | 1.53ms |
| china-tjj(U64) | 820.5µs | 1.20ms | 990.1µs | 1.47ms |
| china-tjj(SL+U64) | 886.0µs | 1.13ms | 936.6µs | 1.46ms |
| BobuSumisu-ac | 384.3µs | 442.8µs | 679.6µs | 2.86ms |
| BobuSumisu-go-ac | 474.2µs | 524.8µs | 723.5µs | 1.35ms |
| anknown | 453.3µs | 452.6µs | 676.7µs | 964.6µs |
| TheFutureIsOurs | 195.2µs | 242.8µs | 364.6µs | 390.4µs |
| orbit-w | 166.5µs | 219.2µs | 326.8µs | 393.1µs |
| sepetrov | 547.8µs | 854.0µs | 1.24ms | 2.16ms |
| cloudflare | 280.1µs | 618.9µs | 1.07ms | 6.95ms |
| petar-dambovaliev | 1.17ms | 1.54ms | 2.18ms | 6.24ms |
| iohub | 576.6µs | 653.5µs | 962.7µs | 1.69ms |
| ClarkThan | 636.9µs | 744.7µs | 1.19ms | 2.26ms |
| pgavlin | 1.18ms | 1.55ms | 2.17ms | 4.97ms |
| gnames | 2.07ms | 2.34ms | 3.30ms | 6.36ms |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 2.18ms | 2.64ms | 3.63ms | 5.55ms |
| china-tjj(SL) | 1.93ms | 2.27ms | 3.21ms | 4.92ms |
| china-tjj(U64) | 1.91ms | 2.31ms | 3.39ms | 5.25ms |
| china-tjj(SL+U64) | 1.72ms | 2.05ms | 3.22ms | 5.10ms |
| BobuSumisu-ac | 405.8µs | 699.1µs | 1.57ms | 4.49ms |
| BobuSumisu-go-ac | 531.6µs | 657.0µs | 1.49ms | 2.99ms |
| anknown | 1.67ms | 1.35ms | 2.38ms | 6.07ms |
| TheFutureIsOurs | 756.8µs | 779.0µs | 1.40ms | 2.24ms |
| orbit-w | 720.1µs | 776.4µs | 1.43ms | 2.39ms |
| sepetrov | 2.02ms | 2.71ms | 5.24ms | 12.13ms |
| cloudflare | 324.9µs | 644.4µs | 1.25ms | 4.24ms |
| petar-dambovaliev | 1.45ms | 2.04ms | 4.11ms | 5.75ms |
| iohub | 783.3µs | 1.10ms | 2.50ms | 5.82ms |
| ClarkThan | 1.91ms | 2.47ms | 4.27ms | 9.20ms |
| pgavlin | 1.44ms | 2.05ms | 3.98ms | 5.60ms |
| gnames | 2.28ms | 3.03ms | 5.88ms | 15.35ms |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 1.34ms | 1.84ms | 1.49ms | 2.19ms |
| china-tjj(SL) | 1.29ms | 1.75ms | 1.36ms | 2.41ms |
| china-tjj(U64) | 1.16ms | 1.65ms | 1.44ms | 2.33ms |
| china-tjj(SL+U64) | 1.08ms | 1.51ms | 1.35ms | 2.21ms |
| BobuSumisu-ac | 404.0µs | 597.5µs | 816.7µs | 1.80ms |
| BobuSumisu-go-ac | 554.9µs | 618.9µs | 862.2µs | 1.39ms |
| anknown | 757.9µs | 856.8µs | 1.25ms | 2.06ms |
| TheFutureIsOurs | 402.4µs | 489.1µs | 644.7µs | 910.7µs |
| orbit-w | 331.0µs | 462.8µs | 607.1µs | 1.11ms |
| sepetrov | 908.0µs | 1.31ms | 2.18ms | 4.75ms |
| cloudflare | 311.0µs | 738.3µs | 1.11ms | 3.61ms |
| petar-dambovaliev | 1.37ms | 1.93ms | 2.62ms | 4.62ms |
| iohub | 612.4µs | 844.7µs | 1.26ms | 2.27ms |
| ClarkThan | 1.15ms | 1.58ms | 2.33ms | 3.69ms |
| pgavlin | 1.36ms | 1.88ms | 2.54ms | 4.09ms |
| gnames | 2.31ms | 2.78ms | 3.82ms | 8.26ms |

# AC 自动机 Benchmark 结果

## 简介

本项目对多个 Go 语言 Aho-Corasick（AC 自动机）开源库进行性能基准测试，对比维度包括 **建树耗时**、**建树内存申请量**、**建树产物内存占用**、**匹配耗时**。

测试词表覆盖 100 / 1,000 / 10,000 / 100,000 四种规模，语言类型涵盖纯中文、纯英文、中英混合（各 50%），词表由代码随机构造并模拟真实概率分布。

### 对比库

| 库 | Benchmark 名 | 说明 |
|---|---|---|
| [china-tjj/acautomaton](https://github.com/china-tjj/acautomaton) | china-tjj | 紧凑 Trie，三级索引（线性/二分/哈希），自动选择最小 uint 类型 |
| 同上 | china-tjj(SL) | 同上 + 构建后缀链接（加速匹配，额外 O(N) 空间） |
| 同上 | china-tjj(U64) | 同上，手动指定 uint64 索引（与其他库同一维度对比） |
| 同上 | china-tjj(SL+U64) | 后缀链接 + uint64 索引 |
| [BobuSumisu/aho-corasick](https://github.com/BobuSumisu/aho-corasick) | BobuSumisu-ac | DFA 矩阵实现，构建快，int 索引 |
| [BobuSumisu/go-ahocorasick](https://github.com/BobuSumisu/go-ahocorasick) | BobuSumisu-go-ac | 双数组 Trie，作者旧版实现 |
| [anknown/ahocorasick](https://github.com/anknown/ahocorasick) | anknown | 双数组 Trie，int 索引，内存占用低 |
| [sepetrov/ahocorasick](https://github.com/sepetrov/ahocorasick) | sepetrov | 标准 Trie，map 存储子节点 |
| [cloudflare/ahocorasick](https://github.com/cloudflare/ahocorasick) | cloudflare | 标准 Trie，[]byte 匹配，int 索引 |
| [petar-dambovaliev/aho-corasick](https://github.com/petar-dambovaliev/aho-corasick) | petar-dambovaliev | 移植自 Rust BurntSushi 库，NFA 模式 |
| [iohub/ahocorasick](https://github.com/iohub/ahocorasick) | iohub | cedar 双数组实现 |
| [ClarkThan/ahocorasick](https://github.com/ClarkThan/ahocorasick) | ClarkThan | 标准 Trie，map[rune]*Node |
| [pgavlin/aho-corasick](https://github.com/pgavlin/aho-corasick) | pgavlin | 源自 petar-dambovaliev，支持 NFA/DFA 切换 |
| [gnames/aho_corasick](https://github.com/gnames/aho_corasick) | gnames | 标准 Trie，字节级匹配，含后缀链接 |

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
| china-tjj | 16.9µs | 187.6µs | 1.84ms | 24.16ms |
| china-tjj(SL) | 17.3µs | 188.8µs | 1.87ms | 24.28ms |
| china-tjj(U64) | 21.0µs | 198.5µs | 2.06ms | 26.25ms |
| china-tjj(SL+U64) | 18.7µs | 201.6µs | 2.06ms | 26.29ms |
| BobuSumisu-ac | 233.4µs | 1.92ms | 15.55ms | 345.73ms |
| BobuSumisu-go-ac | 385.5µs | 11.21ms | 745.83ms | 45.354s |
| anknown | 221.7µs | 649.2µs | 5.90ms | 67.21ms |
| sepetrov | 33.0µs | 336.9µs | 3.54ms | 43.78ms |
| cloudflare | 608.8µs | 5.73ms | 74.44ms | 1.190s |
| petar-dambovaliev | 96.9µs | 874.9µs | 11.95ms | 229.20ms |
| iohub | 56.8µs | 543.6µs | 5.39ms | 69.32ms |
| ClarkThan | 28.3µs | 298.6µs | 3.11ms | 41.78ms |
| pgavlin | 82.3µs | 856.4µs | 10.29ms | 227.77ms |
| gnames | 123.5µs | 1.17ms | 12.79ms | 164.68ms |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 23.9µs | 243.3µs | 3.43ms | 52.43ms |
| china-tjj(SL) | 24.2µs | 245.6µs | 3.53ms | 47.64ms |
| china-tjj(U64) | 26.0µs | 252.1µs | 3.96ms | 49.13ms |
| china-tjj(SL+U64) | 26.4µs | 261.0µs | 4.16ms | 52.21ms |
| BobuSumisu-ac | 168.4µs | 1.27ms | 9.59ms | 203.38ms |
| BobuSumisu-go-ac | 264.6µs | 5.87ms | 264.77ms | 16.492s |
| anknown | 92.7µs | 897.7µs | 11.40ms | 164.35ms |
| sepetrov | 76.6µs | 680.3µs | 7.14ms | 101.38ms |
| cloudflare | 506.9µs | 4.32ms | 53.12ms | 845.48ms |
| petar-dambovaliev | 74.9µs | 671.1µs | 7.89ms | 173.26ms |
| iohub | 46.6µs | 469.5µs | 4.44ms | 58.30ms |
| ClarkThan | 59.7µs | 570.9µs | 5.90ms | 98.00ms |
| pgavlin | 73.7µs | 661.4µs | 7.84ms | 159.93ms |
| gnames | 104.4µs | 1.03ms | 17.01ms | 174.70ms |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 21.7µs | 233.2µs | 2.73ms | 33.89ms |
| china-tjj(SL) | 21.9µs | 235.5µs | 2.79ms | 35.78ms |
| china-tjj(U64) | 22.8µs | 244.4µs | 3.04ms | 36.81ms |
| china-tjj(SL+U64) | 23.4µs | 249.9µs | 3.48ms | 42.07ms |
| BobuSumisu-ac | 201.9µs | 1.77ms | 12.74ms | 267.19ms |
| BobuSumisu-go-ac | 347.9µs | 9.37ms | 511.59ms | 33.478s |
| anknown | 212.8µs | 944.2µs | 20.74ms | 162.95ms |
| sepetrov | 54.0µs | 589.6µs | 5.74ms | 76.19ms |
| cloudflare | 573.4µs | 5.15ms | 66.21ms | 1.012s |
| petar-dambovaliev | 88.4µs | 789.1µs | 8.74ms | 204.62ms |
| iohub | 53.8µs | 519.8µs | 5.01ms | 62.04ms |
| ClarkThan | 44.0µs | 472.2µs | 4.63ms | 68.29ms |
| pgavlin | 87.2µs | 776.5µs | 10.45ms | 202.21ms |
| gnames | 114.9µs | 1.16ms | 12.29ms | 169.97ms |

### 建树内存申请量

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 11.5KB | 105.4KB | 992.3KB | 14.34MB |
| china-tjj(SL) | 12.0KB | 110.6KB | 1.02MB | 15.03MB |
| china-tjj(U64) | 34.1KB | 324.1KB | 2.96MB | 26.63MB |
| china-tjj(SL+U64) | 36.1KB | 344.1KB | 3.14MB | 28.02MB |
| BobuSumisu-ac | 1.50MB | 13.51MB | 125.22MB | 1.007GB |
| BobuSumisu-go-ac | 60.9KB | 727.3KB | 8.92MB | 73.78MB |
| anknown | 2.66MB | 3.56MB | 16.66MB | 110.84MB |
| sepetrov | 58.8KB | 599.1KB | 5.11MB | 36.97MB |
| cloudflare | 3.26MB | 32.12MB | 320.84MB | 3.132GB |
| petar-dambovaliev | 226.7KB | 2.21MB | 22.75MB | 229.36MB |
| iohub | 125.6KB | 1.12MB | 9.65MB | 78.90MB |
| ClarkThan | 45.8KB | 437.3KB | 3.84MB | 29.39MB |
| pgavlin | 225.5KB | 2.20MB | 22.63MB | 228.28MB |
| gnames | 190.9KB | 1.71MB | 16.69MB | 138.67MB |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 19.4KB | 181.0KB | 1.58MB | 27.05MB |
| china-tjj(SL) | 20.4KB | 190.2KB | 1.65MB | 28.15MB |
| china-tjj(U64) | 62.1KB | 571.5KB | 5.05MB | 50.30MB |
| china-tjj(SL+U64) | 66.1KB | 611.5KB | 5.32MB | 52.48MB |
| BobuSumisu-ac | 1.13MB | 9.31MB | 76.54MB | 637.44MB |
| BobuSumisu-go-ac | 57.1KB | 493.9KB | 5.27MB | 46.46MB |
| anknown | 192.2KB | 1.70MB | 17.80MB | 192.22MB |
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
| china-tjj | 15.8KB | 153.3KB | 1.32MB | 19.81MB |
| china-tjj(SL) | 16.5KB | 161.3KB | 1.39MB | 20.75MB |
| china-tjj(U64) | 47.0KB | 470.4KB | 4.06MB | 36.82MB |
| china-tjj(SL+U64) | 50.0KB | 498.4KB | 4.29MB | 38.69MB |
| BobuSumisu-ac | 1.37MB | 12.12MB | 104.87MB | 891.76MB |
| BobuSumisu-go-ac | 61.5KB | 704.0KB | 6.98MB | 60.00MB |
| anknown | 2.00MB | 4.15MB | 15.01MB | 144.72MB |
| sepetrov | 95.0KB | 948.0KB | 7.52MB | 55.58MB |
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
| china-tjj | 3.8KB | 34.7KB | 370.5KB | 4.40MB |
| china-tjj(SL) | 4.1KB | 39.9KB | 418.6KB | 5.10MB |
| china-tjj(U64) | 11.1KB | 106.3KB | 1.04MB | 8.13MB |
| china-tjj(SL+U64) | 13.1KB | 126.5KB | 1.22MB | 9.52MB |
| BobuSumisu-ac | 1.34MB | 12.00MB | 110.61MB | 914.27MB |
| BobuSumisu-go-ac | 32.8KB | 280.1KB | 2.53MB | 19.40MB |
| anknown | 1.42MB | 1.58MB | 3.76MB | 17.24MB |
| sepetrov | 44.3KB | 425.8KB | 3.77MB | 26.35MB |
| cloudflare | 3.23MB | 31.77MB | 317.17MB | 3.097GB |
| petar-dambovaliev | 96.5KB | 667.1KB | 5.60MB | 50.38MB |
| iohub | 52.6KB | 428.1KB | 3.33MB | 26.60MB |
| ClarkThan | 41.5KB | 398.9KB | 3.54MB | 25.26MB |
| pgavlin | 102.9KB | 661.6KB | 5.60MB | 50.38MB |
| gnames | 157.5KB | 1.37MB | 12.53MB | 100.12MB |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 6.7KB | 58.9KB | 456.2KB | 6.23MB |
| china-tjj(SL) | 7.6KB | 68.0KB | 528.2KB | 7.33MB |
| china-tjj(U64) | 20.1KB | 186.3KB | 1.34MB | 11.37MB |
| china-tjj(SL+U64) | 24.1KB | 226.2KB | 1.61MB | 13.55MB |
| BobuSumisu-ac | 1.01MB | 8.27MB | 68.02MB | 567.08MB |
| BobuSumisu-go-ac | 29.5KB | 200.1KB | 1.55MB | 12.33MB |
| anknown | 38.3KB | 293.6KB | 3.18MB | 42.24MB |
| sepetrov | 102.0KB | 816.5KB | 6.42MB | 51.95MB |
| cloudflare | 2.45MB | 23.83MB | 243.72MB | 2.465GB |
| petar-dambovaliev | 95.8KB | 462.9KB | 3.76MB | 33.27MB |
| iohub | 52.4KB | 428.3KB | 3.33MB | 26.60MB |
| ClarkThan | 93.0KB | 748.8KB | 5.90MB | 47.83MB |
| pgavlin | 95.8KB | 462.7KB | 3.76MB | 33.27MB |
| gnames | 114.3KB | 955.7KB | 7.47MB | 60.81MB |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 5.4KB | 48.3KB | 458.5KB | 5.48MB |
| china-tjj(SL) | 5.8KB | 56.2KB | 522.5KB | 6.42MB |
| china-tjj(U64) | 15.5KB | 142.3KB | 1.30MB | 10.06MB |
| china-tjj(SL+U64) | 18.7KB | 170.4KB | 1.53MB | 11.93MB |
| BobuSumisu-ac | 1.22MB | 10.77MB | 92.91MB | 788.88MB |
| BobuSumisu-go-ac | 32.1KB | 264.1KB | 2.03MB | 15.98MB |
| anknown | 1.18MB | 1.59MB | 2.94MB | 26.16MB |
| sepetrov | 72.7KB | 678.8KB | 5.45MB | 41.17MB |
| cloudflare | 2.85MB | 27.94MB | 278.34MB | 2.770GB |
| petar-dambovaliev | 129.7KB | 591.6KB | 4.66MB | 43.58MB |
| iohub | 46.8KB | 428.1KB | 3.32MB | 26.60MB |
| ClarkThan | 67.2KB | 627.2KB | 5.05MB | 38.35MB |
| pgavlin | 129.8KB | 591.4KB | 4.66MB | 43.58MB |
| gnames | 142.8KB | 1.22MB | 10.41MB | 86.71MB |

### 匹配耗时

#### 纯中文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 1.09ms | 1.41ms | 994.3µs | 1.59ms |
| china-tjj(SL) | 942.7µs | 1.36ms | 939.2µs | 1.56ms |
| china-tjj(U64) | 1.06ms | 1.29ms | 1.08ms | 1.86ms |
| china-tjj(SL+U64) | 892.9µs | 1.25ms | 1.02ms | 1.69ms |
| BobuSumisu-ac | 411.4µs | 492.0µs | 812.8µs | 3.54ms |
| BobuSumisu-go-ac | 509.9µs | 560.6µs | 820.8µs | 1.49ms |
| anknown | 464.5µs | 468.6µs | 667.9µs | 1.05ms |
| sepetrov | 561.5µs | 854.0µs | 1.34ms | 2.36ms |
| cloudflare | 309.4µs | 662.7µs | 1.59ms | 7.48ms |
| petar-dambovaliev | 1.23ms | 1.66ms | 2.44ms | 8.60ms |
| iohub | 570.4µs | 648.3µs | 1.00ms | 1.79ms |
| ClarkThan | 637.0µs | 941.6µs | 1.30ms | 2.23ms |
| pgavlin | 1.22ms | 1.60ms | 2.65ms | 8.54ms |
| gnames | 2.15ms | 2.51ms | 3.57ms | 11.17ms |

#### 纯英文

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 2.36ms | 2.92ms | 4.02ms | 6.41ms |
| china-tjj(SL) | 2.03ms | 2.47ms | 3.60ms | 5.95ms |
| china-tjj(U64) | 2.22ms | 2.75ms | 4.02ms | 6.95ms |
| china-tjj(SL+U64) | 1.87ms | 2.31ms | 3.62ms | 6.82ms |
| BobuSumisu-ac | 491.1µs | 792.1µs | 1.87ms | 6.13ms |
| BobuSumisu-go-ac | 621.3µs | 727.5µs | 1.62ms | 3.61ms |
| anknown | 1.51ms | 1.36ms | 2.43ms | 8.37ms |
| sepetrov | 2.15ms | 3.02ms | 5.42ms | 15.09ms |
| cloudflare | 424.3µs | 806.2µs | 1.76ms | 7.93ms |
| petar-dambovaliev | 1.51ms | 2.23ms | 4.45ms | 7.32ms |
| iohub | 785.8µs | 1.10ms | 2.58ms | 7.11ms |
| ClarkThan | 2.03ms | 2.77ms | 4.55ms | 11.98ms |
| pgavlin | 1.52ms | 2.20ms | 4.47ms | 6.18ms |
| gnames | 2.36ms | 3.15ms | 6.32ms | 18.81ms |

#### 中英混合

| Library | 100 | 1,000 | 10,000 | 100,000 |
|---|---|---|---|---|
| china-tjj | 1.47ms | 2.02ms | 1.66ms | 2.65ms |
| china-tjj(SL) | 1.44ms | 1.80ms | 1.50ms | 2.51ms |
| china-tjj(U64) | 1.34ms | 1.80ms | 1.72ms | 2.91ms |
| china-tjj(SL+U64) | 1.25ms | 1.66ms | 1.52ms | 2.85ms |
| BobuSumisu-ac | 485.6µs | 593.8µs | 1.01ms | 2.88ms |
| BobuSumisu-go-ac | 587.3µs | 670.4µs | 952.8µs | 1.82ms |
| anknown | 887.0µs | 881.5µs | 1.34ms | 2.41ms |
| sepetrov | 954.9µs | 1.39ms | 2.37ms | 5.81ms |
| cloudflare | 391.7µs | 872.2µs | 1.85ms | 6.78ms |
| petar-dambovaliev | 1.43ms | 1.96ms | 3.01ms | 5.88ms |
| iohub | 621.5µs | 807.9µs | 1.32ms | 3.07ms |
| ClarkThan | 1.27ms | 1.65ms | 2.39ms | 5.80ms |
| pgavlin | 1.40ms | 2.00ms | 2.88ms | 6.55ms |
| gnames | 2.62ms | 2.91ms | 4.27ms | 10.32ms |

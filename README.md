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

对比库覆盖 GitHub 搜索 [`ahocorasick language:Go`](https://github.com/search?q=ahocorasick+language%3AGo&type=repositories)（共 39 个仓库）中全部 28 个可本地基准测试的库，另补充 5 个搜索外知名库，合计 33 个库、38 个 Benchmark 目标；未收录的 11 个仓库及原因见文末「未收录仓库说明」。

| 库 | Benchmark 名 | 实现算法 | 索引粒度 | 完整匹配结果 | 后缀链接 | 其它 |
|---|---|---|---|---|---|---|
| [china-tjj/ahocorasick](https://github.com/china-tjj/ahocorasick) | china-tjj | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型 |
| 同上 | china-tjj(FB) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型，启用快速构建模式 |
| 同上 | china-tjj(U64) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型 |
| 同上 | china-tjj(U64+OL) | 紧凑Trie | auto | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接 |
| 同上 | china-tjj(U64+TI) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型，返回结果含pattern id |
| 同上 | china-tjj(U64+OL+TI) | 紧凑Trie | auto | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接，返回结果含pattern id |
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
| [gansidui/ahocorasick](https://github.com/gansidui/ahocorasick) | gansidui | 标准Trie(map) | rune | 完整 | 无 | 匹配时沿fail链收集；许多其它Go实现参考的基础版本 |
| [coregx/ahocorasick](https://github.com/coregx/ahocorasick) | coregx | DFA(扁平转移表) | byte | 完整 | 有 | 活跃维护；Byte Classes压缩字母表+预过滤；要求go>=1.25.4 |
| [rrethy/ahocorasick](https://github.com/RRethy/ahocorasick) | RRethy | 双数组Trie(DAT) | byte | 完整 | 无 | 构建时合并fail节点output；支持[]byte和string输入 |
| [hkspirt/ahocorasick](https://github.com/hkspirt/ahocorasick) | hkspirt | 标准Trie(map) | rune | 完整 | 无 | 基于gansidui，增加敏感词贪婪替换(Replace)功能 |
| [arkadijs/ahocorasick-go](https://github.com/arkadijs/ahocorasick-go) | arkadijs | 混合Trie(浅层数组+深层map) | byte | 完整 | 无 | 构建时合并fail输出；支持context取消搜索 |
| [yanlinLiu0424/ahocorasick](https://github.com/yanlinLiu0424/ahocorasick) | yanlinLiu0424 | DFA(扁平int32状态表) | byte | 完整 | 有 | Ken Steele算法变体，字母表压缩；支持忽略大小写标记 |
| [pombredanne/ahocorasick](https://github.com/pombredanne/ahocorasick) | pombredanne | 数组Trie(排序切片+二分) | byte | 完整 | 有 | 显式dict后缀链接；channel流式输出，提供io.Reader接口；2013年老库 |
| [ofw/ahocorasick](https://github.com/ofw/ahocorasick) | ofw | 数组Trie([256]指针) | byte | 不完整 | 无 | 相同pattern去重仅报首次命中；适合ASCII/字节流 |
| [Icarus0xff/ahocorasick](https://github.com/Icarus0xff/ahocorasick) | Icarus0xff | 标准Trie(map) | rune | 完整 | 无 | 构建时合并fail输出；支持动态增删，RWMutex并发安全 |
| [mangotree2/ahocorasick](https://github.com/mangotree2/ahocorasick) | mangotree2 | 双数组Trie(DAT) | rune | 语义不同 | 无 | 敏感词过滤/替换引擎，Handle执行过滤替换而非返回匹配列表 |
| [smotes/ahocorasick](https://github.com/smotes/ahocorasick) | smotes | DFA(泛型) | byte/rune | 完整 | 有 | 显式DictLink；Go 1.23+迭代器API，多种匹配语义可配 |
| [Codehardt/go-ahocorasick](https://github.com/Codehardt/go-ahocorasick) | Codehardt | 标准Trie(map) | byte | 完整 | 有 | 教科书式实现，维护专用outputLink |
| [DaemonMonch/ac](https://github.com/DaemonMonch/ac) | DaemonMonch | 标准Trie(map) | rune | 完整 | 无 | 构建时合并fail链emits；延迟初始化失配指针 |
| [chowyu12/ahocorasick](https://github.com/chowyu12/ahocorasick) | chowyu12 | 标准Trie(map) | rune | 完整 | 无 | 支持编译后动态增量添加模式串，并发读写保护 |
| [codefever/ahocorasick](https://github.com/codefever/ahocorasick) | codefever | 双数组Trie(DAT) | byte | 完整 | 有 | 显式suffixLink数组；支持每个pattern映射自定义value |
| [kiry163/ahocorasick](https://github.com/kiry163/ahocorasick) | kiry163 | DFA/NFA(按规模自动选择) | byte | 完整 | 有 | Rust aho-corasick的Go移植，含prefilter等优化 |
| [Leon180/AhoCorasick](https://github.com/Leon180/AhoCorasick) | Leon180 | 标准Trie(map) | rune | 完整 | 无 | 支持后台异步重构，适合词库频繁变动场景 |
| [jsphLim/Base_AhoCorasick](https://github.com/jsphLim/Base_AhoCorasick) | jsphLim | 标准Trie(map) | rune | 不完整 | 无 | 原型实现，未合并fail输出，位置计算有缺陷 |
| [raaaaaaaay86/ahocorasick](https://github.com/Raaaaaaaay86/ahocorasick) | Raaaaaaaay86 | 标准Trie(map) | rune | 完整 | 无 | 构建时递归合并fail输出；提供仅最长匹配的过滤选项 |
| [kirklin/go-swd](https://github.com/kirklin/go-swd) | go-swd | 混合Trie(根部dense+深层排序边) | rune | 完整 | 有 | 敏感词检测库，支持Gap匹配/重复折叠/2-gram预过滤；benchmark已关闭默认词库；字母表上限16383个不同字符(超出的大词表中文用例跳过) |

### 未收录仓库说明

GitHub 搜索 `ahocorasick language:Go` 共 39 个仓库，以下 11 个未纳入 Benchmark：

| 仓库 | 未收录原因 |
|---|---|
| [heidawei/AhoCorasickDoubleArrayTrie](https://github.com/heidawei/AhoCorasickDoubleArrayTrie) | 库自身 bug：移植 Java 版时用 Go map 替代原版有序 Map，兄弟节点顺序随机导致 DAT size 少算，fail/output 表长度不足，构建期随机 panic（还可能静默截断数据） |
| [go-ego/cedar](https://github.com/go-ego/cedar) | 双数组前缀树（Insert/PrefixMatch），aho 子目录为空包，不是完整 AC 自动机 |
| [tmikus/ahocorasick_rs](https://github.com/tmikus/ahocorasick_rs) | Rust 库 BurntSushi/aho-corasick 的 CGO 封装，匹配引擎非 Go 实现 |
| [Hoshinonyaruko/Sanae_Filter](https://github.com/Hoshinonyaruko/Sanae_Filter) | 敏感词过滤 HTTP 服务（main 程序），非可 import 的库，无 go.mod |
| [skyoo2003/acor](https://github.com/skyoo2003/acor) | 词典存储在 Redis/Valkey，依赖外部服务，非纯内存本地库 |
| [theflavoroflife/ahocorasick](https://github.com/theflavoroflife/ahocorasick) | go.mod 声明 `module ahocorasick` 与仓库路径不匹配，无法 go get |
| [yjb2807/ahocorasick](https://github.com/yjb2807/ahocorasick) | anknown/ahocorasick 的镜像拷贝（anknown 已收录） |
| [duggytuxy/ahocorasick](https://github.com/duggytuxy/ahocorasick) | coregx/ahocorasick 的复制重发（coregx 已收录），且要求 go>=1.26.5 |
| [yflau/ahocorasick](https://github.com/yflau/ahocorasick) | 2012 年 Google Code 官方仓库的导出镜像，GOPATH 时代代码，无 go.mod |
| [jsphLim/Aho_Filter](https://github.com/jsphLim/Aho_Filter) | 使用相对路径 import（`./ac`）的 main 程序，不支持 module 模式 |
| [dcto/go-sieve](https://github.com/dcto/go-sieve) | 匹配核心复用 anknown（已收录），自身是带 SQLite 依赖的应用层封装 |

**注**：个别库对数据有限制（如 go-swd 字母表上限 16383 个不同字符），不支持的用例会在 Benchmark 中跳过（日志输出 SKIP），对应单元格显示 N/A。

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
| china-tjj | 2.7KB | 3.2KB | 14.2µs | 939.0µs |
| china-tjj(FB) | 2.7KB | 8.4KB | 14.4µs | 931.0µs |
| china-tjj(U64) | 7.2KB | 9.0KB | 14.4µs | 818.7µs |
| china-tjj(U64+OL) | 9.2KB | 11.0KB | 14.5µs | 812.7µs |
| china-tjj(U64+TI) | 9.0KB | 10.8KB | 14.7µs | 834.3µs |
| china-tjj(U64+OL+TI) | 11.0KB | 12.8KB | 14.9µs | 792.2µs |
| BobuSumisu-ac | 1.33MB | 1.50MB | 163.9µs | 370.1µs |
| BobuSumisu-go-ac | 32.8KB | 60.9KB | 368.2µs | 470.6µs |
| anknown | 1.42MB | 2.66MB | 168.2µs | 418.6µs |
| TheFutureIsOurs | 2.09MB | 7.57MB | 398.6µs | 183.5µs |
| orbit-w | 2.57MB | 3.60MB | 176.0µs | 156.2µs |
| sepetrov | 44.0KB | 58.8KB | 28.7µs | 529.3µs |
| cloudflare | 3.22MB | 3.26MB | 584.5µs | 302.9µs |
| petar-dambovaliev | 102.0KB | 226.7KB | 71.3µs | 1.15ms |
| iohub | 52.4KB | 124.9KB | 49.2µs | 535.9µs |
| ClarkThan | 41.3KB | 45.8KB | 25.6µs | 622.6µs |
| pgavlin | 102.0KB | 225.5KB | 73.4µs | 1.14ms |
| gnames | 157.2KB | 190.9KB | 110.1µs | 1.94ms |
| gansidui | 43.2KB | 57.3KB | 30.0µs | 723.4µs |
| coregx | 345.7KB | 686.5KB | 218.8µs | 188.5µs |
| RRethy | 97.7KB | 110.0KB | 32.8µs | 371.8µs |
| hkspirt | 47.2KB | 61.2KB | 30.3µs | 621.3µs |
| arkadijs | 358.2KB | 358.2KB | 83.6µs | 1.48ms |
| yanlinLiu0424 | 218.4KB | 396.5KB | 1.99ms | 252.0µs |
| pombredanne | 58.5KB | 128.0KB | 132.1µs | 2.19ms |
| ofw | 1.47MB | 1.50MB | 255.2µs | 339.4µs |
| Icarus0xff | 48.8KB | 62.8KB | 32.7µs | 781.9µs |
| mangotree2 | 1.84MB | 3.10MB | 201.5µs | 362.7µs |
| smotes | 52.7KB | 60.5KB | 32.0µs | 576.5µs |
| Codehardt | 156.5KB | 162.9KB | 113.3µs | 2.57ms |
| DaemonMonch | 52.7KB | 54.9KB | 19.5µs | 540.9µs |
| chowyu12 | 49.8KB | 3.7KB | 587ns | 684.0µs |
| codefever | 44.4KB | 290.4KB | 88.0µs | 687.4µs |
| kiry163 | 809.5KB | 3.28MB | 2.41ms | 212.63ms |
| Leon180 | 51.0KB | 57.4KB | 40.3µs | 483.6µs |
| jsphLim | 41.3KB | 45.5KB | 30.0µs | 692.7µs |
| Raaaaaaaay86 | 51.9KB | 58.2KB | 28.4µs | 476.2µs |
| go-swd | 3.48MB | 3.88MB | 354.8µs | 319.1µs |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 25.5KB | 29.5KB | 201.8µs | 1.30ms |
| china-tjj(FB) | 25.5KB | 76.2KB | 160.8µs | 1.32ms |
| china-tjj(U64) | 70.2KB | 86.3KB | 196.0µs | 1.17ms |
| china-tjj(U64+OL) | 90.2KB | 106.3KB | 201.9µs | 1.13ms |
| china-tjj(U64+TI) | 86.2KB | 102.3KB | 206.2µs | 1.19ms |
| china-tjj(U64+OL+TI) | 106.2KB | 122.3KB | 202.6µs | 1.16ms |
| BobuSumisu-ac | 12.00MB | 13.51MB | 1.34ms | 451.0µs |
| BobuSumisu-go-ac | 280.1KB | 727.3KB | 10.96ms | 518.9µs |
| anknown | 1.58MB | 3.56MB | 560.3µs | 454.7µs |
| TheFutureIsOurs | 2.09MB | 7.89MB | 648.2µs | 216.6µs |
| orbit-w | 2.77MB | 4.07MB | 781.9µs | 199.4µs |
| sepetrov | 425.2KB | 599.1KB | 300.7µs | 792.7µs |
| cloudflare | 31.77MB | 32.12MB | 4.70ms | 591.3µs |
| petar-dambovaliev | 661.4KB | 2.21MB | 735.5µs | 1.52ms |
| iohub | 428.0KB | 1.11MB | 466.8µs | 595.3µs |
| ClarkThan | 398.5KB | 437.3KB | 266.8µs | 690.2µs |
| pgavlin | 661.4KB | 2.20MB | 728.6µs | 1.46ms |
| gnames | 1.37MB | 1.71MB | 1.03ms | 2.20ms |
| gansidui | 417.8KB | 552.2KB | 315.8µs | 946.4µs |
| coregx | 3.03MB | 6.30MB | 1.73ms | 354.8µs |
| RRethy | 327.7KB | 1.29MB | 359.4µs | 435.9µs |
| hkspirt | 456.5KB | 590.9KB | 329.5µs | 802.8µs |
| arkadijs | 2.24MB | 2.24MB | 640.5µs | 1.85ms |
| yanlinLiu0424 | 1.88MB | 3.62MB | 17.58ms | 425.7µs |
| pombredanne | 528.9KB | 1.08MB | 1.45ms | 2.88ms |
| ofw | 13.28MB | 13.56MB | 2.55ms | 389.0µs |
| Icarus0xff | 472.1KB | 606.4KB | 331.3µs | 1.06ms |
| mangotree2 | 1.94MB | 4.13MB | 673.6µs | 397.1µs |
| smotes | 510.7KB | 593.7KB | 323.8µs | 692.4µs |
| Codehardt | 1.36MB | 1.42MB | 988.3µs | 2.75ms |
| DaemonMonch | 510.7KB | 529.2KB | 171.0µs | 661.1µs |
| chowyu12 | 480.3KB | 32.2KB | 4.5µs | 807.8µs |
| codefever | 304.1KB | 2.52MB | 748.8µs | 991.0µs |
| kiry163 | 7.11MB | 29.95MB | 21.33ms | 201.35ms |
| Leon180 | 474.4KB | 545.4KB | 371.3µs | 670.4µs |
| jsphLim | 398.5KB | 434.1KB | 411.6µs | 794.0µs |
| Raaaaaaaay86 | 502.9KB | 573.9KB | 289.9µs | 571.6µs |
| go-swd | 3.61MB | 4.26MB | 592.3µs | 353.2µs |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 277.4KB | 317.6KB | 3.85ms | 792.4µs |
| china-tjj(FB) | 277.4KB | 749.7KB | 1.64ms | 800.2µs |
| china-tjj(U64) | 720.4KB | 880.6KB | 3.88ms | 802.2µs |
| china-tjj(U64+OL) | 904.4KB | 1.04MB | 4.00ms | 765.7µs |
| china-tjj(U64+TI) | 880.4KB | 1.02MB | 4.00ms | 804.1µs |
| china-tjj(U64+OL+TI) | 1.04MB | 1.20MB | 3.98ms | 779.7µs |
| BobuSumisu-ac | 110.61MB | 125.22MB | 12.53ms | 621.1µs |
| BobuSumisu-go-ac | 2.53MB | 8.92MB | 699.15ms | 762.3µs |
| anknown | 3.76MB | 16.66MB | 5.19ms | 664.0µs |
| TheFutureIsOurs | 2.09MB | 11.16MB | 3.08ms | 275.8µs |
| orbit-w | 3.12MB | 9.05MB | 61.79ms | 301.3µs |
| sepetrov | 3.77MB | 5.11MB | 3.25ms | 1.19ms |
| cloudflare | 317.17MB | 320.84MB | 54.17ms | 982.0µs |
| petar-dambovaliev | 5.60MB | 22.75MB | 8.29ms | 2.08ms |
| iohub | 3.33MB | 9.58MB | 4.53ms | 911.5µs |
| ClarkThan | 3.54MB | 3.84MB | 2.85ms | 1.12ms |
| pgavlin | 5.60MB | 22.63MB | 8.01ms | 2.08ms |
| gnames | 12.53MB | 16.69MB | 11.35ms | 2.97ms |
| gansidui | 3.72MB | 4.92MB | 3.38ms | 1.33ms |
| coregx | 27.93MB | 60.77MB | 24.84ms | 558.0µs |
| RRethy | 2.96MB | 21.13MB | 12.36ms | 696.7µs |
| hkspirt | 4.07MB | 5.27MB | 3.55ms | 1.19ms |
| arkadijs | 15.64MB | 15.64MB | 6.67ms | 2.78ms |
| yanlinLiu0424 | 17.36MB | 35.20MB | 178.15ms | 626.7µs |
| pombredanne | 4.78MB | 10.14MB | 18.04ms | 4.47ms |
| ofw | 122.50MB | 125.05MB | 36.28ms | 925.3µs |
| Icarus0xff | 4.22MB | 5.43MB | 3.60ms | 1.48ms |
| mangotree2 | 3.58MB | 18.25MB | 6.49ms | 538.9µs |
| smotes | 4.58MB | 5.55MB | 3.59ms | 1.19ms |
| Codehardt | 12.54MB | 13.15MB | 13.58ms | 4.79ms |
| DaemonMonch | 4.58MB | 4.72MB | 1.94ms | 1.09ms |
| chowyu12 | 4.30MB | 320.2KB | 40.8µs | 1.24ms |
| codefever | 3.36MB | 31.71MB | 8.17ms | 1.80ms |
| kiry163 | 11.69MB | 24.85MB | 8.44ms | 207.94ms |
| Leon180 | 4.23MB | 5.08MB | 3.87ms | 1.07ms |
| jsphLim | 3.54MB | 3.98MB | 14.36ms | 1.27ms |
| Raaaaaaaay86 | 4.50MB | 5.35MB | 3.14ms | 1.07ms |
| go-swd | 4.83MB | 8.30MB | 3.40ms | 403.6µs |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 2.81MB | 3.58MB | 47.84ms | 1.20ms |
| china-tjj(FB) | 2.81MB | 9.14MB | 20.79ms | 1.23ms |
| china-tjj(U64) | 4.91MB | 6.44MB | 49.04ms | 1.24ms |
| china-tjj(U64+OL) | 6.29MB | 7.82MB | 49.85ms | 1.23ms |
| china-tjj(U64+TI) | 6.44MB | 7.97MB | 52.09ms | 1.27ms |
| china-tjj(U64+OL+TI) | 7.82MB | 9.35MB | 49.17ms | 1.20ms |
| BobuSumisu-ac | 914.27MB | 1.007GB | 224.80ms | 2.02ms |
| BobuSumisu-go-ac | 19.40MB | 73.78MB | 43.353s | 1.14ms |
| anknown | 17.24MB | 110.84MB | 57.75ms | 926.3µs |
| TheFutureIsOurs | 8.19MB | 68.69MB | 79.49ms | 376.6µs |
| orbit-w | 9.83MB | 39.88MB | 1.311s | 384.2µs |
| sepetrov | 26.35MB | 36.96MB | 36.07ms | 1.94ms |
| cloudflare | 3.097GB | 3.132GB | 979.65ms | 2.79ms |
| petar-dambovaliev | 50.38MB | 229.53MB | 195.18ms | 4.69ms |
| iohub | 26.60MB | 77.59MB | 51.79ms | 1.36ms |
| ClarkThan | 25.26MB | 29.39MB | 34.19ms | 1.87ms |
| pgavlin | 50.38MB | 228.15MB | 192.48ms | 4.86ms |
| gnames | 100.12MB | 138.67MB | 146.98ms | 7.35ms |
| gansidui | 26.64MB | 36.54MB | 46.14ms | 2.02ms |
| coregx | 234.48MB | 539.98MB | 396.12ms | 1.12ms |
| RRethy | 22.96MB | 190.43MB | 66.47ms | 963.0µs |
| hkspirt | 29.40MB | 39.29MB | 49.57ms | 1.68ms |
| arkadijs | 123.15MB | 123.15MB | 77.17ms | 8.65ms |
| yanlinLiu0424 | 146.79MB | 304.75MB | 1.747s | 1.55ms |
| pombredanne | 39.70MB | 92.37MB | 208.95ms | 9.87ms |
| ofw | 1012.70MB | 1.010GB | 296.53ms | 2.64ms |
| Icarus0xff | 30.92MB | 40.82MB | 45.76ms | 2.07ms |
| mangotree2 | 11.36MB | 120.27MB | 73.01ms | 773.5µs |
| smotes | 33.68MB | 42.95MB | 50.73ms | 2.08ms |
| Codehardt | 100.66MB | 105.56MB | 174.77ms | 6.56ms |
| DaemonMonch | 33.68MB | 35.31MB | 24.34ms | 1.94ms |
| chowyu12 | 31.69MB | 3.06MB | 471.5µs | 1.92ms |
| codefever | 25.96MB | 292.22MB | 79.92ms | 3.22ms |
| kiry163 | 105.73MB | 248.13MB | 193.56ms | 210.96ms |
| Leon180 | 30.92MB | 39.05MB | 54.03ms | 1.99ms |
| jsphLim | 25.26MB | 31.18MB | 1.304s | 2.03ms |
| Raaaaaaaay86 | 32.92MB | 41.05MB | 45.74ms | 2.03ms |
| go-swd | N/A | N/A | N/A | N/A |

### 纯英文

#### 词表规模：100

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 3.7KB | 4.2KB | 19.9µs | 2.22ms |
| china-tjj(FB) | 3.7KB | 10.0KB | 19.2µs | 2.40ms |
| china-tjj(U64) | 12.7KB | 14.5KB | 19.2µs | 2.06ms |
| china-tjj(U64+OL) | 16.7KB | 18.5KB | 19.5µs | 1.81ms |
| china-tjj(U64+TI) | 14.5KB | 16.3KB | 19.5µs | 2.07ms |
| china-tjj(U64+OL+TI) | 18.5KB | 20.3KB | 20.2µs | 1.77ms |
| BobuSumisu-ac | 1.01MB | 1.13MB | 143.4µs | 462.4µs |
| BobuSumisu-go-ac | 29.5KB | 57.1KB | 263.1µs | 507.1µs |
| anknown | 38.0KB | 192.2KB | 84.3µs | 1.78ms |
| TheFutureIsOurs | 37.1KB | 142.0KB | 46.8µs | 738.9µs |
| orbit-w | 30.8KB | 123.1KB | 36.3µs | 724.9µs |
| sepetrov | 101.8KB | 130.7KB | 70.0µs | 2.00ms |
| cloudflare | 2.46MB | 2.49MB | 520.3µs | 393.2µs |
| petar-dambovaliev | 95.4KB | 182.9KB | 71.6µs | 1.41ms |
| iohub | 52.4KB | 112.1KB | 41.9µs | 717.3µs |
| ClarkThan | 93.1KB | 96.0KB | 54.7µs | 2.12ms |
| pgavlin | 95.4KB | 182.0KB | 65.2µs | 1.37ms |
| gnames | 114.0KB | 137.1KB | 97.6µs | 2.27ms |
| gansidui | 97.0KB | 121.2KB | 63.7µs | 2.46ms |
| coregx | 72.7KB | 215.1KB | 63.8µs | 164.8µs |
| RRethy | 97.7KB | 108.3KB | 29.6µs | 512.2µs |
| hkspirt | 104.9KB | 129.1KB | 66.2µs | 2.14ms |
| arkadijs | 329.2KB | 329.1KB | 70.3µs | 1.19ms |
| yanlinLiu0424 | 81.9KB | 205.4KB | 768.4µs | 230.8µs |
| pombredanne | 44.4KB | 110.1KB | 91.2µs | 2.75ms |
| ofw | 1.11MB | 1.13MB | 208.2µs | 522.6µs |
| Icarus0xff | 106.5KB | 130.7KB | 69.3µs | 2.28ms |
| mangotree2 | 36.1KB | 209.0KB | 100.0µs | 780.4µs |
| smotes | 114.4KB | 123.6KB | 65.3µs | 1.98ms |
| Codehardt | 114.3KB | 118.1KB | 81.9µs | 3.13ms |
| DaemonMonch | 114.3KB | 114.9KB | 36.3µs | 1.84ms |
| chowyu12 | 107.5KB | 3.7KB | 676ns | 2.29ms |
| codefever | 32.4KB | 209.5KB | 72.3µs | 868.9µs |
| kiry163 | 257.2KB | 2.24MB | 1.52ms | 4.05ms |
| Leon180 | 108.8KB | 116.9KB | 83.7µs | 1.93ms |
| jsphLim | 93.1KB | 95.7KB | 59.8µs | 2.26ms |
| Raaaaaaaay86 | 113.5KB | 121.7KB | 58.7µs | 1.83ms |
| go-swd | 3.49MB | 3.91MB | 415.4µs | 1.18ms |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 32.2KB | 36.3KB | 237.8µs | 2.76ms |
| china-tjj(FB) | 32.2KB | 92.4KB | 193.2µs | 2.76ms |
| china-tjj(U64) | 117.0KB | 133.0KB | 229.6µs | 2.56ms |
| china-tjj(U64+OL) | 157.0KB | 173.0KB | 229.4µs | 2.22ms |
| china-tjj(U64+TI) | 133.0KB | 149.0KB | 233.9µs | 2.51ms |
| china-tjj(U64+OL+TI) | 173.0KB | 189.0KB | 255.3µs | 2.06ms |
| BobuSumisu-ac | 8.27MB | 9.31MB | 1.09ms | 689.2µs |
| BobuSumisu-go-ac | 200.1KB | 493.9KB | 5.71ms | 649.8µs |
| anknown | 293.4KB | 1.70MB | 789.8µs | 1.29ms |
| TheFutureIsOurs | 160.1KB | 1.02MB | 388.4µs | 741.8µs |
| orbit-w | 229.8KB | 1008.0KB | 361.5µs | 735.6µs |
| sepetrov | 816.0KB | 1.00MB | 601.4µs | 2.73ms |
| cloudflare | 23.84MB | 24.09MB | 4.06ms | 758.5µs |
| petar-dambovaliev | 462.7KB | 1.43MB | 607.2µs | 1.98ms |
| iohub | 428.0KB | 995.5KB | 376.7µs | 1.05ms |
| ClarkThan | 748.5KB | 777.2KB | 546.9µs | 2.46ms |
| pgavlin | 462.7KB | 1.42MB | 584.9µs | 1.96ms |
| gnames | 955.8KB | 1.23MB | 958.4µs | 2.89ms |
| gansidui | 780.9KB | 983.9KB | 610.0µs | 3.08ms |
| coregx | 586.6KB | 2.20MB | 767.9µs | 258.8µs |
| RRethy | 289.1KB | 970.3KB | 303.6µs | 581.5µs |
| hkspirt | 845.7KB | 1.02MB | 638.8µs | 2.68ms |
| arkadijs | 1.73MB | 1.72MB | 497.1µs | 2.19ms |
| yanlinLiu0424 | 613.6KB | 1.70MB | 7.07ms | 348.1µs |
| pombredanne | 367.6KB | 901.8KB | 792.8µs | 4.08ms |
| ofw | 9.11MB | 9.30MB | 1.73ms | 767.4µs |
| Icarus0xff | 863.7KB | 1.04MB | 656.4µs | 2.94ms |
| mangotree2 | 208.1KB | 1.84MB | 904.2µs | 801.2µs |
| smotes | 926.2KB | 1.00MB | 596.7µs | 2.59ms |
| Codehardt | 926.2KB | 965.8KB | 762.5µs | 3.71ms |
| DaemonMonch | 928.5KB | 934.7KB | 333.6µs | 2.42ms |
| chowyu12 | 871.1KB | 32.2KB | 5.4µs | 3.14ms |
| codefever | 232.1KB | 1.87MB | 604.6µs | 1.10ms |
| kiry163 | 2.07MB | 18.82MB | 12.82ms | 11.49ms |
| Leon180 | 866.0KB | 959.1KB | 736.0µs | 2.65ms |
| jsphLim | 748.5KB | 774.1KB | 735.8µs | 2.57ms |
| Raaaaaaaay86 | 919.9KB | 1012.3KB | 573.0µs | 2.45ms |
| go-swd | 3.67MB | 4.39MB | 721.4µs | 1.59ms |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 248.2KB | 288.3KB | 4.18ms | 3.34ms |
| china-tjj(FB) | 248.2KB | 841.1KB | 2.78ms | 3.38ms |
| china-tjj(U64) | 848.2KB | 1008.3KB | 4.19ms | 3.15ms |
| china-tjj(U64+OL) | 1.09MB | 1.25MB | 4.36ms | 2.86ms |
| china-tjj(U64+TI) | 1008.2KB | 1.14MB | 4.32ms | 3.29ms |
| china-tjj(U64+OL+TI) | 1.25MB | 1.41MB | 4.54ms | 2.98ms |
| BobuSumisu-ac | 68.02MB | 76.54MB | 8.59ms | 1.64ms |
| BobuSumisu-go-ac | 1.55MB | 5.27MB | 255.71ms | 1.52ms |
| anknown | 3.18MB | 17.80MB | 10.01ms | 2.36ms |
| TheFutureIsOurs | 1.34MB | 10.76MB | 6.34ms | 1.50ms |
| orbit-w | 1.73MB | 7.86MB | 5.95ms | 1.40ms |
| sepetrov | 6.42MB | 8.74MB | 7.26ms | 5.56ms |
| cloudflare | 243.72MB | 246.33MB | 50.28ms | 1.37ms |
| petar-dambovaliev | 3.76MB | 15.36MB | 6.89ms | 4.02ms |
| iohub | 3.33MB | 7.90MB | 4.03ms | 2.43ms |
| ClarkThan | 5.90MB | 6.12MB | 5.24ms | 4.29ms |
| pgavlin | 3.76MB | 15.28MB | 6.73ms | 4.37ms |
| gnames | 7.47MB | 10.45MB | 10.52ms | 5.52ms |
| gansidui | 6.16MB | 7.80MB | 6.56ms | 4.83ms |
| coregx | 4.81MB | 19.63MB | 10.10ms | 698.7µs |
| RRethy | 2.01MB | 13.11MB | 4.71ms | 1.37ms |
| hkspirt | 6.68MB | 8.32MB | 6.66ms | 3.90ms |
| arkadijs | 10.51MB | 10.05MB | 4.35ms | 6.83ms |
| yanlinLiu0424 | 5.35MB | 15.56MB | 72.85ms | 842.3µs |
| pombredanne | 2.98MB | 7.19MB | 8.19ms | 8.94ms |
| ofw | 75.33MB | 76.90MB | 21.44ms | 1.29ms |
| Icarus0xff | 6.99MB | 8.68MB | 7.01ms | 4.89ms |
| mangotree2 | 1.56MB | 18.83MB | 10.79ms | 1.20ms |
| smotes | 7.36MB | 8.51MB | 6.36ms | 3.96ms |
| Codehardt | 7.36MB | 7.74MB | 7.53ms | 5.25ms |
| DaemonMonch | 7.51MB | 7.43MB | 3.23ms | 4.09ms |
| chowyu12 | 7.01MB | 320.2KB | 47.2µs | 4.61ms |
| codefever | 1.77MB | 18.31MB | 5.96ms | 1.74ms |
| kiry163 | 17.31MB | 159.81MB | 108.82ms | 51.95ms |
| Leon180 | 6.99MB | 8.11MB | 7.42ms | 4.02ms |
| jsphLim | 5.90MB | 6.18MB | 19.70ms | 3.16ms |
| Raaaaaaaay86 | 7.37MB | 8.45MB | 6.20ms | 3.96ms |
| go-swd | 5.16MB | 8.99MB | 4.48ms | 2.70ms |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 3.55MB | 4.32MB | 52.42ms | 4.75ms |
| china-tjj(FB) | 3.55MB | 14.38MB | 34.71ms | 5.08ms |
| china-tjj(U64) | 6.83MB | 8.36MB | 59.48ms | 5.01ms |
| china-tjj(U64+OL) | 9.02MB | 10.55MB | 57.97ms | 5.01ms |
| china-tjj(U64+TI) | 8.36MB | 9.89MB | 55.84ms | 5.20ms |
| china-tjj(U64+OL+TI) | 10.55MB | 12.08MB | 57.17ms | 4.45ms |
| BobuSumisu-ac | 567.08MB | 637.44MB | 170.92ms | 6.27ms |
| BobuSumisu-go-ac | 12.33MB | 46.46MB | 15.779s | 3.33ms |
| anknown | 42.24MB | 192.22MB | 140.64ms | 8.32ms |
| TheFutureIsOurs | 10.50MB | 96.00MB | 74.54ms | 2.17ms |
| orbit-w | 16.26MB | 67.28MB | 138.96ms | 2.49ms |
| sepetrov | 51.95MB | 68.84MB | 86.22ms | 12.67ms |
| cloudflare | 2.465GB | 2.491GB | 1.302s | 3.94ms |
| petar-dambovaliev | 33.27MB | 133.45MB | 157.55ms | 5.46ms |
| iohub | 26.60MB | 64.36MB | 42.11ms | 5.96ms |
| ClarkThan | 47.83MB | 49.77MB | 86.01ms | 7.97ms |
| pgavlin | 33.27MB | 132.59MB | 134.85ms | 5.25ms |
| gnames | 60.80MB | 89.14MB | 132.96ms | 13.11ms |
| gansidui | 50.01MB | 63.78MB | 111.44ms | 7.66ms |
| coregx | 53.83MB | 210.08MB | 167.16ms | 1.92ms |
| RRethy | 17.71MB | 127.38MB | 76.02ms | 2.83ms |
| hkspirt | 54.37MB | 68.14MB | 104.71ms | 5.41ms |
| arkadijs | 90.67MB | 77.28MB | 51.05ms | 22.35ms |
| yanlinLiu0424 | 48.82MB | 143.43MB | 760.15ms | 2.11ms |
| pombredanne | 24.98MB | 59.07MB | 102.77ms | 17.76ms |
| ofw | 628.11MB | 641.20MB | 187.73ms | 2.71ms |
| Icarus0xff | 60.53MB | 75.57MB | 120.52ms | 9.69ms |
| mangotree2 | 12.81MB | 194.91MB | 146.89ms | 1.65ms |
| smotes | 60.26MB | 72.02MB | 96.33ms | 6.39ms |
| Codehardt | 60.26MB | 64.26MB | 128.86ms | 11.16ms |
| DaemonMonch | 64.89MB | 60.95MB | 41.98ms | 8.86ms |
| chowyu12 | 59.09MB | 3.06MB | 484.6µs | 9.68ms |
| codefever | 17.24MB | 185.63MB | 63.62ms | 3.74ms |
| kiry163 | 69.32MB | 139.28MB | 115.11ms | 179.20ms |
| Leon180 | 60.53MB | 72.71MB | 145.65ms | 6.37ms |
| jsphLim | 47.83MB | 51.89MB | 1.886s | 4.20ms |
| Raaaaaaaay86 | 61.92MB | 73.37MB | 111.92ms | 7.07ms |
| go-swd | 18.40MB | 54.16MB | 44.72ms | 6.17ms |

### 中英混合

#### 词表规模：100

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 4.0KB | 4.4KB | 17.8µs | 1.46ms |
| china-tjj(FB) | 4.0KB | 11.6KB | 18.6µs | 1.51ms |
| china-tjj(U64) | 10.7KB | 12.5KB | 17.8µs | 1.39ms |
| china-tjj(U64+OL) | 13.7KB | 15.5KB | 17.5µs | 1.14ms |
| china-tjj(U64+TI) | 12.5KB | 14.3KB | 17.5µs | 1.35ms |
| china-tjj(U64+OL+TI) | 15.5KB | 17.3KB | 17.9µs | 1.15ms |
| BobuSumisu-ac | 1.22MB | 1.37MB | 181.5µs | 448.5µs |
| BobuSumisu-go-ac | 32.0KB | 61.5KB | 354.8µs | 597.6µs |
| anknown | 1.18MB | 2.00MB | 183.2µs | 756.0µs |
| TheFutureIsOurs | 1.66MB | 5.49MB | 406.3µs | 354.9µs |
| orbit-w | 2.20MB | 3.24MB | 211.1µs | 331.8µs |
| sepetrov | 72.2KB | 95.0KB | 47.5µs | 907.3µs |
| cloudflare | 2.85MB | 2.89MB | 577.7µs | 377.8µs |
| petar-dambovaliev | 129.4KB | 252.0KB | 79.1µs | 1.43ms |
| iohub | 52.4KB | 120.5KB | 49.6µs | 588.7µs |
| ClarkThan | 66.6KB | 71.1KB | 41.3µs | 1.19ms |
| pgavlin | 129.4KB | 251.0KB | 79.8µs | 1.34ms |
| gnames | 142.6KB | 173.7KB | 104.1µs | 2.24ms |
| gansidui | 69.5KB | 89.2KB | 47.3µs | 1.10ms |
| coregx | 321.6KB | 639.3KB | 228.7µs | 214.5µs |
| RRethy | 97.7KB | 109.3KB | 31.3µs | 414.8µs |
| hkspirt | 75.3KB | 95.0KB | 50.0µs | 926.9µs |
| arkadijs | 382.5KB | 382.5KB | 80.7µs | 1.76ms |
| yanlinLiu0424 | 242.2KB | 406.8KB | 2.46ms | 267.6µs |
| pombredanne | 53.6KB | 121.8KB | 123.4µs | 2.68ms |
| ofw | 1.34MB | 1.37MB | 252.1µs | 359.1µs |
| Icarus0xff | 76.9KB | 96.5KB | 50.2µs | 1.33ms |
| mangotree2 | 1.55MB | 2.38MB | 209.6µs | 651.2µs |
| smotes | 82.7KB | 91.7KB | 49.4µs | 920.5µs |
| Codehardt | 141.1KB | 145.8KB | 101.2µs | 2.73ms |
| DaemonMonch | 82.7KB | 84.9KB | 27.3µs | 1.08ms |
| chowyu12 | 77.9KB | 3.7KB | 671ns | 1.29ms |
| codefever | 44.4KB | 288.6KB | 86.7µs | 754.8µs |
| kiry163 | 969.3KB | 3.13MB | 2.45ms | 527.57ms |
| Leon180 | 79.2KB | 86.9KB | 62.0µs | 817.7µs |
| jsphLim | 66.6KB | 70.8KB | 45.5µs | 1.30ms |
| Raaaaaaaay86 | 81.9KB | 89.6KB | 44.2µs | 1.04ms |
| go-swd | 3.49MB | 3.90MB | 430.0µs | 540.2µs |

#### 词表规模：1,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 36.2KB | 40.3KB | 224.0µs | 1.85ms |
| china-tjj(FB) | 36.2KB | 111.1KB | 190.9µs | 1.86ms |
| china-tjj(U64) | 98.2KB | 114.3KB | 220.9µs | 1.66ms |
| china-tjj(U64+OL) | 126.2KB | 142.3KB | 227.1µs | 1.51ms |
| china-tjj(U64+TI) | 114.2KB | 130.3KB | 223.1µs | 1.67ms |
| china-tjj(U64+OL+TI) | 142.2KB | 158.3KB | 233.2µs | 1.52ms |
| BobuSumisu-ac | 10.77MB | 12.12MB | 1.32ms | 547.3µs |
| BobuSumisu-go-ac | 264.1KB | 704.0KB | 9.25ms | 631.6µs |
| anknown | 1.59MB | 4.15MB | 880.6µs | 861.4µs |
| TheFutureIsOurs | 2.09MB | 6.35MB | 705.5µs | 452.6µs |
| orbit-w | 2.77MB | 4.19MB | 570.8µs | 454.1µs |
| sepetrov | 678.2KB | 948.0KB | 530.8µs | 1.31ms |
| cloudflare | 27.93MB | 28.25MB | 4.69ms | 689.9µs |
| petar-dambovaliev | 591.1KB | 1.82MB | 713.3µs | 1.77ms |
| iohub | 428.0KB | 1.06MB | 461.5µs | 804.0µs |
| ClarkThan | 626.5KB | 668.6KB | 445.4µs | 1.51ms |
| pgavlin | 591.1KB | 1.81MB | 689.0µs | 1.78ms |
| gnames | 1.22MB | 1.55MB | 1.10ms | 2.67ms |
| gansidui | 654.1KB | 841.6KB | 512.3µs | 1.40ms |
| coregx | 2.72MB | 6.31MB | 2.47ms | 405.5µs |
| RRethy | 288.0KB | 1.05MB | 345.6µs | 510.0µs |
| hkspirt | 709.3KB | 896.8KB | 535.2µs | 1.15ms |
| arkadijs | 2.45MB | 2.45MB | 670.7µs | 2.30ms |
| yanlinLiu0424 | 2.21MB | 3.82MB | 26.60ms | 447.5µs |
| pombredanne | 474.9KB | 1.01MB | 1.15ms | 3.55ms |
| ofw | 11.89MB | 12.14MB | 2.66ms | 476.7µs |
| Icarus0xff | 725.3KB | 912.8KB | 549.4µs | 1.88ms |
| mangotree2 | 1.94MB | 4.71MB | 982.3µs | 682.4µs |
| smotes | 780.1KB | 876.6KB | 490.0µs | 1.17ms |
| Codehardt | 1.21MB | 1.26MB | 966.1µs | 3.12ms |
| DaemonMonch | 780.4KB | 802.0KB | 277.1µs | 1.48ms |
| chowyu12 | 733.4KB | 32.2KB | 5.2µs | 1.72ms |
| codefever | 304.1KB | 2.34MB | 728.6µs | 1.18ms |
| kiry163 | 8.60MB | 27.87MB | 22.09ms | 532.87ms |
| Leon180 | 727.5KB | 813.7KB | 606.1µs | 1.08ms |
| jsphLim | 626.5KB | 665.5KB | 587.0µs | 1.59ms |
| Raaaaaaaay86 | 772.4KB | 858.4KB | 465.7µs | 1.41ms |
| go-swd | 3.67MB | 4.42MB | 711.4µs | 735.7µs |

#### 词表规模：10,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 322.9KB | 363.1KB | 4.20ms | 1.47ms |
| china-tjj(FB) | 322.9KB | 1012.1KB | 2.40ms | 1.50ms |
| china-tjj(U64) | 868.4KB | 1.00MB | 4.32ms | 1.42ms |
| china-tjj(U64+OL) | 1.08MB | 1.24MB | 4.37ms | 1.33ms |
| china-tjj(U64+TI) | 1.00MB | 1.16MB | 4.34ms | 1.51ms |
| china-tjj(U64+OL+TI) | 1.24MB | 1.40MB | 4.44ms | 1.29ms |
| BobuSumisu-ac | 92.91MB | 104.87MB | 11.15ms | 767.1µs |
| BobuSumisu-go-ac | 2.03MB | 6.98MB | 490.13ms | 863.9µs |
| anknown | 2.94MB | 15.01MB | 15.75ms | 1.21ms |
| TheFutureIsOurs | 2.09MB | 12.02MB | 4.58ms | 606.7µs |
| orbit-w | 3.11MB | 9.82MB | 24.73ms | 614.8µs |
| sepetrov | 5.45MB | 7.52MB | 5.32ms | 2.08ms |
| cloudflare | 278.34MB | 281.57MB | 54.30ms | 2.01ms |
| petar-dambovaliev | 4.66MB | 18.89MB | 7.97ms | 2.55ms |
| iohub | 3.33MB | 8.87MB | 4.29ms | 1.16ms |
| ClarkThan | 5.05MB | 5.38MB | 4.35ms | 2.56ms |
| pgavlin | 4.66MB | 18.79MB | 8.06ms | 2.61ms |
| gnames | 10.41MB | 13.93MB | 12.28ms | 3.68ms |
| gansidui | 5.28MB | 6.83MB | 5.23ms | 1.96ms |
| coregx | 23.53MB | 59.57MB | 30.15ms | 622.3µs |
| RRethy | 2.41MB | 17.04MB | 8.08ms | 831.9µs |
| hkspirt | 5.74MB | 7.29MB | 5.35ms | 1.74ms |
| arkadijs | 14.19MB | 14.07MB | 5.82ms | 3.91ms |
| yanlinLiu0424 | 19.60MB | 35.47MB | 274.81ms | 651.2µs |
| pombredanne | 4.03MB | 8.53MB | 13.39ms | 5.83ms |
| ofw | 102.90MB | 105.04MB | 29.81ms | 1.08ms |
| Icarus0xff | 5.93MB | 7.50MB | 5.69ms | 2.76ms |
| mangotree2 | 2.38MB | 16.34MB | 17.48ms | 884.6µs |
| smotes | 6.35MB | 7.41MB | 5.18ms | 1.71ms |
| Codehardt | 10.39MB | 10.88MB | 10.79ms | 4.40ms |
| DaemonMonch | 6.39MB | 6.53MB | 2.77ms | 2.01ms |
| chowyu12 | 6.00MB | 320.2KB | 47.1µs | 2.32ms |
| codefever | 2.70MB | 25.71MB | 7.57ms | 1.98ms |
| kiry163 | 9.81MB | 20.50MB | 7.39ms | 1.010s |
| Leon180 | 5.93MB | 6.91MB | 5.82ms | 1.61ms |
| jsphLim | 5.05MB | 5.38MB | 13.17ms | 2.12ms |
| Raaaaaaaay86 | 6.30MB | 7.26MB | 4.81ms | 1.97ms |
| go-swd | 5.58MB | 11.05MB | 4.33ms | 981.9µs |

#### 词表规模：100,000

| 测试库 | 建树产物大小 | 建树内存申请量 | 建树耗时 | 匹配耗时 |
|---|---|---|---|---|
| china-tjj | 3.78MB | 4.54MB | 53.02ms | 1.98ms |
| china-tjj(FB) | 3.78MB | 12.80MB | 27.12ms | 2.01ms |
| china-tjj(U64) | 6.61MB | 8.14MB | 53.46ms | 1.96ms |
| china-tjj(U64+OL) | 8.48MB | 10.01MB | 53.93ms | 1.82ms |
| china-tjj(U64+TI) | 8.14MB | 9.67MB | 53.40ms | 1.93ms |
| china-tjj(U64+OL+TI) | 10.01MB | 11.54MB | 54.34ms | 1.84ms |
| BobuSumisu-ac | 788.88MB | 891.76MB | 373.82ms | 2.34ms |
| BobuSumisu-go-ac | 15.98MB | 60.00MB | 31.752s | 1.36ms |
| anknown | 26.16MB | 144.72MB | 143.86ms | 1.75ms |
| TheFutureIsOurs | 10.25MB | 86.94MB | 58.55ms | 874.5µs |
| orbit-w | 13.99MB | 59.20MB | 585.58ms | 920.9µs |
| sepetrov | 41.17MB | 55.56MB | 63.24ms | 4.07ms |
| cloudflare | 2.770GB | 2.801GB | 1.136s | 2.57ms |
| petar-dambovaliev | 43.58MB | 184.45MB | 170.30ms | 4.38ms |
| iohub | 26.60MB | 72.84MB | 50.41ms | 2.15ms |
| ClarkThan | 38.35MB | 40.36MB | 62.67ms | 4.27ms |
| pgavlin | 43.58MB | 183.45MB | 171.19ms | 5.01ms |
| gnames | 86.71MB | 122.45MB | 146.02ms | 7.45ms |
| gansidui | 40.21MB | 52.18MB | 84.51ms | 3.67ms |
| coregx | 209.83MB | 518.31MB | 448.55ms | 1.28ms |
| RRethy | 23.94MB | 181.70MB | 80.07ms | 1.44ms |
| hkspirt | 43.95MB | 55.91MB | 80.47ms | 2.87ms |
| arkadijs | 112.83MB | 107.72MB | 69.53ms | 10.11ms |
| yanlinLiu0424 | 167.43MB | 302.70MB | 2.732s | 1.26ms |
| pombredanne | 34.38MB | 71.10MB | 163.42ms | 10.49ms |
| ofw | 873.80MB | 892.01MB | 261.61ms | 2.51ms |
| Icarus0xff | 47.25MB | 59.72MB | 82.73ms | 4.67ms |
| mangotree2 | 12.00MB | 152.03MB | 166.57ms | 1.13ms |
| smotes | 49.21MB | 59.52MB | 70.74ms | 2.92ms |
| Codehardt | 86.43MB | 91.02MB | 156.58ms | 8.59ms |
| DaemonMonch | 50.98MB | 49.97MB | 34.46ms | 3.67ms |
| chowyu12 | 47.30MB | 3.06MB | 491.0µs | 3.72ms |
| codefever | 21.11MB | 242.89MB | 77.09ms | 3.80ms |
| kiry163 | 91.33MB | 198.52MB | 150.83ms | 2.456s |
| Leon180 | 47.25MB | 57.08MB | 91.75ms | 2.73ms |
| jsphLim | 38.35MB | 41.18MB | 1.028s | 2.98ms |
| Raaaaaaaay86 | 49.50MB | 58.92MB | 74.83ms | 4.27ms |
| go-swd | 20.99MB | 68.93MB | 45.03ms | 1.51ms |

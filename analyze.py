#!/usr/bin/env python3
"""Parse Go benchmark output and generate charts + Markdown tables."""

import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


# ── CJK font setup (cross-platform) ──────────────
def _setup_cjk_font():
    """Find and configure a CJK-capable font for matplotlib."""
    # Candidates: macOS → Linux → Windows → bundled Noto
    candidates = [
        "PingFang SC",  # macOS
        "Heiti SC",  # macOS fallback
        "STHeiti",  # macOS fallback
        "Hiragino Sans GB",  # macOS fallback
        "Microsoft YaHei",  # Windows
        "SimHei",  # Windows fallback
        "WenQuanYi Micro Hei",  # Linux
        "WenQuanYi Zen Hei",  # Linux
        "Noto Sans CJK SC",  # Linux / cross-platform
        "Noto Sans SC",  # Linux / cross-platform
        "Source Han Sans SC",  # Adobe
        "AR PL UMing CN",  # Linux fallback
        "Droid Sans Fallback",  # Android / Linux
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return name
    # If no candidate found, try to locate any .ttf with CJK support
    for f in fm.fontManager.ttflist:
        if any(k in f.name.lower() for k in ("cjk", "chinese", "hei", "song", "ming", "fang")):
            plt.rcParams["font.sans-serif"] = [f.name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return f.name
    print("WARNING: No CJK font found. Chinese text may not render correctly.", file=sys.stderr)
    return None


_cjk_font = _setup_cjk_font()
if _cjk_font:
    print(f"Using CJK font: {_cjk_font}", file=sys.stderr)

# ── parse go bench output ─────────────────────────

NAME_RE = re.compile(r"^Benchmark/(Build|Match|Reset)/(.+?)/(\w+_\d+)-\d+\s+\d+\s+")
METRIC_RE = re.compile(r"([\d.]+)\s+([\w/\-]+)")


def parse(path):
    rows = []
    with open(path) as f:
        for line in f:
            m = NAME_RE.match(line.strip())
            if not m:
                continue
            bench, lib, tc = m.group(1), m.group(2), m.group(3)
            lang, size = tc.rsplit("_", 1)
            # extract all metric pairs from remainder
            metrics = {unit: float(val) for val, unit in METRIC_RE.findall(line)}
            rows.append(dict(
                bench=bench, lib=lib, lang=lang, size=int(size),
                ns_op=metrics.get("ns/op"),
                B_op=metrics.get("B/op"),
                allocs_op=metrics.get("allocs/op"),
                free=metrics.get("free-B"),
            ))
    return rows


# ── formatting helpers ────────────────────────────

def fmt_time(ns):
    if ns is None: return "N/A"
    if ns < 1e3: return f"{ns:.0f}ns"
    if ns < 1e6: return f"{ns / 1e3:.1f}µs"
    if ns < 1e9: return f"{ns / 1e6:.2f}ms"
    return f"{ns / 1e9:.3f}s"


def fmt_bytes(b):
    if b is None: return "N/A"
    if b < 1024: return f"{b:.0f}B"
    if b < 1024 ** 2: return f"{b / 1024:.1f}KB"
    if b < 1024 ** 3: return f"{b / 1024 ** 2:.2f}MB"
    return f"{b / 1024 ** 3:.3f}GB"


LANG_TITLE = {"cn": "纯中文", "en": "纯英文", "mix": "中英混合"}


def fmt_bar_label(v, unit):
    """Short label for bar annotation – always includes unit."""
    if v <= 0: return ""
    if unit == "ms":  # value is already in ms
        if v < 0.001: return f"{v * 1e3:.1f}µs"
        if v < 1:     return f"{v * 1e3:.0f}µs"
        if v < 1000:  return f"{v:.1f}ms"
        return f"{v / 1e3:.1f}s"
    else:  # MB
        if v < 0.001: return f"{v * 1024:.0f}KB"
        if v < 1:     return f"{v * 1024:.0f}KB"
        if v < 1000:  return f"{v:.1f}MB"
        return f"{v / 1024:.1f}GB"


# ── assign stable colors ──────────────────────────

def get_colors(lib_names):
    cmap = plt.get_cmap("tab20")
    return {n: cmap(i / max(len(lib_names), 1)) for i, n in enumerate(lib_names)}


# ── charts ────────────────────────────────────────

def make_charts(rows, out_dir):
    # (bench, column, 中文标题, 显示单位, 除数, 输出文件名)
    # 文件名统一小写，前缀 bench_ 方便排序到一起
    metrics = [
        ("Reset", "free", "建树产物大小", "MB", 1024 ** 2, "bench_build_retained.png"),
        ("Build", "B_op", "建树内存申请量", "MB", 1024 ** 2, "bench_build_alloc.png"),
        ("Build", "ns_op", "建树耗时", "ms", 1e6, "bench_build_time.png"),
        ("Match", "ns_op", "匹配耗时", "ms", 1e6, "bench_match_time.png"),
    ]
    langs = ["cn", "en", "mix"]
    all_libs = list(dict.fromkeys(r["lib"] for r in rows))
    all_sizes = sorted(set(r["size"] for r in rows))
    nl = len(all_libs)
    colors = get_colors(all_libs)
    chart_files = []

    # index: (bench, lib, lang, size) -> row
    idx = {}
    for r in rows:
        idx[(r["bench"], r["lib"], r["lang"], r["size"])] = r

    for bench, col, title, unit, div, fname in metrics:
        fig, axes = plt.subplots(1, 3, figsize=(max(28, int(nl * 1.2)), 9), sharey=False)
        fig.suptitle(title, fontsize=22, fontweight="bold", y=1.02)
        for ai, lang in enumerate(langs):
            ax = axes[ai]
            ns = len(all_sizes)
            bw = 0.8 / nl
            x = np.arange(ns)
            for li, lib in enumerate(all_libs):
                vals = []
                for s in all_sizes:
                    r = idx.get((bench, lib, lang, s))
                    v = r.get(col) if r else None
                    vals.append(v / div if v else 0)
                off = (li - nl / 2 + 0.5) * bw
                ax.bar(x + off, vals, bw, label=lib, color=colors[lib],
                       edgecolor="white", linewidth=0.3)
            ax.set_title(LANG_TITLE.get(lang, lang), fontsize=16)
            ax.set_xlabel("词表大小", fontsize=13)
            ax.set_ylabel(f"{title} ({unit})", fontsize=13)
            ax.tick_params(axis="both", labelsize=11)
            ax.set_xticks(x)
            ax.set_xticklabels([f"{s:,}" for s in all_sizes])
            ax.set_yscale("log")
            ax.grid(axis="y", alpha=0.3)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=min(nl, 7),
                   fontsize=10, bbox_to_anchor=(0.5, -0.12))
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, fname), dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(f"  chart: {fname}", file=sys.stderr)
        chart_files.append(fname)
    return chart_files


# ── markdown tables ───────────────────────────────

# 图表文件名 → 中文标题（用于 README.md 中引用）
CHART_TITLES = {
    "bench_build_retained": "建树产物大小",
    "bench_build_alloc": "建树内存申请量",
    "bench_build_time": "建树耗时",
    "bench_match_time": "匹配耗时",
}


def make_tables(rows, out_path, chart_files):
    metrics = [
        ("Reset", "free", "建树产物大小", fmt_bytes),
        ("Build", "B_op", "建树内存申请量", fmt_bytes),
        ("Build", "ns_op", "建树耗时", fmt_time),
        ("Match", "ns_op", "匹配耗时", fmt_time),
    ]
    langs = ["cn", "en", "mix"]
    all_libs = list(dict.fromkeys(r["lib"] for r in rows))
    all_sizes = sorted(set(r["size"] for r in rows))

    idx = {}
    for r in rows:
        idx[(r["bench"], r["lib"], r["lang"], r["size"])] = r

    lines = ["# AC 自动机 Benchmark 结果\n",
             "## 简介\n",
             "本项目对多个 Go 语言 Aho-Corasick（AC 自动机）开源库进行性能基准测试，对比维度包括 **建树产物大小**、**建树内存申请量**、**建树耗时**、**匹配耗时**。\n",
             "### 测试数据\n",
             "- **词表规模**：每组包含 100 / 1,000 / 10,000 / 100,000 个互不重复的 pattern（词条）。\n",
             "- **纯中文词条**：由 `U+4E00`～`U+9FA5` 范围内的汉字生成；词长为 2～4 个汉字，"
             "其中 2 字词占 50%、3 字词占 35%、4 字词占 15%。\n",
             "- **纯英文词条**：由 26 个小写英文字母生成；词长服从均值为 6、标准差为 2 的近似正态分布，并限制在 3～12 个字母之间。\n",
             "- **中英混合词表**：生成每个词条时各以 50% 的概率选择中文或英文，词长规则分别沿用上述配置。\n",
             "- **字符分布**：字符按齐夫分布采样，使少数字符高频、大量字符低频；中文字符多样性随词表规模增加，"
             "英文字符池固定为 26 个小写字母。所有生成结果都会去重，直到达到目标词条数量。\n",
             "- **匹配文本**：每组生成约 100 KB 的同语言类型文本；生成过程中有 10% 的概率直接插入词表中的词条，"
             "以保证稳定的命中样本。随机数种子固定，确保各次 Benchmark 使用相同数据。\n", "### 对比库\n",
             "对比库覆盖 GitHub 搜索 [`ahocorasick language:Go`](https://github.com/search?q=ahocorasick+language%3AGo&type=repositories)"
             "（共 39 个仓库）中全部 28 个可本地基准测试的库，另补充 5 个搜索外知名库，合计 33 个库、38 个 Benchmark 目标；"
             "未收录的 11 个仓库及原因见文末「未收录仓库说明」。\n",
             "| 库 | Benchmark 名 | 实现算法 | 索引粒度 | 完整匹配结果 | 后缀链接 | 其它 |",
             "|---|---|---|---|---|---|---|",
             "| [china-tjj/ahocorasick](https://github.com/china-tjj/ahocorasick) | china-tjj | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型 |",
             "| 同上 | china-tjj(FB) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，自动选择最小 uint 类型，启用快速构建模式 |",
             "| 同上 | china-tjj(U64) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型 |",
             "| 同上 | china-tjj(U64+OL) | 紧凑Trie | auto | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接 |",
             "| 同上 | china-tjj(U64+TI) | 紧凑Trie | auto | 完整 | 无 | 紧凑数据结构，手动指定 uint64 类型，返回结果含pattern id |",
             "| 同上 | china-tjj(U64+OL+TI) | 紧凑Trie | auto | 完整 | 有 | 紧凑数据结构，手动指定 uint64 类型，开启后缀链接，返回结果含pattern id |",
             "| [BobuSumisu/aho-corasick](https://github.com/BobuSumisu/aho-corasick) | BobuSumisu-ac | 标准Trie + 预计算转移表 | byte | 完整 | 有 | 返回Match含pattern id与位置；sync.Pool复用；支持Encode/Decode(gzip) |",
             "| [BobuSumisu/go-ahocorasick](https://github.com/BobuSumisu/go-ahocorasick) | BobuSumisu-go-ac | 双数组Trie(DAT) | byte | 完整 | 有 | SaveTrie/LoadTrie；Match结果不含pattern索引(仅pos+match bytes) |",
             "| [anknown/ahocorasick](https://github.com/anknown/ahocorasick) | anknown | 双数组Trie(DAT) | rune | 完整 | 有 | 输出在构建时合并到output(等价后缀链效果)；Term不含pattern索引(靠Word) |",
             "| [TheFutureIsOurs/ahocorasick](https://github.com/TheFutureIsOurs/ahocorasick) | TheFutureIsOurs | 双数组Trie(DAT) | rune | 不完整 | 有 | output压缩：同终点/后缀只保留最长term；主打低内存/低GC |",
             "| [orbit-w/aho_corasick](https://github.com/orbit-w/aho_corasick) | orbit-w | 双数组Trie(DAT) | rune | 完整 | 有 | Trie构建时把fail节点output合并到当前节点；提供Validate/Replace等 |",
             "| [sepetrov/ahocorasick](https://github.com/sepetrov/ahocorasick) | sepetrov | 标准Trie | rune | 完整 | 有 | 返回map[patternIndex][]pos(位置是byte offset)；含suffixLink+dictSuffixLink |",
             "| [cloudflare/ahocorasick](https://github.com/cloudflare/ahocorasick) | cloudflare | 标准Trie | byte | 不完整 | 有 | Match返回命中过的pattern集合(去重、无位置)；有MatchThreadSafe/Contains |",
             "| [petar-dambovaliev/aho-corasick](https://github.com/petar-dambovaliev/aho-corasick) | petar-dambovaliev | NFA/DFA | byte | 完整 | 有 | 多种MatchKind；Standard可完整/可重叠；LeftMost*会裁剪；含prefilter/Replace/迭代器 |",
             "| [iohub/ahocorasick](https://github.com/iohub/ahocorasick) | iohub | cedar 双数组Trie | byte | 完整 | 有 | value可存任意interface{}；迭代器输出；sync.Pool复用；graphviz可视化 |",
             "| [ClarkThan/ahocorasick](https://github.com/ClarkThan/ahocorasick) | ClarkThan | 标准Trie | rune | 完整 | 有 | SearchAppend/SearchIndexedAppend支持buf复用；输出不含pattern索引(只有Hit{Start,Len}或string) |",
             "| [pgavlin/aho-corasick](https://github.com/pgavlin/aho-corasick) | pgavlin | NFA/DFA | byte | 完整 | 有 | 基本同petar分支；Standard可完整；LeftMost*会裁剪 |",
             "| [gnames/aho_corasick](https://github.com/gnames/aho_corasick) | gnames | 标准Trie | byte | 不完整 | 有 | dict link实现为单跳(仅linkDict一次，不会多级追溯)，可能漏更深后缀命中；Match含pattern索引+start/end |",
             "| [gansidui/ahocorasick](https://github.com/gansidui/ahocorasick) | gansidui | 标准Trie(map) | rune | 完整 | 无 | 匹配时沿fail链收集；许多其它Go实现参考的基础版本 |",
             "| [coregx/ahocorasick](https://github.com/coregx/ahocorasick) | coregx | DFA(扁平转移表) | byte | 完整 | 有 | 活跃维护；Byte Classes压缩字母表+预过滤；要求go>=1.25.4 |",
             "| [rrethy/ahocorasick](https://github.com/RRethy/ahocorasick) | RRethy | 双数组Trie(DAT) | byte | 完整 | 无 | 构建时合并fail节点output；支持[]byte和string输入 |",
             "| [hkspirt/ahocorasick](https://github.com/hkspirt/ahocorasick) | hkspirt | 标准Trie(map) | rune | 完整 | 无 | 基于gansidui，增加敏感词贪婪替换(Replace)功能 |",
             "| [arkadijs/ahocorasick-go](https://github.com/arkadijs/ahocorasick-go) | arkadijs | 混合Trie(浅层数组+深层map) | byte | 完整 | 无 | 构建时合并fail输出；支持context取消搜索 |",
             "| [yanlinLiu0424/ahocorasick](https://github.com/yanlinLiu0424/ahocorasick) | yanlinLiu0424 | DFA(扁平int32状态表) | byte | 完整 | 有 | Ken Steele算法变体，字母表压缩；支持忽略大小写标记 |",
             "| [pombredanne/ahocorasick](https://github.com/pombredanne/ahocorasick) | pombredanne | 数组Trie(排序切片+二分) | byte | 完整 | 有 | 显式dict后缀链接；channel流式输出，提供io.Reader接口；2013年老库 |",
             "| [ofw/ahocorasick](https://github.com/ofw/ahocorasick) | ofw | 数组Trie([256]指针) | byte | 不完整 | 无 | 相同pattern去重仅报首次命中；适合ASCII/字节流 |",
             "| [Icarus0xff/ahocorasick](https://github.com/Icarus0xff/ahocorasick) | Icarus0xff | 标准Trie(map) | rune | 完整 | 无 | 构建时合并fail输出；支持动态增删，RWMutex并发安全 |",
             "| [mangotree2/ahocorasick](https://github.com/mangotree2/ahocorasick) | mangotree2 | 双数组Trie(DAT) | rune | 语义不同 | 无 | 敏感词过滤/替换引擎，Handle执行过滤替换而非返回匹配列表 |",
             "| [smotes/ahocorasick](https://github.com/smotes/ahocorasick) | smotes | DFA(泛型) | byte/rune | 完整 | 有 | 显式DictLink；Go 1.23+迭代器API，多种匹配语义可配 |",
             "| [Codehardt/go-ahocorasick](https://github.com/Codehardt/go-ahocorasick) | Codehardt | 标准Trie(map) | byte | 完整 | 有 | 教科书式实现，维护专用outputLink |",
             "| [DaemonMonch/ac](https://github.com/DaemonMonch/ac) | DaemonMonch | 标准Trie(map) | rune | 完整 | 无 | 构建时合并fail链emits；延迟初始化失配指针 |",
             "| [chowyu12/ahocorasick](https://github.com/chowyu12/ahocorasick) | chowyu12 | 标准Trie(map) | rune | 完整 | 无 | 支持编译后动态增量添加模式串，并发读写保护 |",
             "| [codefever/ahocorasick](https://github.com/codefever/ahocorasick) | codefever | 双数组Trie(DAT) | byte | 完整 | 有 | 显式suffixLink数组；支持每个pattern映射自定义value |",
             "| [kiry163/ahocorasick](https://github.com/kiry163/ahocorasick) | kiry163 | DFA/NFA(按规模自动选择) | byte | 完整 | 有 | Rust aho-corasick的Go移植，含prefilter等优化 |",
             "| [Leon180/AhoCorasick](https://github.com/Leon180/AhoCorasick) | Leon180 | 标准Trie(map) | rune | 完整 | 无 | 支持后台异步重构，适合词库频繁变动场景 |",
             "| [jsphLim/Base_AhoCorasick](https://github.com/jsphLim/Base_AhoCorasick) | jsphLim | 标准Trie(map) | rune | 不完整 | 无 | 原型实现，未合并fail输出，位置计算有缺陷 |",
             "| [raaaaaaaay86/ahocorasick](https://github.com/Raaaaaaaay86/ahocorasick) | Raaaaaaaay86 | 标准Trie(map) | rune | 完整 | 无 | 构建时递归合并fail输出；提供仅最长匹配的过滤选项 |",
             "| [kirklin/go-swd](https://github.com/kirklin/go-swd) | go-swd | 混合Trie(根部dense+深层排序边) | rune | 完整 | 有 | 敏感词检测库，支持Gap匹配/重复折叠/2-gram预过滤；benchmark已关闭默认词库；字母表上限16383个不同字符(超出的大词表中文用例跳过) |",
             "",
             "### 未收录仓库说明\n",
             "GitHub 搜索 `ahocorasick language:Go` 共 39 个仓库，以下 11 个未纳入 Benchmark：\n",
             "| 仓库 | 未收录原因 |", "|---|---|",
             "| [heidawei/AhoCorasickDoubleArrayTrie](https://github.com/heidawei/AhoCorasickDoubleArrayTrie) | 库自身 bug：移植 Java 版时用 Go map 替代原版有序 Map，兄弟节点顺序随机导致 DAT size 少算，fail/output 表长度不足，构建期随机 panic（还可能静默截断数据） |",
             "| [go-ego/cedar](https://github.com/go-ego/cedar) | 双数组前缀树（Insert/PrefixMatch），aho 子目录为空包，不是完整 AC 自动机 |",
             "| [tmikus/ahocorasick_rs](https://github.com/tmikus/ahocorasick_rs) | Rust 库 BurntSushi/aho-corasick 的 CGO 封装，匹配引擎非 Go 实现 |",
             "| [Hoshinonyaruko/Sanae_Filter](https://github.com/Hoshinonyaruko/Sanae_Filter) | 敏感词过滤 HTTP 服务（main 程序），非可 import 的库，无 go.mod |",
             "| [skyoo2003/acor](https://github.com/skyoo2003/acor) | 词典存储在 Redis/Valkey，依赖外部服务，非纯内存本地库 |",
             "| [theflavoroflife/ahocorasick](https://github.com/theflavoroflife/ahocorasick) | go.mod 声明 `module ahocorasick` 与仓库路径不匹配，无法 go get |",
             "| [yjb2807/ahocorasick](https://github.com/yjb2807/ahocorasick) | anknown/ahocorasick 的镜像拷贝（anknown 已收录） |",
             "| [duggytuxy/ahocorasick](https://github.com/duggytuxy/ahocorasick) | coregx/ahocorasick 的复制重发（coregx 已收录），且要求 go>=1.26.5 |",
             "| [yflau/ahocorasick](https://github.com/yflau/ahocorasick) | 2012 年 Google Code 官方仓库的导出镜像，GOPATH 时代代码，无 go.mod |",
             "| [jsphLim/Aho_Filter](https://github.com/jsphLim/Aho_Filter) | 使用相对路径 import（`./ac`）的 main 程序，不支持 module 模式 |",
             "| [dcto/go-sieve](https://github.com/dcto/go-sieve) | 匹配核心复用 anknown（已收录），自身是带 SQLite 依赖的应用层封装 |",
             "",
             "**注**：个别库对数据有限制（如 go-swd 字母表上限 16383 个不同字符），不支持的用例会在 Benchmark 中跳过（日志输出 SKIP），对应单元格显示 N/A。\n",
             "## 图表总览\n"]

    # ── intro ──

    # ── images first ──
    for cf in chart_files:
        key = cf.replace(".png", "")
        title = CHART_TITLES.get(key, key)
        lines.append(f"### {title}\n")
        lines.append(f"![{title}]({cf})\n")

    # ── then tables ──
    lines.append("---\n")
    lines.append("## 详细数据\n")
    metric_headers = [title for _, _, title, _ in metrics]
    for lang in langs:
        lines.append(f"### {LANG_TITLE.get(lang, lang)}\n")
        for size in all_sizes:
            lines.append(f"#### 词表规模：{size:,}\n")
            header = "| 测试库 | " + " | ".join(metric_headers) + " |"
            separator = "|" + "|".join(["---"] * (len(metrics) + 1)) + "|"
            lines += [header, separator]
            for lib in all_libs:
                cells = []
                for bench, col, _, fmt_fn in metrics:
                    row = idx.get((bench, lib, lang, size))
                    value = row.get(col) if row else None
                    cells.append(fmt_fn(value))
                lines.append(f"| {lib} | " + " | ".join(cells) + " |")
            lines.append("")

    md = "\n".join(lines)
    with open(out_path, "w") as f:
        f.write(md)
    print(f"  markdown: {out_path}", file=sys.stderr)


# ── main ──────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <bench.txt>", file=sys.stderr)
        sys.exit(1)
    rows = parse(sys.argv[1])
    if not rows:
        print("No benchmark data found.", file=sys.stderr)
        sys.exit(1)
    print(f"Parsed {len(rows)} rows", file=sys.stderr)
    out = os.path.dirname(sys.argv[1]) or "."
    chart_files = make_charts(rows, out)
    md_path = os.path.join(out, "README.md")
    make_tables(rows, md_path, chart_files)
    # 输出保存汇总
    print(f"\n✅ 已保存到 {out}/:", file=sys.stderr)
    for cf in chart_files:
        print(f"   图表: {cf}", file=sys.stderr)
    print(f"   报告: README.md", file=sys.stderr)


if __name__ == "__main__":
    main()

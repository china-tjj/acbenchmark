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

NAME_RE = re.compile(r"^Benchmark/(Build|Match)/(.+?)/(\w+_\d+)-\d+\s+\d+\s+")
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
                retained=metrics.get("retained-B"),
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
        ("Build", "ns_op", "建树耗时", "ms", 1e6, "bench_build_time.png"),
        ("Build", "B_op", "建树内存申请量", "MB", 1024 ** 2, "bench_build_alloc.png"),
        ("Build", "retained", "建树产物占用", "MB", 1024 ** 2, "bench_build_retained.png"),
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
        fig, axes = plt.subplots(1, 3, figsize=(28, 9), sharey=False)
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
    "bench_build_time": "建树耗时",
    "bench_build_alloc": "建树内存申请量",
    "bench_build_retained": "建树产物占用",
    "bench_match_time": "匹配耗时",
}


def make_tables(rows, out_path, chart_files):
    metrics = [
        ("Build", "ns_op", "建树耗时", fmt_time),
        ("Build", "B_op", "建树内存申请量", fmt_bytes),
        ("Build", "retained", "建树产物占用", fmt_bytes),
        ("Match", "ns_op", "匹配耗时", fmt_time),
    ]
    langs = ["cn", "en", "mix"]
    all_libs = list(dict.fromkeys(r["lib"] for r in rows))
    all_sizes = sorted(set(r["size"] for r in rows))

    idx = {}
    for r in rows:
        idx[(r["bench"], r["lib"], r["lang"], r["size"])] = r

    lines = ["# AC 自动机 Benchmark 结果\n"]

    # ── intro ──
    lines.append("## 简介\n")
    lines.append("本项目对多个 Go 语言 Aho-Corasick（AC 自动机）开源库进行性能基准测试，"
                 "对比维度包括 **建树耗时**、**建树内存申请量**、**建树产物内存占用**、**匹配耗时**。\n")
    lines.append("测试词表覆盖 100 / 1,000 / 10,000 / 100,000 四种规模，"
                 "语言类型涵盖纯中文、纯英文、中英混合（各 50%），"
                 "词表由代码随机构造并模拟真实概率分布。\n")
    lines.append("### 对比库\n")
    lines.append("| 库 | Benchmark 名 | 说明 |")
    lines.append("|---|---|---|")
    lines.append(
        "| [china-tjj/acautomaton](https://github.com/china-tjj/acautomaton) | china-tjj | 紧凑 Trie，三级索引（线性/二分/哈希），自动选择最小 uint 类型 |")
    lines.append("| 同上 | china-tjj(SL) | 同上 + 构建后缀链接（加速匹配，额外 O(N) 空间） |")
    lines.append("| 同上 | china-tjj(U64) | 同上，手动指定 uint64 索引（与其他库同一维度对比） |")
    lines.append("| 同上 | china-tjj(SL+U64) | 后缀链接 + uint64 索引 |")
    lines.append(
        "| [BobuSumisu/aho-corasick](https://github.com/BobuSumisu/aho-corasick) | BobuSumisu-ac | DFA 矩阵实现，构建快，int 索引 |")
    lines.append(
        "| [BobuSumisu/go-ahocorasick](https://github.com/BobuSumisu/go-ahocorasick) | BobuSumisu-go-ac | 双数组 Trie，作者旧版实现 |")
    lines.append(
        "| [anknown/ahocorasick](https://github.com/anknown/ahocorasick) | anknown | 双数组 Trie，int 索引，内存占用低 |")
    lines.append(
        "| [sepetrov/ahocorasick](https://github.com/sepetrov/ahocorasick) | sepetrov | 标准 Trie，map 存储子节点 |")
    lines.append(
        "| [cloudflare/ahocorasick](https://github.com/cloudflare/ahocorasick) | cloudflare | 标准 Trie，[]byte 匹配，int 索引 |")
    lines.append(
        "| [petar-dambovaliev/aho-corasick](https://github.com/petar-dambovaliev/aho-corasick) | petar-dambovaliev | 移植自 Rust BurntSushi 库，NFA 模式 |")
    lines.append("| [iohub/ahocorasick](https://github.com/iohub/ahocorasick) | iohub | cedar 双数组实现 |")
    lines.append(
        "| [ClarkThan/ahocorasick](https://github.com/ClarkThan/ahocorasick) | ClarkThan | 标准 Trie，map[rune]*Node |")
    lines.append(
        "| [pgavlin/aho-corasick](https://github.com/pgavlin/aho-corasick) | pgavlin | 源自 petar-dambovaliev，支持 NFA/DFA 切换 |")
    lines.append(
        "| [gnames/aho_corasick](https://github.com/gnames/aho_corasick) | gnames | 标准 Trie，字节级匹配，含后缀链接 |")
    lines.append("")

    # ── images first ──
    lines.append("## 图表总览\n")
    for cf in chart_files:
        key = cf.replace(".png", "")
        title = CHART_TITLES.get(key, key)
        lines.append(f"### {title}\n")
        lines.append(f"![{title}]({cf})\n")

    # ── then tables ──
    lines.append("---\n")
    lines.append("## 详细数据\n")
    for bench, col, title, fmt_fn in metrics:
        lines.append(f"### {title}\n")
        for lang in langs:
            lines.append(f"#### {LANG_TITLE.get(lang, lang)}\n")
            hdr = "| Library | " + " | ".join(f"{s:,}" for s in all_sizes) + " |"
            sep = "|" + "|".join(["---"] * (len(all_sizes) + 1)) + "|"
            lines += [hdr, sep]
            for lib in all_libs:
                cells = []
                for s in all_sizes:
                    r = idx.get((bench, lib, lang, s))
                    v = r.get(col) if r else None
                    cells.append(fmt_fn(v))
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

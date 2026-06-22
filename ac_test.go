package acbenchmark

import (
	"fmt"
	"math"
	"math/rand"
	"runtime"
	"runtime/debug"
	"strings"
	"sync"
	"testing"

	"github.com/china-tjj/acautomaton"

	bobuac "github.com/BobuSumisu/aho-corasick"
	bobugoac "github.com/BobuSumisu/go-ahocorasick"
	clarkthanac "github.com/ClarkThan/ahocorasick"
	anknownac "github.com/anknown/ahocorasick"
	cloudflareac "github.com/cloudflare/ahocorasick"
	gnamesac "github.com/gnames/aho_corasick"
	iohubac "github.com/iohub/ahocorasick"
	petarac "github.com/petar-dambovaliev/aho-corasick"
	pgavlinac "github.com/pgavlin/aho-corasick"
	sepetrovac "github.com/sepetrov/ahocorasick"
)

// ── library adapters ──────────────────────────────

// lib wraps each AC library behind a uniform interface.
// setup returns (build, match, reset) closures sharing the automaton variable.
// reset nils out the automaton so GC can reclaim it (used for retained measurement).
type lib struct {
	name  string
	setup func(patterns []string, text string) (build func(), match func() int, reset func())
}

func chinaTJJSetup(opts ...acautomaton.Option) func([]string, string) (func(), func() int, func()) {
	return func(p []string, t string) (func(), func() int, func()) {
		var ac acautomaton.IAcAutomaton
		return func() { ac = acautomaton.NewAcAutomaton(p, opts...) },
			func() int { return len(ac.MatchAll(t)) },
			func() { ac = nil }
	}
}

var libs = []lib{
	// ── china-tjj variants ──
	{"china-tjj", chinaTJJSetup()},
	{"china-tjj(SL)", chinaTJJSetup(acautomaton.WithOutputLink(true))},
	{"china-tjj(U64)", chinaTJJSetup(acautomaton.WithDType(acautomaton.DTypeUint64))},
	{"china-tjj(SL+U64)", chinaTJJSetup(acautomaton.WithOutputLink(true), acautomaton.WithDType(acautomaton.DTypeUint64))},

	// ── other libraries ──
	{"BobuSumisu-ac", func(p []string, t string) (func(), func() int, func()) {
		var trie *bobuac.Trie
		return func() { trie = bobuac.NewTrieBuilder().AddStrings(p).Build() },
			func() int { return len(trie.MatchString(t)) },
			func() { trie = nil }
	}},
	{"BobuSumisu-go-ac", func(p []string, t string) (func(), func() int, func()) {
		var trie *bobugoac.Trie
		return func() { trie = bobugoac.NewTrieBuilder().AddStrings(p).Build() },
			func() int { return len(trie.MatchString(t)) },
			func() { trie = nil }
	}},
	{"anknown", func(p []string, t string) (func(), func() int, func()) {
		rp := make([][]rune, len(p))
		for i, s := range p {
			rp[i] = []rune(s)
		}
		rt := []rune(t)
		var m anknownac.Machine
		return func() { m.Build(rp) },
			func() int { return len(m.MultiPatternSearch(rt, false)) },
			func() { m = anknownac.Machine{} }
	}},
	{"sepetrov", func(p []string, t string) (func(), func() int, func()) {
		var trie sepetrovac.Trie
		return func() { trie = sepetrovac.New(p) },
			func() int {
				n := 0
				for _, v := range trie.Search(t) {
					n += len(v)
				}
				return n
			},
			func() { trie = sepetrovac.Trie{} }
	}},
	{"cloudflare", func(p []string, t string) (func(), func() int, func()) {
		var m *cloudflareac.Matcher
		tb := []byte(t)
		return func() { m = cloudflareac.NewStringMatcher(p) },
			func() int { return len(m.Match(tb)) },
			func() { m = nil }
	}},
	{"petar-dambovaliev", func(p []string, t string) (func(), func() int, func()) {
		var ac petarac.AhoCorasick
		builder := petarac.NewAhoCorasickBuilder(petarac.Opts{})
		return func() { ac = builder.Build(p) },
			func() int { return len(ac.FindAll(t)) },
			func() { ac = petarac.AhoCorasick{} }
	}},
	{"iohub", func(p []string, t string) (func(), func() int, func()) {
		var m *iohubac.Matcher
		tb := []byte(t)
		bp := make([][]byte, len(p))
		for i, s := range p {
			bp[i] = []byte(s)
		}
		return func() {
				m = iohubac.NewMatcher()
				for _, pat := range bp {
					m.Insert(pat, nil)
				}
				m.Compile()
			},
			func() int {
				resp := m.Match(tb)
				n := 0
				for resp.HasNext() {
					n += len(resp.NextMatchItem(tb))
				}
				resp.Release()
				return n
			},
			func() { m = nil }
	}},
	{"ClarkThan", func(p []string, t string) (func(), func() int, func()) {
		var m *clarkthanac.Matcher
		return func() {
				m = clarkthanac.NewMatcher()
				m.BuildWithPatterns(p)
			},
			func() int { return len(m.Search(t)) },
			func() { m = nil }
	}},
	{"pgavlin", func(p []string, t string) (func(), func() int, func()) {
		var ac pgavlinac.AhoCorasick
		builder := pgavlinac.NewAhoCorasickBuilder(pgavlinac.Opts{})
		return func() { ac = builder.Build(p) },
			func() int { return len(ac.FindAll(t)) },
			func() { ac = pgavlinac.AhoCorasick{} }
	}},
	{"gnames", func(p []string, t string) (func(), func() int, func()) {
		var trie gnamesac.AhoCorasick
		return func() {
				trie = gnamesac.New()
				trie.Setup(p)
			},
			func() int { return len(trie.Search(t)) },
			func() { trie = nil }
	}},
}

// ── test data generation (Zipf distribution) ─────

// 打乱的汉字池（0x4E00 ~ 0x9FA5），避免连续字符集对某些数据结构有优势
var cnPool []rune

// 打乱的英文字母池
var enPool []byte

func init() {
	// 汉字 Unicode 范围：0x4E00 (一) ~ 0x9FA5 (龥)
	for c := rune(0x4E00); c <= rune(0x9FA5); c++ {
		cnPool = append(cnPool, c)
	}
	rng := rand.New(rand.NewSource(0))
	rng.Shuffle(len(cnPool), func(i, j int) { cnPool[i], cnPool[j] = cnPool[j], cnPool[i] })

	// 英文小写字母，打乱顺序
	for c := byte('a'); c <= 'z'; c++ {
		enPool = append(enPool, c)
	}
	rng.Shuffle(len(enPool), func(i, j int) { enPool[i], enPool[j] = enPool[j], enPool[i] })
}

// zipfIdx 使用齐夫定律的逆采样：小索引概率高，大索引概率低
func zipfIdx(r *rand.Rand, size int) int {
	return int(float64(size) * (1 - math.Pow(r.Float64(), 0.3)))
}

// rCnChar 生成单个随机汉字（齐夫分布）
// charDiversity 控制字符多样性，与词表规模正相关
func rCnChar(r *rand.Rand, charDiversity int) rune {
	idx := zipfIdx(r, charDiversity)
	return cnPool[idx%len(cnPool)]
}

// rEnChar 生成单个随机英文字母（齐夫分布）
func rEnChar(r *rand.Rand, charDiversity int) byte {
	idx := zipfIdx(r, charDiversity)
	return enPool[idx%len(enPool)]
}

func rWord(r *rand.Rand, lang string, cnDiv, enDiv int) string {
	var sb strings.Builder
	switch lang {
	case "cn":
		// 中文词长：2 字 50%，3 字 35%，4 字 15%
		n := 2
		if p := r.Float64(); p > 0.85 {
			n = 4
		} else if p > 0.50 {
			n = 3
		}
		for i := 0; i < n; i++ {
			sb.WriteRune(rCnChar(r, cnDiv))
		}
	case "en":
		// 英文词长近似正态：均值 6，范围 3~12
		n := int(math.Round(r.NormFloat64()*2 + 6))
		if n < 3 {
			n = 3
		} else if n > 12 {
			n = 12
		}
		for i := 0; i < n; i++ {
			sb.WriteByte(rEnChar(r, enDiv))
		}
	default: // mix — 中文英文各用各自的 diversity
		if r.Float64() < 0.5 {
			return rWord(r, "cn", cnDiv, enDiv)
		}
		return rWord(r, "en", cnDiv, enDiv)
	}
	return sb.String()
}

// diversityForSize 根据词表规模确定中文和英文各自的字符多样性
func diversityForSize(dictSize int) (cnDiv, enDiv int) {
	// 中文：100 词 → ~500 字符多样性，100K 词 → ~8000
	cnDiv = min(dictSize*5, len(cnPool))
	// 英文：字母只有 26 个，diversity 控制分布集中度
	enDiv = min(dictSize/4+10, len(enPool))
	return
}

func genPatterns(r *rand.Rand, n int, lang string) []string {
	cnDiv, enDiv := diversityForSize(n)
	seen := make(map[string]bool, n)
	out := make([]string, 0, n)
	for len(out) < n {
		w := rWord(r, lang, cnDiv, enDiv)
		if !seen[w] {
			seen[w] = true
			out = append(out, w)
		}
	}
	return out
}

func genText(r *rand.Rand, lang string, pats []string) string {
	const size = 100 << 10 // 100 KB
	cnDiv, enDiv := diversityForSize(len(pats))
	var sb strings.Builder
	sb.Grow(size + 4096)
	for sb.Len() < size {
		if r.Float64() < 0.10 && len(pats) > 0 {
			// 10% 概率插入词表中的词，保证命中率
			sb.WriteString(pats[r.Intn(len(pats))])
		} else if lang == "en" {
			sb.WriteString(rWord(r, "en", cnDiv, enDiv))
			sb.WriteByte(' ')
		} else if lang == "cn" {
			sb.WriteRune(rCnChar(r, cnDiv))
		} else { // mix
			if r.Float64() < 0.5 {
				sb.WriteRune(rCnChar(r, cnDiv))
			} else {
				sb.WriteByte(rEnChar(r, enDiv))
			}
		}
	}
	return sb.String()
}

// ── cached test cases ─────────────────────────────

type testCase struct {
	name     string
	patterns []string
	text     string
}

var (
	tcOnce  sync.Once
	tcCache []testCase
)

func testCases() []testCase {
	tcOnce.Do(func() {
		rng := rand.New(rand.NewSource(42))
		for _, lang := range []string{"cn", "en", "mix"} {
			for _, sz := range []int{100, 1_000, 10_000, 100_000} {
				pats := genPatterns(rng, sz, lang)
				text := genText(rng, lang, pats)
				tcCache = append(tcCache, testCase{
					name:     fmt.Sprintf("%s_%d", lang, sz),
					patterns: pats,
					text:     text,
				})
			}
		}
	})
	return tcCache
}

// ── benchmarks ────────────────────────────────────
// 统一入口：先 bench build，再用最后一次 build 的结果 bench match，
// retained 通过 reset→GC→baseline 差值获得，无需额外构建。

func Benchmark(b *testing.B) {
	for _, tc := range testCases() {
		for _, l := range libs {
			tc, l := tc, l
			buildFn, matchFn, resetFn := l.setup(tc.patterns, tc.text)

			// ── Build ──
			b.Run("Build/"+l.name+"/"+tc.name, func(b *testing.B) {
				// 清除上一轮 calibration 残留，测量 baseline
				resetFn()
				runtime.GC()
				debug.FreeOSMemory()
				runtime.GC()
				var m1 runtime.MemStats
				runtime.ReadMemStats(&m1)

				b.ReportAllocs()
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					buildFn()
				}

				// 测量 retained：GC 后只有最后一次 build 的产物存活
				b.StopTimer()
				runtime.GC()
				debug.FreeOSMemory()
				runtime.GC()
				var m2 runtime.MemStats
				runtime.ReadMemStats(&m2)
				if d := int64(m2.HeapAlloc) - int64(m1.HeapAlloc); d > 0 {
					b.ReportMetric(float64(d), "retained-B")
				}
			})

			// ── Match ── 直接复用 Build 最后一次的结果，无需再构建
			b.Run("Match/"+l.name+"/"+tc.name, func(b *testing.B) {
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					matchFn()
				}
			})
		}
	}
}

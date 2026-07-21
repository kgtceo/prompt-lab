"use client";

import { useState } from "react";
import { getExample, run } from "../lib/api";
import type { LabResult, TestCase } from "../lib/types";

export default function Home() {
  const [prompt, setPrompt] = useState("Classify the sentiment of this review: {input}");
  const [cases, setCases] = useState<TestCase[]>([{ input: "", expectation: "" }]);
  const [result, setResult] = useState<LabResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setCase(i: number, k: "input" | "expectation", v: string) {
    setCases((cs) => cs.map((c, j) => (j === i ? { ...c, [k]: v } : c)));
  }

  async function go() {
    const cs = cases.filter((c) => c.input.trim() && c.expectation.trim());
    if (!prompt.includes("{input}")) { setError("Your prompt must contain the {input} placeholder."); return; }
    if (cs.length === 0) { setError("Add at least one test case (input + expectation)."); return; }
    setLoading(true); setError(null); setResult(null);
    try { setResult(await run(prompt, cs)); }
    catch (e) { setError(e instanceof Error ? e.message : "Something went wrong."); }
    finally { setLoading(false); }
  }

  async function loadExample() {
    try { const ex = await getExample(); setPrompt(ex.prompt); setCases(ex.cases); setResult(null); } catch {}
  }

  const rateClass = result ? (result.pass_rate >= 0.8 ? "hi" : result.pass_rate >= 0.5 ? "mid" : "lo") : "";

  return (
    <div className="container">
      <header>
        <h1>prompt-lab</h1>
        <p>Measure a prompt, don&rsquo;t vibe it. Add test cases; it runs your prompt, an independent judge scores each output, and suggests a better prompt.</p>
      </header>

      <label htmlFor="p">Prompt (must include <code>{"{input}"}</code>)</label>
      <textarea id="p" value={prompt} onChange={(e) => setPrompt(e.target.value)} />

      <label>Test cases — <span style={{ color: "var(--muted)" }}>input + what a good output should do</span></label>
      {cases.map((c, i) => (
        <div className="case" key={i}>
          <input type="text" placeholder="input" value={c.input} onChange={(e) => setCase(i, "input", e.target.value)} />
          <input type="text" placeholder="expectation (e.g. one word: positive)" value={c.expectation} onChange={(e) => setCase(i, "expectation", e.target.value)} />
          {cases.length > 1 && <button className="ghost" onClick={() => setCases((cs) => cs.filter((_, j) => j !== i))}>✕</button>}
        </div>
      ))}
      <button className="ghost" onClick={() => setCases((cs) => [...cs, { input: "", expectation: "" }])}>+ Add case</button>

      <div className="actions">
        <button onClick={go} disabled={loading}>{loading ? "Running…" : "Run"}</button>
        <button className="ghost" onClick={loadExample} disabled={loading}>Load example</button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="panel">
          <div className={`rate ${rateClass}`}>{Math.round(result.pass_rate * 100)}% <span style={{ fontSize: 14, color: "var(--muted)", fontWeight: 400 }}>({result.passed}/{result.total})</span></div>
          <table>
            <thead><tr><th>✓</th><th>Input</th><th>Output</th><th>Why</th></tr></thead>
            <tbody>
              {result.results.map((r, i) => (
                <tr key={i}>
                  <td className={r.passed ? "pass" : "fail"}>{r.passed ? "✓" : "✗"}</td>
                  <td className="io">{r.input}</td>
                  <td className="io">{r.output}</td>
                  <td className="io">{r.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="sec-title">Failure pattern</div>
          <p style={{ margin: 0, fontSize: 14 }}>{result.failure_summary}</p>
          <div className="sec-title">Suggested prompt</div>
          <div className="improved">{result.improved_prompt}</div>
        </div>
      )}
    </div>
  );
}

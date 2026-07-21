// Mirrors the backend Pydantic models (prompt_lab.models).

export interface TestCase {
  input: string;
  expectation: string;
}

export interface CaseResult {
  input: string;
  expectation: string;
  output: string;
  passed: boolean;
  reason: string;
}

export interface LabResult {
  prompt: string;
  results: CaseResult[];
  passed: number;
  total: number;
  pass_rate: number;
  failure_summary: string;
  improved_prompt: string;
}

export interface ExampleResponse {
  prompt: string;
  cases: TestCase[];
}

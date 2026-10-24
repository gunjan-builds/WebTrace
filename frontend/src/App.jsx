
import { useState } from 'react'

function App() {
  const [url, setUrl] = useState('')
  const [objective, setObjective] = useState('')
  const [loading, setLoading] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [executionResults, setExecutionResults] = useState(null)
  const [error, setError] = useState('')

  async function handleRunTest(event) {
    event.preventDefault()

    setLoading(true)
    setError('')
    setTestResult(null)
    setExecutionResults(null)

    try {
      // Step 1: Create and execute the test
      const response = await fetch('http://127.0.0.1:8000/api/tests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          objective: objective,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Failed to start the test.'
        )
      }

      setTestResult(data)

      // Step 2: Fetch the actual execution results
      if (data.run_id) {
        const resultsResponse = await fetch(
          `http://127.0.0.1:8000/api/tests/${data.run_id}/report`
        )

        const resultsData = await resultsResponse.json()

        if (!resultsResponse.ok) {
          throw new Error(
            'Test ran, but execution results could not be retrieved.'
          )
        }

        setExecutionResults(resultsData)
      } else {
        throw new Error('The backend did not return a test run ID.')
      }
    } catch (err) {
      setError(
        err.message ||
          'Could not connect to the backend. Check that FastAPI is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  const steps = executionResults?.steps ?? []
  const passedCount = steps.filter(
    (step) => step.status === 'passed'
  ).length
  const failedCount = steps.filter(
    (step) => step.status === 'failed'
  ).length

  return (
    <div className="min-h-screen bg-[#071225] text-slate-100 md:flex">
      {/* Sidebar */}
      <aside className="w-full border-b border-white/10 bg-[#0a162b] p-5 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-600 text-xl font-bold">
            W
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-wide">WebTrace</h1>
            <p className="text-xs text-slate-400">Autonomous AI QA</p>
          </div>
        </div>

        <p className="mb-3 mt-9 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Workspace
        </p>

        <nav className="space-y-2">
          <div className="flex items-center gap-3 rounded-xl bg-violet-500/15 px-4 py-3 text-sm font-medium text-violet-300">
            <span>◫</span> Dashboard
          </div>

          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-400">
            <span>◷</span> Test Runs
          </div>

          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-400">
            <span>▤</span> Reports
          </div>

          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-400">
            <span>⚙</span> Settings
          </div>
        </nav>

        <div className="mt-10 rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-sm font-medium">AI Test Engine</p>

          <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Dashboard connected
          </div>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Submit a test to execute browser actions and retrieve results.
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="min-w-0 flex-1 p-5 md:p-9 lg:p-12">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
          <div>
            <p className="text-sm text-slate-400">Workspace / Dashboard</p>
            <h2 className="mt-2 text-2xl font-semibold">Dashboard</h2>
          </div>

          <div className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-300">
            AI-powered testing
          </div>
        </header>

        {/* Welcome section */}
        <section className="mb-8 mt-9">
          <p className="text-sm font-medium text-violet-400">
            AUTONOMOUS QUALITY ASSURANCE
          </p>

          <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
            Test smarter.{' '}
            <span className="text-violet-400">Ship confidently.</span>
          </h2>

          <p className="mt-4 max-w-2xl leading-7 text-slate-400">
            Give WebTrace a website and describe what you want to test.
            Your AI testing engine will explore the journey and report what happens.
          </p>
        </section>

        {/* Test creation form */}
        <section className="rounded-2xl border border-white/10 bg-[#0c1a31] p-5 shadow-xl shadow-black/10 md:p-7">
          <div className="mb-6">
            <h3 className="text-lg font-semibold">Create a test run</h3>
            <p className="mt-1 text-sm text-slate-400">
              No scripts. Just describe the test in plain English.
            </p>
          </div>

          <form onSubmit={handleRunTest} className="space-y-6">
            <div>
              <label
                htmlFor="url"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Website URL
              </label>

              <input
                id="url"
                type="url"
                required
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://example.com"
                className="w-full rounded-xl border border-white/10 bg-[#071225] px-4 py-3.5 text-sm outline-none transition placeholder:text-slate-600 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
              />
            </div>

            <div>
              <label
                htmlFor="objective"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                What should WebTrace test?
              </label>

              <textarea
                id="objective"
                required
                rows={5}
                value={objective}
                onChange={(event) => setObjective(event.target.value)}
                placeholder="Example: Open the login page, enter valid credentials, click Login, and verify that the dashboard appears."
                className="w-full resize-y rounded-xl border border-white/10 bg-[#071225] px-4 py-3.5 text-sm leading-6 outline-none transition placeholder:text-slate-600 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
              />

              <p className="mt-2 text-xs text-slate-500">
                Describe the user journey and the expected result.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-5">
              <p className="text-xs text-slate-500">
                Browser actions will run through the backend.
              </p>

              <button
                type="submit"
                disabled={loading}
                className="rounded-xl bg-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-950/40 transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? 'Running test...' : 'Run AI Test →'}
              </button>
            </div>
          </form>
        </section>

        {/* Loading indicator */}
        {loading && (
          <div className="mt-6 rounded-xl border border-violet-500/20 bg-violet-500/10 p-4 text-sm text-violet-300">
            WebTrace is executing the test and retrieving the results...
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Test execution response */}
        {testResult && (
          <section className="mt-6 rounded-2xl border border-white/10 bg-[#0c1a31] p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-lg font-semibold">Test execution response</h3>

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
                  testResult.status === 'completed'
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'bg-amber-500/10 text-amber-300'
                }`}
              >
                {testResult.status}
              </span>
            </div>

            <div className="mt-4 space-y-3 text-sm">
              <p>
                <span className="text-slate-400">Run ID: </span>
                <span className="break-all text-slate-200">
                  {testResult.run_id}
                </span>
              </p>

              <p className="text-slate-300">{testResult.message}</p>
            </div>
          </section>
        )}

        {/* Actual execution results */}
        {executionResults && (
          <section className="mt-6 rounded-2xl border border-white/10 bg-[#0c1a31] p-5 md:p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
                  Test report
                </p>
                <h3 className="mt-2 text-xl font-semibold">
                  Execution Results
                </h3>
              </div>

              <span
                className={`rounded-full px-3 py-1.5 text-sm font-semibold ${
                  executionResults.status === 'completed' && failedCount === 0
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'bg-amber-500/10 text-amber-300'
                }`}
              >
                {executionResults.status}
              </span>
            </div>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              {executionResults.objective}
            </p>

            {/* Summary cards */}
            <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-sm text-slate-400">Total steps</p>
                <p className="mt-2 text-2xl font-bold">{steps.length}</p>
              </div>

              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/[0.05] p-4">
                <p className="text-sm text-slate-400">Passed</p>
                <p className="mt-2 text-2xl font-bold text-emerald-400">
                  {passedCount}
                </p>
              </div>

              <div className="rounded-xl border border-red-500/20 bg-red-500/[0.05] p-4">
                <p className="text-sm text-slate-400">Failed</p>
                <p className="mt-2 text-2xl font-bold text-red-400">
                  {failedCount}
                </p>
              </div>
            </div>

            {/* Individual steps */}
            <div className="mt-7">
              <h4 className="mb-4 text-sm font-semibold text-slate-200">
                Step-by-step execution
              </h4>

              {steps.length > 0 ? (
                <div className="space-y-3">
                  {steps.map((step, index) => {
                    const passed = step.status === 'passed'

                    return (
                      <div
                        key={`${step.name}-${index}`}
                        className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-4"
                      >
                        <span
                          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                            passed
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : 'bg-red-500/10 text-red-400'
                          }`}
                        >
                          {passed ? '✓' : '✕'}
                        </span>

                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-slate-200">
                            {step.name || `Step ${index + 1}`}
                          </p>

                          <p className="mt-1 break-words text-sm leading-6 text-slate-400">
                            {step.message || 'No additional details provided.'}
                          </p>
                        </div>

                        <span
                          className={`shrink-0 text-xs font-semibold uppercase ${
                            passed ? 'text-emerald-400' : 'text-red-400'
                          }`}
                        >
                          {step.status || 'unknown'}
                        </span>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="rounded-xl border border-white/10 p-4 text-sm text-slate-400">
                  No individual step results were returned for this run.
                </p>
              )}
            </div>

            {/* Reported issues */}
            {executionResults.issues?.length > 0 && (
              <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4">
                <h4 className="font-semibold text-red-300">Issues found</h4>

                {executionResults.issues.map((issue, index) => (
                  <p
                    key={index}
                    className="mt-2 break-words text-sm leading-6 text-red-200"
                  >
                    {typeof issue === 'string'
                      ? issue
                      : JSON.stringify(issue)}
                  </p>
                ))}
              </div>
            )}

            {executionResults.issues?.length === 0 && (
              <p className="mt-5 text-sm text-emerald-400">
                ✓ No issues reported by the backend.
              </p>
            )}
          </section>
        )}

        {/* Empty state: shown before results are available */}
        {!executionResults && !loading && (
          <section className="mt-8 rounded-2xl border border-dashed border-white/15 bg-white/[0.02] p-8 text-center md:p-12">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-400/20 bg-violet-500/10 text-2xl text-violet-300">
              ◈
            </div>

            <h3 className="mt-5 text-lg font-semibold">
              Your test results will appear here
            </h3>

            <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-400">
              Run a test to see the actual execution status, passed and failed
              steps, and any reported issues.
            </p>

            <p className="mt-3 text-xs text-slate-500">
              No results to display yet
            </p>
          </section>
        )}

        <footer className="pb-4 pt-8 text-center text-xs text-slate-600">
          WebTrace · Autonomous AI QA Engineer
        </footer>
      </main>
    </div>
  )
}

export default App

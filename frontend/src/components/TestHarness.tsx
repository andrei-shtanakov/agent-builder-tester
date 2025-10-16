import { useState } from "react";

interface TestHarnessProps {
  agentName: string;
  config: Record<string, unknown>;
}

interface TestResult {
  success: boolean;
  response?: string;
  error?: string;
  config_valid?: boolean;
  system_message_length?: number;
}

export function TestHarness({ agentName, config }: TestHarnessProps): JSX.Element {
  const [testInput, setTestInput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<TestResult | null>(null);

  const handleTest = () => {
    setIsRunning(true);
    setResult(null);

    // Simulate test execution
    setTimeout(() => {
      const systemMessage = config.system_message as string || "";
      const hasValidConfig = systemMessage.length > 0;

      setResult({
        success: hasValidConfig,
        response: hasValidConfig
          ? `Test completed successfully for agent "${agentName}"`
          : undefined,
        error: hasValidConfig
          ? undefined
          : "Agent has no system message configured",
        config_valid: hasValidConfig,
        system_message_length: systemMessage.length,
      });
      setIsRunning(false);
    }, 1500);
  };

  const getStatusColor = () => {
    if (!result) return "";
    return result.success ? "test-harness__result--success" : "test-harness__result--error";
  };

  return (
    <div className="test-harness">
      <div className="test-harness__info">
        <p>
          Test your agent configuration before creating it. This will validate the
          system prompt and configuration.
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="test-input">Test Input</label>
        <textarea
          id="test-input"
          value={testInput}
          onChange={(e) => setTestInput(e.target.value)}
          placeholder="Enter a test message..."
          rows={4}
        />
      </div>

      <button
        type="button"
        className="button button--secondary"
        onClick={handleTest}
        disabled={isRunning || !testInput.trim()}
      >
        {isRunning ? "Running Test..." : "Run Test"}
      </button>

      {result && (
        <div className={`test-harness__result ${getStatusColor()}`}>
          <h4>Test Result</h4>
          {result.success ? (
            <div className="test-harness__success">
              <p className="test-harness__message">{result.response}</p>
              <div className="test-harness__details">
                <div className="test-harness__detail">
                  <span className="test-harness__detail-label">Config Valid:</span>
                  <span className="test-harness__detail-value">
                    {result.config_valid ? "Yes" : "No"}
                  </span>
                </div>
                <div className="test-harness__detail">
                  <span className="test-harness__detail-label">
                    System Message Length:
                  </span>
                  <span className="test-harness__detail-value">
                    {result.system_message_length} characters
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="test-harness__error">
              <p className="test-harness__message">Error: {result.error}</p>
            </div>
          )}
        </div>
      )}

      <div className="test-harness__config-preview">
        <h4>Configuration Preview</h4>
        <pre className="test-harness__config-code">
          {JSON.stringify(config, null, 2)}
        </pre>
      </div>
    </div>
  );
}


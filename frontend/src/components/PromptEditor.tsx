import { useState } from "react";

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export function PromptEditor({ value, onChange }: PromptEditorProps): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const insertVariable = (variable: string) => {
    const textarea = document.querySelector<HTMLTextAreaElement>(
      ".prompt-editor__textarea"
    );
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = value;
    const before = text.substring(0, start);
    const after = text.substring(end);
    const newValue = before + `{${variable}}` + after;

    onChange(newValue);

    // Set cursor position after inserted variable
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + variable.length + 2,
        start + variable.length + 2
      );
    }, 0);
  };

  const variables = [
    { name: "user_name", description: "Current user's name" },
    { name: "date", description: "Current date" },
    { name: "time", description: "Current time" },
    { name: "context", description: "Additional context" },
  ];

  return (
    <div className="prompt-editor">
      <div className="prompt-editor__toolbar">
        <button
          type="button"
          className="button button--small"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? "Collapse" : "Expand"}
        </button>
        <div className="prompt-editor__variables">
          <span className="prompt-editor__label">Insert Variable:</span>
          {variables.map((variable) => (
            <button
              key={variable.name}
              type="button"
              className="button button--small button--ghost"
              onClick={() => insertVariable(variable.name)}
              title={variable.description}
            >
              {`{${variable.name}}`}
            </button>
          ))}
        </div>
      </div>

      <textarea
        className="prompt-editor__textarea"
        value={value}
        onChange={handleChange}
        rows={isExpanded ? 20 : 10}
        placeholder="Enter system prompt here..."
      />

      <div className="prompt-editor__info">
        <span>Characters: {value.length}</span>
        <span>Lines: {value.split("\n").length}</span>
      </div>
    </div>
  );
}


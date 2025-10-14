import { FormEvent, useState } from "react";

interface TokenInputProps {
  token: string | null;
  onSave: (token: string) => void;
  onClear: () => void;
}

export function TokenInput({ token, onSave, onClear }: TokenInputProps): JSX.Element {
  const [draft, setDraft] = useState<string>(token ?? "");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = draft.trim();
    if (trimmed.length > 0) {
      onSave(trimmed);
    }
  };

  return (
    <form className="token-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span className="form-label">API Token</span>
        <input
          className="form-input"
          type="password"
          inputMode="text"
          autoComplete="off"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Paste bearer token"
        />
      </label>
      <div className="token-form__actions">
        <button className="button button--primary" type="submit" disabled={draft.trim().length === 0}>
          Save
        </button>
        <button
          className="button button--ghost"
          type="button"
          onClick={() => {
            setDraft("");
            onClear();
          }}
          disabled={!token}
        >
          Clear
        </button>
      </div>
    </form>
  );
}

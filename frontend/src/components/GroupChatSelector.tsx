import type { GroupChat } from "../api/types";

interface GroupChatSelectorProps {
  groupChats: GroupChat[] | undefined;
  selectedId: string | null;
  onChange: (groupChatId: string | null) => void;
  disabled?: boolean;
}

export function GroupChatSelector(
  props: GroupChatSelectorProps,
): JSX.Element {
  const { groupChats, selectedId, onChange, disabled } = props;

  return (
    <label className="form-field">
      <span className="form-label">Group Chat</span>
      <select
        className="form-select"
        value={selectedId ?? ""}
        onChange={(event) => {
          const value = event.target.value;
          onChange(value.length > 0 ? value : null);
        }}
        disabled={disabled}
      >
        <option value="">Select a group chat</option>
        {(groupChats ?? []).map((groupChat) => (
          <option key={groupChat.id} value={groupChat.id}>
            {groupChat.title} · {groupChat.participants.length} participants
          </option>
        ))}
      </select>
    </label>
  );
}

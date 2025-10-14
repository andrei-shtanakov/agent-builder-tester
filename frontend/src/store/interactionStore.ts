import { create } from "zustand";

interface InteractionState {
  selectedGroupChatId: string | null;
  selectGroupChat: (groupChatId: string | null) => void;
}

export const useInteractionStore = create<InteractionState>((set) => ({
  selectedGroupChatId: null,
  selectGroupChat: (groupChatId) => set({ selectedGroupChatId: groupChatId }),
}));

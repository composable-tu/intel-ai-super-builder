import { create } from "zustand";

const useAppStore = create((set, get) => ({
  notification: null,
  // Notification actions
  showNotification: (message, type = "info", timeout = null) =>
    set({
      notification: { message, type, timestamp: Date.now(), timeout },
    }),
  clearNotification: () => set({ notification: null }),
}));

export default useAppStore;

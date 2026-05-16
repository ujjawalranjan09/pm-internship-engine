import { create } from "zustand";

interface AdminStore {
  sidebarOpen: boolean;
  selectedCycleId: string | null;
  activeTab: string;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setSelectedCycleId: (id: string | null) => void;
  setActiveTab: (tab: string) => void;
}

export const useAdminStore = create<AdminStore>()((set) => ({
  sidebarOpen: true,
  selectedCycleId: null,
  activeTab: "overview",

  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  setSelectedCycleId: (selectedCycleId) => set({ selectedCycleId }),

  setActiveTab: (activeTab) => set({ activeTab }),
}));

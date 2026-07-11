import { create } from "zustand";

interface FilterState {
  sector: string;
  state: string;
  district: string;
  skills: string[];
  searchQuery: string;
  minStipend: number | null;
  maxStipend: number | null;
  isActive: boolean | null;
  setSector: (sector: string) => void;
  setState: (state: string) => void;
  setDistrict: (district: string) => void;
  setSkills: (skills: string[]) => void;
  toggleSkill: (skill: string) => void;
  setSearchQuery: (query: string) => void;
  setStipendRange: (min: number | null, max: number | null) => void;
  setIsActive: (active: boolean | null) => void;
  resetFilters: () => void;
}

const initialState = {
  sector: "",
  state: "",
  district: "",
  skills: [],
  searchQuery: "",
  minStipend: null,
  maxStipend: null,
  isActive: null,
};

export const useFilterStore = create<FilterState>()((set) => ({
  ...initialState,

  setSector: (sector) => set({ sector }),

  setState: (state) => set({ state, district: "" }),

  setDistrict: (district) => set({ district }),

  setSkills: (skills) => set({ skills }),

  toggleSkill: (skill) =>
    set((s) => ({
      skills: s.skills.includes(skill)
        ? s.skills.filter((sk) => sk !== skill)
        : [...s.skills, skill],
    })),

  setSearchQuery: (searchQuery) => set({ searchQuery }),

  setStipendRange: (min, max) => set({ minStipend: min, maxStipend: max }),

  setIsActive: (isActive) => set({ isActive }),

  resetFilters: () => set(initialState),
}));

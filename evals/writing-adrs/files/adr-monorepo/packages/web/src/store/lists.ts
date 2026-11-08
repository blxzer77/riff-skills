import { create } from "zustand";

type ListsState = { lists: string[]; add: (name: string) => void };

export const useLists = create<ListsState>((set) => ({
  lists: [],
  add: (name) => set((s) => ({ lists: [...s.lists, name] })),
}));

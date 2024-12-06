import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SocialAccount, SocialAccountStore } from '../types/social';

export const useSocialStore = create<SocialAccountStore>()(
  persist(
    (set) => ({
      accounts: [],
      addAccount: (account) =>
        set((state) => ({
          accounts: [...state.accounts.filter((a) => a.platform !== account.platform), account],
        })),
      removeAccount: (platform) =>
        set((state) => ({
          accounts: state.accounts.filter((account) => account.platform !== platform),
        })),
      updateAccount: (platform, data) =>
        set((state) => ({
          accounts: state.accounts.map((account) =>
            account.platform === platform ? { ...account, ...data } : account
          ),
        })),
    }),
    {
      name: 'social-accounts',
    }
  )
);
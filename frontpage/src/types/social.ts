export interface SocialAccount {
  id: string;
  platform: 'youtube' | 'instagram' | 'tiktok';
  username: string;
  profileUrl: string;
  avatarUrl?: string;
  stats: {
    followers: number;
    posts: number;
    engagement?: number;
  };
  connected: boolean;
  lastSync?: string;
}

export interface SocialAccountStore {
  accounts: SocialAccount[];
  addAccount: (account: SocialAccount) => void;
  removeAccount: (platform: string) => void;
  updateAccount: (platform: string, data: Partial<SocialAccount>) => void;
}
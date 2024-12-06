import React from 'react';
import { Youtube, Instagram, GithubIcon } from 'lucide-react';
import { useSocialStore } from '../store/socialStore';

const platforms = [
  {
    name: 'YouTube',
    icon: Youtube,
    color: 'bg-red-600',
    hoverColor: 'hover:bg-red-700',
  },
  {
    name: 'Instagram',
    icon: Instagram,
    color: 'bg-pink-600',
    hoverColor: 'hover:bg-pink-700',
  },
  {
    name: 'TikTok',
    icon: GithubIcon, // Using a temporary icon as TikTok isn't available in lucide-react
    color: 'bg-black',
    hoverColor: 'hover:bg-gray-900',
  },
];

export function SocialConnect() {
  const { accounts, addAccount } = useSocialStore();

  const handleConnect = (platform: string) => {
    // Simulate connecting to social media
    const mockAccount = {
      id: Math.random().toString(36).substr(2, 9),
      platform: platform.toLowerCase() as 'youtube' | 'instagram' | 'tiktok',
      username: `demo_${platform.toLowerCase()}`,
      profileUrl: `https://${platform.toLowerCase()}.com/demo`,
      avatarUrl: `https://api.dicebear.com/7.x/avatars/svg?seed=${platform}`,
      stats: {
        followers: Math.floor(Math.random() * 10000),
        posts: Math.floor(Math.random() * 100),
        engagement: Math.random() * 5,
      },
      connected: true,
      lastSync: new Date().toISOString(),
    };
    addAccount(mockAccount);
  };

  return (
    <div id="connect" className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:text-center mb-12">
          <h2 className="text-base text-indigo-600 font-semibold tracking-wide uppercase">
            Connect Your Accounts
          </h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Sync Your Social Media
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Connect your social media accounts to get personalized content suggestions
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          {platforms.map((platform) => {
            const isConnected = accounts.some(
              (account) => account.platform === platform.name.toLowerCase()
            );

            return (
              <div
                key={platform.name}
                className="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
              >
                <div className="flex items-center">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-md ${platform.color} text-white`}
                  >
                    <platform.icon className="h-6 w-6" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">{platform.name}</h3>
                    <p className="text-sm text-gray-500">
                      {isConnected ? 'Connected' : 'Not connected'}
                    </p>
                  </div>
                </div>
                <div className="mt-4">
                  <button
                    onClick={() => handleConnect(platform.name)}
                    disabled={isConnected}
                    className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                      isConnected
                        ? 'bg-gray-400 cursor-not-allowed'
                        : `${platform.color} ${platform.hoverColor}`
                    } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                  >
                    {isConnected ? 'Connected' : 'Connect'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
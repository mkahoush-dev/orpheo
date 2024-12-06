import React from 'react';
import { useSocialStore } from '../store/socialStore';
import { Users, Video, BarChart3 } from 'lucide-react';

export function AccountStats() {
  const { accounts } = useSocialStore();

  if (accounts.length === 0) {
    return null;
  }

  return (
    <div className="bg-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Connected Accounts</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {accounts.map((account) => (
            <div
              key={account.platform}
              className="bg-white overflow-hidden shadow rounded-lg border border-gray-200"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <img
                    className="h-10 w-10 rounded-full"
                    src={account.avatarUrl}
                    alt={`${account.username} avatar`}
                  />
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900 capitalize">
                      {account.platform}
                    </h3>
                    <p className="text-sm text-gray-500">@{account.username}</p>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <div className="flex flex-col">
                    <div className="flex items-center text-sm font-medium text-gray-500">
                      <Users className="h-4 w-4 mr-1" />
                      Followers
                    </div>
                    <span className="text-lg font-semibold text-gray-900">
                      {account.stats.followers.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <div className="flex items-center text-sm font-medium text-gray-500">
                      <Video className="h-4 w-4 mr-1" />
                      Posts
                    </div>
                    <span className="text-lg font-semibold text-gray-900">
                      {account.stats.posts.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <div className="flex items-center text-sm font-medium text-gray-500">
                      <BarChart3 className="h-4 w-4 mr-1" />
                      Engagement
                    </div>
                    <span className="text-lg font-semibold text-gray-900">
                      {account.stats.engagement?.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
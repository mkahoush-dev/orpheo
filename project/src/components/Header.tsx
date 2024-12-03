import React from 'react';
import { Menu, MessageSquarePlus, User } from 'lucide-react';

export function Header() {
  return (
    <header className="fixed top-0 w-full bg-white shadow-sm z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Menu className="h-6 w-6 text-gray-600 sm:hidden" />
            <h1 className="ml-4 text-xl font-bold text-gray-900">ContentMind</h1>
          </div>
          <nav className="hidden sm:flex space-x-8">
            <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-gray-900">How it Works</a>
            <a href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</a>
          </nav>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-600 hover:text-gray-900">
              <MessageSquarePlus className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900">
              <User className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
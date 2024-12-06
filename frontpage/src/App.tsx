import React from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { Features } from './components/Features';
import { SocialConnect } from './components/SocialConnect';
import { AccountStats } from './components/AccountStats';

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <Hero />
      <Features />
      <SocialConnect />
      <AccountStats />
    </div>
  );
}

export default App;
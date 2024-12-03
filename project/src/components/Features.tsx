import React from 'react';
import { Brain, Sparkles, TrendingUp, Users, MessageSquare, Clock } from 'lucide-react';

const features = [
  {
    name: 'AI-Powered Analysis',
    description: 'Advanced algorithms analyze your content performance and audience engagement.',
    icon: Brain,
  },
  {
    name: 'Smart Suggestions',
    description: 'Get personalized content ideas based on your style and audience preferences.',
    icon: Sparkles,
  },
  {
    name: 'Engagement Tracking',
    description: 'Monitor and optimize your content performance across platforms.',
    icon: TrendingUp,
  },
  {
    name: 'Audience Insights',
    description: 'Understand your audience demographics and behavior patterns.',
    icon: Users,
  },
  {
    name: 'Interactive Chat',
    description: 'Brainstorm ideas and get instant feedback from your AI assistant.',
    icon: MessageSquare,
  },
  {
    name: 'Schedule Manager',
    description: 'Plan and schedule your content with an intelligent calendar.',
    icon: Clock,
  },
];

export function Features() {
  return (
    <div id="features" className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:text-center">
          <h2 className="text-base text-indigo-600 font-semibold tracking-wide uppercase">Features</h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to create amazing content
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Powerful tools and insights to streamline your content creation workflow.
          </p>
        </div>

        <div className="mt-10">
          <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            {features.map((feature) => (
              <div key={feature.name} className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                  <feature.icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">{feature.name}</p>
                <p className="mt-2 ml-16 text-base text-gray-500">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
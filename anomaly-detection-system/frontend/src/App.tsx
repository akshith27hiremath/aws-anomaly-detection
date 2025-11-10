import { useState } from "react";
import { LandingPage } from "./components/LandingPage";
import { Dashboard } from "./components/Dashboard";
import { FloatingShapes } from "./components/FloatingShapes";

export default function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900" />
      
      {/* Floating shapes in background */}
      <FloatingShapes />
      
      {/* Main content */}
      <div className="relative z-10">
        {!showDashboard ? (
          <LandingPage onExplore={() => setShowDashboard(true)} />
        ) : (
          <Dashboard onBack={() => setShowDashboard(false)} />
        )}
      </div>
    </div>
  );
}

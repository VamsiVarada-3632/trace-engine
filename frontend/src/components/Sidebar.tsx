"use client";

import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FileWarning,
  Brain,
  Database,
  Settings,
} from "lucide-react";

type View = "dashboard" | "report" | "analysis" | "memory";

interface SidebarProps {
  currentView: View;
  onNavigate: (view: View) => void;
}

const navItems = [
  { id: "dashboard" as View, label: "Dashboard", icon: LayoutDashboard },
  { id: "report" as View, label: "Report Incident", icon: FileWarning },
  { id: "memory" as View, label: "Machine Memory", icon: Database },
];

export function Sidebar({ currentView, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 bg-industrial-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-industrial-700">
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-industrial-400" />
          <div>
            <h1 className="text-xl font-bold">TRACE</h1>
            <p className="text-xs text-industrial-400">
              Adaptive Context Engine
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <li key={item.id}>
                <button
                  onClick={() => onNavigate(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                    isActive
                      ? "bg-industrial-700 text-white"
                      : "text-industrial-300 hover:bg-industrial-800 hover:text-white"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-industrial-700">
        <p className="text-xs text-industrial-500 text-center">
          Powered by Hindsight Memory
        </p>
      </div>
    </aside>
  );
}

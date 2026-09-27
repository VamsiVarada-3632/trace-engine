"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Dashboard } from "@/components/Dashboard";
import { ReportIncident } from "@/components/ReportIncident";
import { IncidentAnalysis } from "@/components/IncidentAnalysis";
import { MachineMemory } from "@/components/MachineMemory";
import type { AnalysisResult } from "@/types/incident";

type View = "dashboard" | "report" | "analysis" | "memory";

export default function Home() {
  const [currentView, setCurrentView] = useState<View>("dashboard");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [selectedMachineId, setSelectedMachineId] = useState<string>("");

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result);
    setCurrentView("analysis");
  };

  const handleViewMachineMemory = (machineId: string) => {
    setSelectedMachineId(machineId);
    setCurrentView("memory");
  };

  const renderContent = () => {
    switch (currentView) {
      case "dashboard":
        return (
          <Dashboard
            onReportIncident={() => setCurrentView("report")}
            onViewMachineMemory={handleViewMachineMemory}
          />
        );
      case "report":
        return (
          <ReportIncident
            onAnalysisComplete={handleAnalysisComplete}
            onCancel={() => setCurrentView("dashboard")}
          />
        );
      case "analysis":
        return analysisResult ? (
          <IncidentAnalysis
            result={analysisResult}
            onBack={() => setCurrentView("dashboard")}
            onViewMachineMemory={handleViewMachineMemory}
          />
        ) : (
          <Dashboard
            onReportIncident={() => setCurrentView("report")}
            onViewMachineMemory={handleViewMachineMemory}
          />
        );
      case "memory":
        return (
          <MachineMemory
            machineId={selectedMachineId}
            onBack={() => setCurrentView("dashboard")}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar currentView={currentView} onNavigate={setCurrentView} />
      <main className="flex-1 p-8">{renderContent()}</main>
    </div>
  );
}

"use client";

import type { AnalysisResult } from "@/types/incident";

interface Props {
  result: AnalysisResult;
  onBack: () => void;
  onViewMachineMemory: (machineId: string) => void;
}

export function IncidentAnalysis({ result, onBack }: Props) {
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Incident Analysis</h2>
      <p className="text-gray-600">Analysis component - to be implemented</p>
      <button onClick={onBack} className="mt-4 px-4 py-2 bg-gray-200 rounded">
        Back
      </button>
    </div>
  );
}

"use client";

interface Props {
  machineId: string;
  onBack: () => void;
}

export function MachineMemory({ machineId, onBack }: Props) {
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Machine Memory: {machineId}</h2>
      <p className="text-gray-600">Machine memory component - to be implemented</p>
      <button onClick={onBack} className="mt-4 px-4 py-2 bg-gray-200 rounded">
        Back
      </button>
    </div>
  );
}

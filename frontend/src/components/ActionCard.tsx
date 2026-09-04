import React from 'react';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export interface Action {
  id: string;
  title: string;
  description: string;
  confidence: number;
  requiresApproval: boolean;
}

interface ActionCardProps {
  action: Action;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export default function ActionCard({ action, onApprove, onReject }: ActionCardProps) {
  return (
    <div className="my-2 max-w-sm rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-start justify-between">
        <h4 className="font-semibold text-gray-900">{action.title}</h4>
        {action.confidence && (
          <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
            {Math.round(action.confidence * 100)}% Match
          </span>
        )}
      </div>
      
      <p className="mb-4 text-sm text-gray-600">{action.description}</p>
      
      {action.requiresApproval ? (
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(action.id)}
            className="flex flex-1 items-center justify-center gap-1 rounded-lg bg-blue-600 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            <CheckCircle className="h-4 w-4" />
            Approve
          </button>
          <button
            onClick={() => onReject(action.id)}
            className="flex flex-1 items-center justify-center gap-1 rounded-lg border border-gray-300 bg-white py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <XCircle className="h-4 w-4 text-gray-500" />
            Reject
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-lg bg-blue-50 p-2 text-sm text-blue-700">
          <AlertCircle className="h-4 w-4" />
          Executed automatically
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Settings, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  due_date: string;
}

export default function Operations() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/operations/tasks');
        setTasks(response.data.tasks || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load operations tasks');
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-50/50">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-lg bg-red-50 p-4 text-red-600">
          <h3 className="font-semibold text-red-800">Error loading tasks</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const highPriority = tasks.filter(t => t.priority === 'High').length;

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Operations</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor internal tasks, workflows, and operational metrics.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-blue-50 p-8">
            <Clock className="h-8 w-8 text-blue-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">Active Tasks</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
              {tasks.length}
            </dd>
          </div>
        </div>
        <div className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <div className="absolute -right-4 -top-4 rounded-full bg-red-50 p-8">
            <AlertCircle className="h-8 w-8 text-red-500/50" />
          </div>
          <div className="relative">
            <dt className="truncate text-sm font-medium text-gray-500">High Priority</dt>
            <dd className="mt-2 text-3xl font-bold tracking-tight text-red-600">
              {highPriority}
            </dd>
          </div>
        </div>
      </div>

      <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200 overflow-hidden">
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Settings className="h-5 w-5 text-gray-500" />
            Workflow Tasks
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {task.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      task.priority === 'High' ? 'bg-red-100 text-red-800' : 
                      task.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {task.priority || 'Normal'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {task.status || 'Pending'}
                  </td>
                </tr>
              ))}
              {tasks.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                    No active tasks.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { CheckSquare, ShieldAlert, ArrowRight, Clock } from 'lucide-react';
import { NavLink } from 'react-router';

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
}

interface Approval {
  id: string;
  action_type: string;
  status: string;
  created_at: string;
}

export default function WorkInbox() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInbox = async () => {
      try {
        const [tasksRes, approvalsRes] = await Promise.all([
          api.get('/operations/tasks'),
          api.get('/approvals/pending')
        ]);
        setTasks(tasksRes.data.tasks || []);
        setApprovals(approvalsRes.data.approvals || []);
      } catch (err) {
        console.error('Failed to load inbox data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInbox();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-50/50">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const pendingTasks = tasks.filter(t => t.status !== 'Completed');

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Work Inbox</h1>
        <p className="mt-1 text-sm text-gray-500">
          Your unified dashboard for tasks and pending approvals.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Approvals Section */}
        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200 flex flex-col">
          <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-orange-500" />
              Action Required ({approvals.length})
            </h2>
            <NavLink to="/app/approvals" className="text-sm font-medium text-blue-600 hover:text-blue-500 flex items-center gap-1">
              View all <ArrowRight className="h-4 w-4" />
            </NavLink>
          </div>
          <div className="flex-1 p-6">
            {approvals.length > 0 ? (
              <div className="space-y-4">
                {approvals.slice(0, 3).map(app => (
                  <div key={app.id} className="flex items-start gap-4 p-4 rounded-lg border border-gray-100 bg-gray-50/50">
                    <div className="mt-1"><ShieldAlert className="h-5 w-5 text-orange-600" /></div>
                    <div>
                      <p className="font-medium text-gray-900">{app.action_type}</p>
                      <p className="text-sm text-gray-500 mt-1">{new Date(app.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckSquare className="mx-auto h-12 w-12 text-gray-300" />
                <h3 className="mt-2 text-sm font-semibold text-gray-900">All caught up!</h3>
                <p className="text-sm text-gray-500">No pending approvals require your attention.</p>
              </div>
            )}
          </div>
        </div>

        {/* Tasks Section */}
        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200 flex flex-col">
          <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-500" />
              Active Tasks ({pendingTasks.length})
            </h2>
            <NavLink to="/app/operations" className="text-sm font-medium text-blue-600 hover:text-blue-500 flex items-center gap-1">
              View all <ArrowRight className="h-4 w-4" />
            </NavLink>
          </div>
          <div className="flex-1 p-6">
            {pendingTasks.length > 0 ? (
              <div className="space-y-4">
                {pendingTasks.slice(0, 4).map(task => (
                  <div key={task.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-100">
                    <div className="flex items-center gap-3">
                      <input type="checkbox" className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600" />
                      <span className="font-medium text-gray-900 text-sm">{task.title}</span>
                    </div>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      task.priority === 'High' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckSquare className="mx-auto h-12 w-12 text-gray-300" />
                <h3 className="mt-2 text-sm font-semibold text-gray-900">Inbox Zero</h3>
                <p className="text-sm text-gray-500">No active tasks found.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

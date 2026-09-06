import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

const formatTimeOnly = (isoString) => {
  if (!isoString) return null;
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return String(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (_) {
    return String(isoString);
  }
};

const formatStatus = (status) => {
  const s = String(status || '').toUpperCase();
  if (s === 'PRESENT') return 'Present';
  if (s === 'ABSENT') return 'Absent';
  if (s === 'LATE') return 'Late';
  if (s === 'HALF_DAY') return 'Half Day';
  if (s === 'ON_LEAVE') return 'On Leave';
  if (s === 'MISSING_CHECKOUT') return 'Missing Checkout';
  return status || 'Present';
};

export const normalizeAttendance = (item, employeeMap) => {
  if (!item) return null;
  const emp = employeeMap?.get(String(item.employee_id));
  const empName = emp?.name || item.employee_name || (item.employee_id ? `Employee ${String(item.employee_id).slice(0, 8)}` : 'Employee');
  const worked = Number(item.worked_hours ?? 0);
  const overtime = Number(item.overtime_hours ?? 0);

  return {
    ...item,
    id: item.id,
    employeeId: item.employee_id,
    employeeName: empName,
    date: item.work_date || (item.check_in ? String(item.check_in).slice(0, 10) : ''),
    checkIn: formatTimeOnly(item.check_in),
    checkOut: formatTimeOnly(item.check_out),
    rawCheckIn: item.check_in,
    rawCheckOut: item.check_out,
    workedHours: worked,
    overtimeHours: overtime,
    status: formatStatus(item.status),
    rawStatus: item.status || 'PRESENT',
    isManualCorrection: Boolean(item.is_manual_correction),
    correctionReason: item.correction_reason || null,
  };
};

export const normalizeAttendanceDetail = (data, empInfo) => {
  if (!data) return null;
  const empMap = empInfo ? new Map([[String(data.employee_id), empInfo]]) : undefined;
  const base = normalizeAttendance(data, empMap);
  return {
    ...base,
    department: empInfo?.department || data.department || 'General',
    manager: empInfo?.manager || data.manager || 'None',
    notes: data.correction_reason || (data.is_manual_correction ? 'Manually corrected record' : 'Standard session'),
  };
};

export const useAttendanceQuery = (employeeId) => useQuery({
  queryKey: ['attendance', 'list', employeeId],
  queryFn: async () => {
    const [attRes, empRes] = await Promise.all([
      httpClient.get('/attendance/', {
        params: employeeId ? { employee_id: employeeId } : undefined,
      }),
      httpClient.get('/employees/').catch(() => ({ data: [] })),
    ]);

    const employeeMap = new Map();
    (empRes.data || []).forEach((e) => {
      const name = [e.first_name, e.last_name].filter(Boolean).join(' ').trim() || e.name || e.employee_code;
      employeeMap.set(String(e.id), {
        name,
        department: e.department_name || 'General',
        manager: e.manager_name || 'None',
      });
    });

    const records = Array.isArray(attRes.data) ? attRes.data : [];
    return records.map((record) => normalizeAttendance(record, employeeMap));
  },
});

export const useAttendanceDetailQuery = (id) => useQuery({
  queryKey: ['attendance', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/attendance/${id}`);
    let empInfo = null;
    if (data.employee_id) {
      try {
        const empRes = await httpClient.get(`/employees/${data.employee_id}`);
        const e = empRes.data;
        empInfo = {
          name: [e.first_name, e.last_name].filter(Boolean).join(' ').trim() || e.employee_code,
          department: e.department_name || 'General',
          manager: e.manager_name || 'None',
        };
      } catch (_) {
        empInfo = null;
      }
    }
    return normalizeAttendanceDetail(data, empInfo);
  },
  enabled: Boolean(id),
});

export const useCorrectAttendance = (id) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ check_in, check_out, reason }) => {
      const { data } = await httpClient.patch(`/attendance/${id}`, {
        check_in: check_in || null,
        check_out: check_out || null,
        reason: reason || 'Manual correction',
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance'] });
    },
  });
};

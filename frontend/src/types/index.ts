export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  student_id?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

export interface StudentsResponse {
  students: User[];
  count: number;
}

export interface AttendanceRow {
  student_id: number;
  student_student_id: string;
  name: string;
  email: string;
  status: string;
  record_id?: number;
}

export interface AttendanceResponse {
  date: string;
  class_id?: number;
  class_name?: string;
  attendance: AttendanceRow[];
  count: number;
}

export interface Class {
  id: number;
  name: string;
  description?: string;
  teacher_id: number;
  teacher_name?: string;
  student_count: number;
  is_active: boolean;
}

export interface Assignment {
  id: number;
  name: string;
  description?: string;
  class_id: number;
  class_name?: string;
  max_points: number;
  due_date?: string;
  assignment_type: string;
}

export interface Grade {
  id: number;
  student_id: number;
  assignment_id: number;
  student_name?: string;
  student_student_id?: string;
  assignment_name?: string;
  assignment_max_points?: number;
  points_earned?: number;
  percentage?: number;
  letter_grade?: string;
  comments?: string;
}

export interface GradesResponse {
  class: Class;
  assignments: Assignment[];
  students: Array<{
    id: number;
    name: string;
    student_id: string;
    grades: { [assignment_id: number]: Grade };
  }>;
  grades: { [student_id: number]: { [assignment_id: number]: Grade } };
}

export interface DashboardProps {
  currentUser: User;
  onLogout: () => void;
} 
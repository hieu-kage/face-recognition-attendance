// src/pages/CourseDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './CourseDetailPage.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function EnrollmentUploader({ courseId, courseName, onSuccess }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Vui lòng chọn file.');
      return;
    }

    setIsUploading(true);
    setMessage('Đang xử lý file...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', courseId);

    try {
      const response = await axios.post(`${API_URL}/enrollments/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(response.data.message);
      setFile(null);
      if (onSuccess) onSuccess();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Lỗi: Không thể xử lý file.');
    }

    setIsUploading(false);
  };

  return (
    <div className="detail-card enrollment-card">
      <div className="card-header">
        <h2> Ghi danh hàng loạt</h2>
        <p className="card-subtitle">Upload file CSV/Excel để ghi danh nhiều sinh viên cùng lúc</p>
      </div>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-wrapper">
          <input
            type="file"
            id="file-upload"
            onChange={(e) => setFile(e.target.files[0])}
            accept=".csv,.xlsx,.xls,image/*"
            required
          />
          <label htmlFor="file-upload" className="file-label">
            <span className="file-text">
              {file ? file.name : 'Chọn file CSV hoặc Excel'}
            </span>
          </label>
        </div>

        <button type="submit" className="btn btn-primary" disabled={isUploading}>
          {isUploading ? (
            <>
              <span className="spinner"></span>
              Đang xử lý...
            </>
          ) : (
            <>
              <span>⚡</span>
              Bắt đầu Ghi danh
            </>
          )}
        </button>
      </form>

      {message && (
        <div className={`message ${message.includes('Lỗi') ? 'message-error' : 'message-success'}`}>
          {message}
        </div>
      )}
    </div>
  );
}


function StudentList({ courseId, refreshTrigger }) {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);

  // Mặc định là chuỗi rỗng '' để hiển thị ALL ngay từ đầu
  const [searchTerm, setSearchTerm] = useState('');

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/enrollments/search`, {
        course_id: parseInt(courseId),
        page: 1,
        page_size: 1000,
        student_name: searchTerm
      });

      setStudents(response.data.data || []);
    } catch (err) {
      console.error('Lỗi khi tải danh sách sinh viên:', err);
    }
    setLoading(false);
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchStudents();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [courseId, refreshTrigger, searchTerm]);

  const getProgressColor = (rate) => {
    if (rate >= 80) return '#10b981';
    if (rate >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="detail-card student-list-card">
      <div className="card-header">
        <div className="header-row">
            <h2>Danh sách Sinh viên</h2>
            <span className="student-count">{students.length} sinh viên</span>
        </div>

        <div className="search-container">
            <input
                type="text"
                className="search-input"
                placeholder="🔍 Tìm theo tên hoặc MSSV..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
        </div>
      </div>

      {loading ? (
         <div className="loading-state" style={{padding: '40px'}}><div className="spinner"></div></div>
      ) : students.length === 0 ? (
        <div className="empty-state"><p>Lớp học này chưa có sinh viên nào.</p></div>
      ) : (
        <div className="student-list-vertical">
          {students.map((student) => (
            <div key={student.enrollment_id} className="student-row">
              <div className="student-basic-info">
                <div className="student-avatar-small">
                  {(student.student_name || "U").charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="student-name-text">{student.student_name}</div>
                  <div className="student-code-text">{student.student_id}</div>
                </div>
              </div>

              <div className="student-progress-section">
                <div className="progress-info">
                  <span className="progress-label">Tiến độ:</span>
                  <span className="progress-fraction">
                    {student.attended_count}/{student.total_sessions} buổi
                  </span>
                  <span className="progress-percent" style={{color: getProgressColor(student.attendance_rate)}}>
                    {student.attendance_rate}%
                  </span>
                </div>
                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{
                      width: `${student.attendance_rate}%`,
                      backgroundColor: getProgressColor(student.attendance_rate)
                    }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AddStudentForm({ courseId, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    student_id: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');

    try {
      await axios.post(`${API_URL}/enrollments/${courseId}/students`, formData);
      setMessage(' Thêm sinh viên thành công!');
      setFormData({ name: '', student_id: '' });
      if (onSuccess) onSuccess();
    } catch (err) {
      setMessage(err.response?.data?.detail || ' Lỗi: Không thể thêm sinh viên.');
    }

    setIsSubmitting(false);
  };

  return (
    <div className="detail-card add-student-card">
      <div className="card-header">
        <h2>Thêm Sinh viên</h2>
        <p className="card-subtitle">Ghi danh sinh viên thủ công vào lớp học</p>
      </div>

      <form onSubmit={handleSubmit} className="add-student-form">
        <div className="form-group">
          <label htmlFor="name">Họ và tên *</label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="Nguyễn Văn A"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="student_id">Mã sinh viên *</label>
          <input
            type="text"
            id="student_id"
            value={formData.student_id}
            onChange={(e) => setFormData({...formData, student_id: e.target.value})}
            placeholder="SV001"
            required
          />
        </div>
        <button type="submit" className="btn btn-success" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <span className="spinner"></span>
              Đang thêm...
            </>
          ) : (
            <>
              <span>✓</span>
              Thêm sinh viên
            </>
          )}
        </button>

        {message && (
          <div className={`message ${message.includes('❌') ? 'message-error' : 'message-success'}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
}

function CourseDetailPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCourseDetails = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/courses/${courseId}`);
        setCourse(response.data);
      } catch (err) {
        console.error(err);
        navigate('/admin');
      }
      setLoading(false);
    };
    fetchCourseDetails();
  }, [courseId, navigate, refreshKey]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="course-detail-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Đang tải chi tiết lớp học...</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="course-detail-page">
        <div className="error-state">
          <p>Không tìm thấy lớp học.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="course-detail-page">
      {/* Header */}
      <div className="page-header">
        <Link to="/admin" className="back-button">
          ← Quay lại danh sách lớp
        </Link>
        <div className="course-title-section">
          <h1 className="course-title">{course.name}</h1>
          <span className="course-code-badge">{course.course_code}</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="content-grid">
        {/* Left Column */}
        <div className="left-column">
          <EnrollmentUploader
            courseId={course.id}
            courseName={course.name}
            onSuccess={handleRefresh}
          />

          <AddStudentForm
            courseId={course.id}
            onSuccess={handleRefresh}
          />
        </div>

        {/* Right Column */}
        <div className="right-column">
          <StudentList courseId={course.id} key={refreshKey} />

          {/* Danh sách các buổi học */}
          <div className="detail-card sessions-card">
            <div className="card-header">
              <h2>Các Buổi học của Lớp</h2>
              <span className="session-count">{course.schedules?.length || 0} buổi</span>
            </div>

            {!course.schedules || course.schedules.length === 0 ? (
              <div className="empty-state">
                <p>Chưa có buổi học nào được lên lịch.</p>
              </div>
            ) : (
              <div className="sessions-list">
                {course.schedules.map(schedule => (
                  <Link
                    key={schedule.id}
                    to={`/admin/session/${schedule.id}`}
                    className="session-item"
                  >
                    <div className="session-details">
                        <h3 className="session-date">
                          {new Date(schedule.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false })} -{' '}
                          {new Date(schedule.start_time).toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        </h3>
                      <p className="session-room"> Phòng: {schedule.room}</p>
                    </div>
                    <div className="session-arrow">→</div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetailPage;
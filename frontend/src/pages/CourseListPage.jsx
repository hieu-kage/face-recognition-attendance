import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './CourseListPage.css'; // Add this import

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function CourseListPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/courses`);
      setCourses(response.data || []);
    } catch (err) {
      setError('Không thể tải danh sách khóa học.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  if (loading) return <div className="loading">Đang tải...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Quản lý Lớp học</h1>
          <Link to="/" className="back-link">
            <i className="fas fa-arrow-left"></i> Trang Điểm danh
          </Link>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="action-bar">
          <Link to="/admin/courses/new" className="create-button">
            <i className="fas fa-plus"></i> Tạo Lớp học Mới
          </Link>
        </div>

        <div className="course-grid">
          {courses.map((course) => (
            <Link key={course.id} to={`/admin/course/${course.id}`} className="course-card">
              <div className="course-card-content">
                <h3 className="course-name">{course.name}</h3>
                <div className="course-code">{course.course_code}</div>
                <div className="course-sessions">
                  <i className="fas fa-calendar-alt"></i>
                  <span>{course.schedules?.length || 0} buổi học</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}

export default CourseListPage;
// src/pages/SessionDetailPage.jsx

import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './SessionDetailPage.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// --- Hàm trợ giúp ---
const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString('vi-VN', {
    dateStyle: 'full',
    timeStyle: 'short'
  });
};

const formatTime = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('vi-VN', {
    timeStyle: 'short'
  });
};

const getInitials = (name) => {
  if (!name) return '...';
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
};

const getStatusClass = (status) => {
  if (status === 'present') return 'status-present';
  if (status === 'late') return 'status-late';
  if (status === 'absent') return 'status-absent';
  if (status === 'upcoming') return 'status-upcoming'; // <-- CLASS MỚI
  return '';
};

function SessionDetailPage() {
  const { sessionId } = useParams();
  const [schedule, setSchedule] = useState(null);
  const [attendees, setAttendees] = useState([]);
  const [absentees, setAbsentees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    const fetchSessionDetails = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await axios.get(`${API_URL}/schedules/${sessionId}`);
        setSchedule(response.data.schedule);
        setAttendees(response.data.attendees || []);
        setAbsentees(response.data.absentees || []);
      } catch (err) {
        setError(err.response?.data?.detail || "Không tìm thấy buổi học");
      }
      setLoading(false);
    };
    fetchSessionDetails();
  }, [sessionId]);

  // --- Logic xác định trạng thái buổi học ---
  const sessionStatus = useMemo(() => {
    if (!schedule) return 'unknown';
    const now = new Date();
    const startTime = new Date(schedule.start_time);

    // Nếu hiện tại < giờ bắt đầu -> Buổi học chưa diễn ra
    if (now < startTime) return 'upcoming';
    return 'past'; // Đã qua hoặc đang diễn ra
  }, [schedule]);

  // --- Logic Thống kê ---
  const stats = useMemo(() => {
    const presentCount = attendees.filter(a => a.status === 'present').length;
    const lateCount = attendees.filter(a => a.status === 'late').length;
    const notCheckedInCount = absentees.length;
    const totalStudents = attendees.length + absentees.length;

    return { presentCount, lateCount, notCheckedInCount, totalStudents };
  }, [attendees, absentees]);

  // --- Logic Gộp & Lọc Danh sách ---
  const filteredList = useMemo(() => {
    // Quyết định trạng thái cho người chưa điểm danh: 'absent' hay 'upcoming'
    const notCheckedInStatus = sessionStatus === 'upcoming' ? 'upcoming' : 'absent';

    const formattedAbsentees = absentees.map(student => ({
        status: notCheckedInStatus, // Gán trạng thái dựa trên thời gian
        check_in_time: null,
        profile: student
    }));

    const fullList = [...attendees, ...formattedAbsentees];

    return fullList
      .filter(item => {
        if (filterStatus === 'all') return true;
        // Nếu lọc 'absent' thì cũng hiện 'upcoming' để admin dễ nhìn
        if (filterStatus === 'absent') return item.status === 'absent' || item.status === 'upcoming';
        return item.status === filterStatus;
      })
      .filter(item => {
        if (!searchText) return true;
        const searchLower = searchText.toLowerCase();
        return (
          item.profile?.name?.toLowerCase().includes(searchLower) ||
          item.profile?.student_id?.toLowerCase().includes(searchLower)
        );
      });
  }, [attendees, absentees, filterStatus, searchText, sessionStatus]);


  if (loading) return <div className="container">Đang tải chi tiết buổi học...</div>;
  if (error) return <div className="container" style={{ color: 'red' }}>{error}</div>;
  if (!schedule) return <div className="container">Không có dữ liệu.</div>;

  return (
    <div className="container">
      <header>
        <Link
          to={`/admin/course/${schedule.course_id}`}
          style={{ textDecoration: 'none', color: '#667eea', fontWeight: 600 }}
        >
          &larr; Quay lại Lớp học
        </Link>
        <h1>📋 Chi tiết Điểm danh</h1>
        <div className="date-info">
          Buổi học: {formatDate(schedule.start_time)} (Phòng: {schedule.room})
          {sessionStatus === 'upcoming' && <span style={{marginLeft: '10px', color: '#f59e0b', fontWeight: 'bold'}}>(Chưa diễn ra)</span>}
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card present">
          <h3>Có Mặt</h3>
          <div className="stat-number">{stats.presentCount}</div>
          <div>Sinh viên</div>
        </div>
        <div className="stat-card late">
          <h3>Đi Muộn</h3>
          <div className="stat-number">{stats.lateCount}</div>
          <div>Sinh viên</div>
        </div>

        {/* Đổi màu thẻ này tùy theo trạng thái */}
        <div className={`stat-card ${sessionStatus === 'upcoming' ? 'upcoming' : 'absent'}`}>
          <h3>{sessionStatus === 'upcoming' ? 'Chưa Điểm Danh' : 'Vắng Mặt'}</h3>
          <div className="stat-number">{stats.notCheckedInCount}</div>
          <div>Sinh viên</div>
        </div>

        <div className="stat-card total">
          <h3>Tổng Sĩ Số</h3>
          <div className="stat-number">{stats.totalStudents}</div>
          <div>Sinh viên</div>
        </div>
      </div>

      <div className="main-content">
        <div className="controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Tìm kiếm sinh viên..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </div>
          <div className="filter-buttons">
            <button
              className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
              onClick={() => setFilterStatus('all')}
            >
              Tất cả
            </button>
            <button
              className={`filter-btn ${filterStatus === 'present' ? 'active' : ''}`}
              onClick={() => setFilterStatus('present')}
            >
              Có mặt
            </button>
            <button
              className={`filter-btn ${filterStatus === 'late' ? 'active' : ''}`}
              onClick={() => setFilterStatus('late')}
            >
              Đi muộn
            </button>
            <button
              className={`filter-btn ${filterStatus === 'absent' ? 'active' : ''}`}
              onClick={() => setFilterStatus('absent')}
            >
              {/* Đổi tên nút lọc */}
              {sessionStatus === 'upcoming' ? 'Chưa đến' : 'Vắng mặt'}
            </button>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>STT</th>
              <th>Sinh Viên</th>
              <th>Giờ Vào</th>
              <th>Trạng Thái</th>
            </tr>
          </thead>
          <tbody>
            {filteredList.length === 0 ? (
              <tr>
                <td colSpan="4" style={{textAlign: 'center'}}>Không tìm thấy sinh viên nào.</td>
              </tr>
            ) : (
              filteredList.map((log, index) => (
                <tr key={log.profile?.student_id || index}>
                  <td>{index + 1}</td>
                  <td>
                    <div className="student-info">
                      <div className="avatar">
                        {getInitials(log.profile?.name)}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>
                          {log.profile?.name || '...'}
                        </div>
                        <div style={{ fontSize: '0.85em', color: '#666' }}>
                          MSSV: {log.profile?.student_id || '...'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td>{formatTime(log.check_in_time)}</td>
                  <td>
                    <span className={`status-badge ${getStatusClass(log.status)}`}>
                      {log.status === 'present' && 'Có mặt'}
                      {log.status === 'late' && 'Đi muộn'}
                      {log.status === 'absent' && 'Vắng mặt'}
                      {/* Hiển thị trạng thái mới */}
                      {log.status === 'upcoming' && 'Chưa bắt đầu'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default SessionDetailPage;
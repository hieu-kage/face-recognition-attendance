// src/pages/CreateCoursePage.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './CreateCoursePage.css';
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function CreateCoursePage() {
  // 1. Dùng useNavigate để chuyển trang sau khi tạo thành công
  const navigate = useNavigate();

  // 2. Toàn bộ state và logic của form cũ được chuyển vào đây
  const [formData, setFormData] = useState({
    name: '',
    course_code: '',
    lecturer_id: '',
    template_start_time: '',
    template_end_time: '',
    number_of_sessions: 15,
    template_room: ''
  });
  const [lecturers, setLecturers] = useState([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAddLecturer, setShowAddLecturer] = useState(false);
  const [newLecturer, setNewLecturer] = useState({ name: '', email: '' });
  const [addingLecturer, setAddingLecturer] = useState(false);

  // 🔹 Tải danh sách giảng viên
  const fetchLecturers = async () => {
    try {
      const res = await axios.get(`${API_URL}/lecturers`);
      setLecturers(res.data || []);
    } catch (err) {
      console.error("Không thể tải danh sách giảng viên:", err);
    }
  };

  useEffect(() => {
    fetchLecturers();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddLecturerChange = (e) => {
    const { name, value } = e.target;
    setNewLecturer(prev => ({ ...prev, [name]: value }));
  };

  const handleAddLecturer = async (e) => {
    e.preventDefault();
    setAddingLecturer(true);
    try {
      const res = await axios.post(`${API_URL}/lecturers`, newLecturer);
      const created = res.data;
      await fetchLecturers();
      setFormData(prev => ({ ...prev, lecturer_id: created.id.toString() }));
      setNewLecturer({ name: '', email: '' });
      setShowAddLecturer(false);
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi thêm giảng viên');
    }
    setAddingLecturer(false);
  };

  // 🔹 Xử lý submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.lecturer_id) {
        setMessage('❌ Vui lòng chọn giảng viên');
        return;
    }
    setIsLoading(true);
    setMessage('');

    const payload = {
      ...formData,
      lecturer_id: parseInt(formData.lecturer_id),
      number_of_sessions: parseInt(formData.number_of_sessions),
      template_start_time: new Date(formData.template_start_time).toISOString(),
      template_end_time: new Date(formData.template_end_time).toISOString(),
    };

    try {
      // 3. Gọi API tạo lớp
      const response = await axios.post(`${API_URL}/courses`, payload);
      const newCourse = response.data;
      setMessage('✅ Tạo lớp học thành công! Đang chuyển hướng...');

      // 4. TỰ ĐỘNG CHUYỂN TRANG (như bạn yêu cầu)
      navigate(`/admin/course/${newCourse.id}`);

    } catch (err) {
      setMessage(err.response?.data?.detail || '❌ Lỗi khi tạo lớp học');
      setIsLoading(false); // Chỉ dừng loading nếu có lỗi
    }
  };

  // 3. JSX của trang
  return (
    <div className="admin-dashboard">
  <Link to="/admin" className="back-link">
    <i className="fas fa-arrow-left"></i> Quay lại danh sách lớp
  </Link>

  <div className="admin-card">
    <h2>Tạo Lớp học Mới</h2>
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Tên Lớp học</label>
        <input name="name" placeholder="VD: Công nghệ Web" value={formData.name} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Mã Lớp học</label>
        <input name="course_code" placeholder="VD: IT4409" value={formData.course_code} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Phòng học</label>
        <input name="template_room" placeholder="VD: D9-301" value={formData.template_room} onChange={handleChange} />
      </div>

      <div className="form-group">
        <label>Số buổi học</label>
        <input name="number_of_sessions" type="number" placeholder="VD: 15" value={formData.number_of_sessions} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Giảng viên phụ trách</label>
        <div className="lecturer-select-group">
          <select name="lecturer_id" value={formData.lecturer_id} onChange={handleChange} required>
            <option value="">-- Chọn giảng viên --</option>
            {lecturers.map((lecturer) => (
              <option key={lecturer.id} value={lecturer.id}>{lecturer.name}</option>
            ))}
          </select>
          <button type="button" className="add-lecturer-btn" onClick={() => setShowAddLecturer(prev => !prev)}>
            {showAddLecturer ? 'Hủy' : '+ Thêm'}
          </button>
        </div>
      </div>

      {showAddLecturer && (
        <div className="add-lecturer-box">
          <div className="form-group">
            <label>Tên giảng viên</label>
            <input name="name" placeholder="Nhập tên giảng viên" value={newLecturer.name} onChange={handleAddLecturerChange} required />
          </div>
          <div className="form-group">
            <label>Email giảng viên</label>
            <input name="email" type="email" placeholder="Nhập email giảng viên" value={newLecturer.email} onChange={handleAddLecturerChange} required />
          </div>
          <button type="button" className="submit-btn" onClick={handleAddLecturer} disabled={addingLecturer}>
            {addingLecturer ? 'Đang thêm...' : 'Lưu giảng viên'}
          </button>
        </div>
      )}

      <div className="form-group">
        <label>Thời gian bắt đầu buổi học đầu tiên</label>
        <input name="template_start_time" type="datetime-local" value={formData.template_start_time} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Thời gian kết thúc buổi học đầu tiên</label>
        <input name="template_end_time" type="datetime-local" value={formData.template_end_time} onChange={handleChange} required />
      </div>

      <button type="submit" className="submit-btn" disabled={isLoading}>
        {isLoading ? 'Đang tạo...' : 'Tạo Lớp'}
      </button>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </form>
  </div>
</div>
  );
}

export default CreateCoursePage;
import React, { useState, useRef, useEffect } from 'react'; // Import thêm useEffect
import Webcam from 'react-webcam';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './CheckinPage.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function CheckinPage() {
  const [message, setMessage] = useState('Sẵn sàng điểm danh!');
  const [isLoading, setIsLoading] = useState(false);

  // State cho phần Enroll
  const [studentId, setStudentId] = useState('');

  // State cho phần Checkin
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');

  const webcamRef = useRef(null);


  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get(`${API_URL}/courses`);
        setCourses(response.data);

        if (response.data && response.data.length > 0) {
          setSelectedCourseId(response.data[0].id);
        }
      } catch (error) {
        console.error("Lỗi lấy danh sách môn học:", error);
        setMessage("Không tải được danh sách môn học.");
      }
    };

    fetchCourses();
  }, []);

  // --- XỬ LÝ ĐĂNG KÝ (ENROLL) ---
  const handleEnroll = async () => {
    if (isLoading) return;

    // Yêu cầu: Chỉ cần nhập MSSV
    if (!studentId) {
      setMessage('Vui lòng nhập MSSV');
      return;
    }

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) {
      setMessage('Không thể chụp ảnh. Vui lòng thử lại.');
      return;
    }

    setMessage('Đang xử lý đăng ký...');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/face_embedding/enroll`, {
        studentId: studentId,
        // Backend thường vẫn cần trường name, ta gán tạm bằng studentId
        name: studentId,
        image_base64: imageSrc,
      });
      setMessage(`Đăng ký thành công MSSV: ${studentId}`);
      setStudentId('');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Lỗi khi đăng ký');
    }
    setIsLoading(false);
  };

  // --- XỬ LÝ ĐIỂM DANH (CHECKIN) ---
  const handleCheckin = async () => {
    if (isLoading) return;

    if (!selectedCourseId) {
        setMessage('Vui lòng chọn môn học/buổi học');
        return;
    }

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) {
      setMessage('Không thể chụp ảnh. Vui lòng thử lại.');
      return;
    }

    setMessage('Đang gửi ảnh điểm danh...');
    setIsLoading(true);

    try {
      // Lưu ý: Backend API search-face đang nhận 'schedule_id'.
      // Ở đây ta truyền ID của Course vào (giả định course_id tương đương schedule_id hoặc bạn cần sửa lại backend để nhận course_id)
      const response = await axios.post(`${API_URL}/face_embedding/search-face`, {
        course_id: parseInt(selectedCourseId),
        image_base64: imageSrc,
      });
      setMessage(`Chào mừng, ${response.data.name}!`);
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || 'Lỗi khi điểm danh');
    }
    setIsLoading(false);
  };

  return (
    <div className="App-header">
      <h1>Hệ thống Điểm danh Khuôn mặt</h1>
      <div className="message">{message}</div>
      <nav style={{ margin: '10px' }}>
        <Link to="/admin" style={{ color: '#61dafb' }}>
          Xem Dashboard Admin
        </Link>
      </nav>

      <div className="webcam-container">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={720}
          height={480}
          videoConstraints={{ width: 720, height: 480, facingMode: 'user' }}
        />
      </div>

      <div className="controls-container">
        {/* Khu vực Đăng ký: Đã bỏ input Name */}
        <div className="control-card enroll-card">
          <h2>Đăng ký Mới</h2>
          <input
            type="text"
            placeholder="Nhập MSSV"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            disabled={isLoading}
          />
          <button onClick={handleEnroll} disabled={isLoading}>
            {isLoading ? 'Đang xử lý...' : 'Đăng ký (Chỉ cần MSSV)'}
          </button>
        </div>

        {/* Khu vực Điểm danh: Đã thay Input bằng Select */}
        <div className="control-card checkin-card">
          <h2>Điểm danh</h2>
          <p>Chọn môn học và bấm nút</p>

          <select
            className="course-select"
            value={selectedCourseId}
            onChange={(e) => setSelectedCourseId(e.target.value)}
            disabled={isLoading}
            style={{ padding: '10px', margin: '10px 0', width: '90%' }}
          >
            {courses.length === 0 && <option value="">Đang tải danh sách...</option>}
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                 {course.name} (Mã: {course.course_code || course.id})
              </option>
            ))}
          </select>

          <button onClick={handleCheckin} disabled={isLoading}>
            {isLoading ? 'Đang gửi...' : 'Bắt đầu Điểm danh'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CheckinPage;
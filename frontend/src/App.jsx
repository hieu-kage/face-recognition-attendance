// App.jsx (Đã cập nhật)

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CheckinPage from './pages/CheckinPage.jsx';
import CourseListPage from './pages/CourseListPage.jsx';
import CreateCoursePage from "./pages/CreateCoursePage.jsx";
import './App.css';

import CourseDetailPage from './pages/CourseDetailPage.jsx';
import SessionDetailPage from './pages/SessionDetailPage.jsx';

function App() {
  return (
    <Routes>
      <Route path="/" element={<CheckinPage />} />
      <Route path="/admin" element={<CourseListPage />} />
      <Route path="/admin/courses/new" element={<CreateCoursePage />} />

      <Route path="/admin/course/:courseId" element={<CourseDetailPage />} />
      <Route path="/admin/session/:sessionId" element={<SessionDetailPage />} />
    </Routes>
  );
}

export default App;
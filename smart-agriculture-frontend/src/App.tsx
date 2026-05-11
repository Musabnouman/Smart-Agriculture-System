import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import DetectPage from "./pages/DetectPage";
import IrrigationPage from "./pages/IrrigationPage";
import AboutPage from "./pages/AboutPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/detect" element={<DetectPage />} />
        <Route path="/irrigation" element={<IrrigationPage />} />
      </Routes>
    </Router>
  );
}

export default App;

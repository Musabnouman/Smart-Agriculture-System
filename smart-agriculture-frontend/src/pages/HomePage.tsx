import { Leaf, Droplets, TreesIcon as Plant } from "lucide-react";
import { useNavigate } from "react-router-dom";

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-[100vh] flex flex-col">
      <header className="px-4 lg:px-6 h-14 flex items-center border-b">
        <div className="flex items-center gap-2 font-semibold">
          <Leaf className="h-6 w-6 text-green-600" />
          <span>SmartFarm</span>
        </div>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <span onClick={() => navigate('/')} className="text-sm font-medium text-black hover:underline underline-offset-4">
            Home
          </span>
          <span onClick={() => navigate('/about')}className="text-sm font-medium text-black hover:underline underline-offset-4 cursor-pointer">About</span>
        </nav>
      </header>

      <main className="flex-1 bg-[url('/homebg.jpeg')] bg-cover bg-center bg-fixed relative">
        <div className="absolute inset-0 bg-black/50"></div>
        <section className="w-full py-12 md:py-24 lg:py-32 h-full relative z-10">
          <div className="container px-4 md:px-6 h-full flex flex-col justify-center">
            <div className="flex flex-col items-center justify-center space-y-4 text-center text-white">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Smart Agriculture Solutions
                </h1>
                <p className="mx-auto max-w-[700px] md:text-xl">
                  Advanced tools for modern farming. Detect plant diseases and optimize irrigation and fertilization with our AI-powered system.
                </p>
              </div>
              <div className="mx-auto w-full max-w-sm space-y-2">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <button
                    onClick={() => navigate("/detect")}
                    className="inline-flex h-12 items-center justify-center rounded-lg bg-gradient-to-r from-green-500 to-green-700 px-5 text-sm font-semibold text-white shadow-md transition-transform transform hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-green-600"
                  >
                    <Plant className="mr-3 h-5 w-5" />
                    Disease Detection
                  </button>
                  <button
                    onClick={() => navigate("/irrigation")}
                    className="inline-flex h-12 items-center justify-center rounded-lg bg-gradient-to-r from-blue-500 to-blue-700 px-5 text-sm font-semibold text-white shadow-md transition-transform transform hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <Droplets className="mr-3 h-5 w-5" />
                    Irrigation and Fertilization Advisor
                  </button>
                </div>

              </div>
            </div>
          </div>
        </section>
      </main>

    
    </div>
  );
};

export default HomePage;

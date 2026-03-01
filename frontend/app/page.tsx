import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import SearchSection from "@/components/SearchSection";
import UploadSection from "@/components/UploadSection";
import UpdatesSection from "@/components/UpdatesSection";

export default function Home() {
  return (
    <div className="relative min-h-screen pb-10">
      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12 space-y-10">
        <HeroSection />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <SearchSection />
          <UploadSection />
        </div>

        <UpdatesSection />
      </main>
    </div>
  );
}
import Image from 'next/image';
import { ImageItem } from '@/app/tune/types/index';

type ImageGridProps = {
  images: ImageItem[];
  isLoading: boolean;
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export default function ImageGrid({ images, isLoading, selectedId, onSelect }: ImageGridProps) {
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[300px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-slate-200 border-t-accent1 rounded-full animate-spin"></div>
          <p className="text-slate-500 tracking-wide text-sm font-medium">Scanning documents for figures...</p>
        </div>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[300px] border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50">
        <Image src="/icons/sparkles.svg" alt="Empty" width={32} height={32} className="opacity-20 mb-3 grayscale" />
        <p className="text-slate-600 text-sm px-4 text-center font-medium">No figures found matching the selected filters.</p>
        <p className="text-slate-400 text-xs mt-1">Try adjusting your filters or upload a custom image.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {images.map((img) => (
          <div
            key={img.azure_url}
            onClick={() => onSelect(img.azure_url)}
            className={`cursor-pointer rounded-xl overflow-hidden transition-all duration-300 relative group aspect-square ${selectedId === img.azure_url
              ? "ring-4 ring-accent1 ring-offset-2 ring-offset-white shadow-md scale-95"
              : "border border-slate-200 hover:border-accent1/50 hover:shadow-md"
              }`}
          >
            <div className="absolute inset-0 bg-slate-100 animate-pulse -z-10"></div>
            <img
              src={img.src}
              alt={img.title}
              className={`w-full h-full object-cover transition-transform duration-500 ${selectedId === img.azure_url ? 'scale-105' : 'group-hover:scale-110'}`}
              loading="lazy"
            />
            {selectedId === img.azure_url && (
              <div className="absolute top-2 right-2 bg-accent1 text-white rounded-full p-1 shadow-sm z-10 animate-fadeIn">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}

            <div className={`absolute bottom-0 left-0 right-0 p-2 text-xs truncate transition-opacity duration-300 ${selectedId === img.azure_url ? 'opacity-100 bg-gradient-to-t from-black/80 to-transparent text-white' : 'opacity-0 group-hover:opacity-100 bg-gradient-to-t from-black/80 to-transparent text-gray-200'}`}>
              {img.speciality}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
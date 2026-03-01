'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { ImageItem } from '@/app/tune/types/index';
import { useImageUpload } from '@/app/tune/hooks/useImageUpload';
import { useImageFilters } from '@/app/tune/hooks/useImageFilters';
import FilterDropdown from '@/app/tune/components/FilterDropdown';
import ImageGrid from '@/app/tune/components/ImageGrid';

type ImagesStepProps = {
  allImages: ImageItem[];
  isLoadingImages: boolean;
  selectedImageId: string | null;
  setSelectedImageId: React.Dispatch<React.SetStateAction<string | null>>;
  onNext: () => void;
};

export default function ImagesStep({
  allImages,
  isLoadingImages,
  selectedImageId,
  setSelectedImageId,
  onNext,
}: ImagesStepProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [images, setImages] = useState<ImageItem[]>(allImages);

  const { isUploading, uploadImages } = useImageUpload();
  const filters = useImageFilters(images);

  useEffect(() => {
    setImages(allImages);
  }, [allImages]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newImages = await uploadImages(e.target.files);
    if (newImages) {
      setImages((prev) => [...newImages, ...prev]);
      setSelectedImageId(newImages[0]?.azure_url ?? null);
    }
  };

  const handleNext = () => {
    onNext();
  };

  return (
    <div className="flex-1 flex flex-col h-full animate-fadeIn min-h-[500px]">
      <div className="bg-slate-50 rounded-xl p-8 border border-slate-200 mb-6 flex-1 flex flex-col">
        <h2 className="text-xl text-slate-800 font-semibold mb-6">Related Medical Figures</h2>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div className="flex gap-4">
            <FilterDropdown
              label="Speciality"
              options={filters.specialityOptions}
              value={filters.selectedSpeciality}
              onChange={filters.setSelectedSpeciality}
            />
            <FilterDropdown
              label="Disease Area"
              options={filters.diseaseOptions}
              value={filters.selectedDisease}
              onChange={filters.setSelectedDisease}
            />
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto mt-4 md:mt-0">
            <input
              type="file"
              accept=".jpg,.jpeg,.png"
              className="hidden"
              id="upload-image"
              onChange={handleUpload}
              disabled={isUploading}
            />
            <label
              htmlFor="upload-image"
              className={`flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors border shadow-sm ${isUploading
                ? "bg-slate-100 text-slate-400 border-slate-200 cursor-wait"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-accent1 cursor-pointer"
                }`}
            >
              {isUploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Image src="/icons/upload-file.svg" alt="Upload" width={16} height={16} className="opacity-70" />
                  Upload Image
                </>
              )}
            </label>
          </div>
        </div>

        <ImageGrid
          images={filters.filteredImages}
          isLoading={isLoadingImages}
          selectedId={selectedImageId}
          onSelect={setSelectedImageId}
        />
      </div>

      <div className="flex justify-between items-center mt-4 px-2">
        <button
          onClick={handleNext}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-accent1 transition-colors cursor-pointer"
        >
          Skip this step
        </button>

        <div className="flex gap-4">
          <button
            onClick={handleNext}
            className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-8 py-2.5 rounded-xl text-sm font-medium hover:bg-slate-50 hover:text-accent1 transition-colors shadow-sm cursor-pointer"
          >
            Skip Image Selection
          </button>
          <button
            onClick={handleNext}
            disabled={!selectedImageId}
            className="btn-gradient px-12 py-3 rounded-xl text-sm font-semibold tracking-wide transition-all shadow-md disabled:opacity-50 disabled:shadow-none hover:shadow-lg cursor-pointer disabled:cursor-not-allowed text-white"
          >
            <span className="flex items-center gap-2">Proceed <Image src="/icons/arrow-right-white.svg" alt="" width={16} height={16} className="invert brightness-0" /></span>
          </button>
        </div>
      </div>
    </div>
  );
}

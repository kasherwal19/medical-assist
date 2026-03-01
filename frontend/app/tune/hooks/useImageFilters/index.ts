import { useState, useMemo } from 'react';
import { ImageItem } from '@/app/tune/types/index';

export const useImageFilters = (images: ImageItem[]) => {
  const [selectedSpeciality, setSelectedSpeciality] = useState<string | null>(null);
  const [selectedDisease, setSelectedDisease] = useState<string | null>(null);

  const specialityOptions = useMemo(() => {
    return Array.from(new Set(images.map((img) => img.speciality)));
  }, [images]);

  const diseaseOptions = useMemo(() => {
    return Array.from(new Set(images.flatMap((img) => img.disease_area)));
  }, [images]);

  const filteredImages = useMemo(() => {
    let result = images;
    if (selectedSpeciality) {
      result = result.filter(
        (img) => img.speciality.toLowerCase() === selectedSpeciality.toLowerCase()
      );
    }
    if (selectedDisease) {
      result = result.filter((img) => img.disease_area.includes(selectedDisease));
    }
    return result;
  }, [images, selectedSpeciality, selectedDisease]);

  return {
    selectedSpeciality,
    setSelectedSpeciality,
    selectedDisease,
    setSelectedDisease,
    specialityOptions,
    diseaseOptions,
    filteredImages,
  };
};